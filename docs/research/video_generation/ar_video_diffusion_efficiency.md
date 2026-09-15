# 自回归视频扩散的推理效率：Dummy Forcing 与 FAST-AR

> 方向：长视频生成 / autoregressive video diffusion / KV cache 与稀疏 attention  
> 笔记版本：2026-07-24  
> 阅读版本：Dummy Forcing 为 arXiv v1（2026-01-28）；FAST-AR 为 arXiv v2（2026-06-12）。

这两篇论文研究的不是“如何从头训练一个更强的视频模型”，而是同一个更具体的问题：

> 一个已经训练好的自回归视频扩散模型，在持续生成更长视频时，如何减少 KV cache 和 attention 中没有必要的计算？

它们给出的答案可以先压缩成一句话：

$$
\boxed{
\text{Dummy Forcing：不同 attention head 不需要相同长度的历史}
}
$$

$$
\boxed{
\text{FAST-AR：不同 token 和 query-key 对也不需要被完整保留或计算}
}
$$

---

## 1. 共同背景：为什么自回归视频越生成越慢

自回归视频扩散把视频按帧或 chunk 分解：

$$
p(x_{1:T})=\prod_{i=1}^{T}p(x_i\mid x_{<i}).
$$

外层的第 $i$ 个 AR step 负责生成下一帧或下一段视频；在这个 step 内部，diffusion model 还要执行若干次去噪。历史帧被编码进 self-attention 的 KV cache，供当前帧查询。这里需要区分三个尺度：

- **AR step $i$**：现在生成到第几帧或第几个 chunk；
- **denoising step $\tau$**：当前 chunk 内部的扩散去噪进度；
- **attention layer / head**：每次去噪前向中真正执行上下文聚合的位置。

来源：[Dummy Forcing, Sec. 3][df-pdf]；[FAST-AR, Sec. 3][fast-pdf]。

若不限制历史长度，第 $i$ 步的 self-attention 可写为：

$$
O_i=\operatorname{softmax}\!\left(
\frac{Q_i[K_1,\ldots,K_i]^\top}{\sqrt d}
\right)[V_1,\ldots,V_i].
$$

随着 $i$ 增大，单步需要访问的 key/value 越来越多。若每帧有 $S$ 个视觉 token，则 KV 显存随视频长度近似按 $O(TSd)$ 增长，完整 rollout 中累计的 attention 配对数近似按 $O(T^2S^2)$ 增长。滑动窗口可以限制成本，却会丢掉窗口外的角色、场景和事件信息，削弱长程一致性。[FAST-AR, Sec. 1 与 Sec. 3][fast-pdf]

因此，两篇论文都在追问：

$$
\text{已经缓存的历史信息，真的在所有 head、所有 token、所有 attention 中都被使用了吗？}
$$

---

## 2. Efficient Autoregressive Video Diffusion with Dummy Head

论文：[arXiv:2601.20499v1][df-abs]；方法名为 **Dummy Forcing**。

### 2.1 这项研究做了什么

作者先分析预训练 autoregressive video diffusion 的多头 self-attention，发现不同 head 对历史的依赖差异很大：有些 head 负责读取第一帧，有些只关心最近帧，还有一批 head 几乎只看当前帧。既然这些 head 不使用历史，就没有必要为它们保存和读取完整 KV cache。

Dummy Forcing 因而把统一的历史窗口改成 **head-specific context**：

1. 用 **Heterogeneous Memory Allocation** 为不同 head 分配不同历史范围；
2. 用 **Dynamic Head Programming** 自动确定每个 head 属于哪一类；
3. 用 **context packing / Packed Attention Forward** 减少 kernel launch，并允许更激进地压缩历史；
4. 整个方法直接作用于预训练模型，不需要重新训练或微调。

来源：[Dummy Forcing 摘要、Sec. 1 与 Sec. 4][df-pdf]。

### 2.2 关键观察：历史上下文在 head 之间利用不均

作者把一个 head 的 attention map 记为 $\mathcal A\in\mathbb R^{HW\times(L+1)HW}$，再分别统计它分给 sink、neighbor 和 current 三组帧的 attention mass：

$$
\alpha_h^r
=\frac{1}{HW}\sum_{u=1}^{HW}
\sum_{v\in\mathcal J_r}\mathcal A^{(h)}_{uv},
\qquad
r\in\{\text{sink},\text{neighbor},\text{current}\}.
$$

其中 $\alpha_h^{\text{sink}}+\alpha_h^{\text{neighbor}}+\alpha_h^{\text{current}}=1$。[Dummy Forcing, Eq. (3)][df-pdf]

论文报告了三个核心现象：

- 约 **25%** 的 head 把超过 **80%** 的注意力放在当前帧，几乎不读取历史；作者称它们为 **dummy heads**。
- dummy head 的位置具有一定稳定性；改变 AR step 时，论文的 core-set 实验中有 **92%** 的 head index 重复出现。
- 固定删除 25% dummy heads 的历史 KV 后，Self Forcing 的总分从 84.00 变为 83.78，仅下降 0.26%；随机删同样比例则降到 79.30。

这说明冗余不是“所有 head 都少看一点历史”，而是具有明显的 **head-wise specialization**。[Dummy Forcing, Sec. 3.2 与 Table 1][df-pdf]

### 2.3 Heterogeneous Memory Allocation：按 head 类型分配历史

作者进一步把 head 分为三类：

| Head 类型 | 允许读取的内容 | 主要作用 |
| --- | --- | --- |
| sink head | sink frame + current frame | 读取全局锚点 |
| neighbor head | 最近 $L-1$ 帧 + current frame | 维持局部运动和连续性 |
| dummy head | current frame | 在当前帧内部提炼特征 |

对应的 attention 可以简写为：

$$
\begin{aligned}
\text{sink}:\quad
&\operatorname{Attn}(Q_i,[K_s,K_i],[V_s,V_i]),\\
\text{neighbor}:\quad
&\operatorname{Attn}(Q_i,K_{i-L+1:i},V_{i-L+1:i}),\\
\text{dummy}:\quad
&\operatorname{Attn}(Q_i,K_i,V_i).
\end{aligned}
$$

核心不是直接把所有历史统一截短，而是把有限的 cache 预算留给真正需要历史的 head。[Dummy Forcing, Eq. (4) 与 Sec. 4.1][df-pdf]

### 2.4 Dynamic Head Programming：如何自动分类

对第 $h$ 个 head，定义

$$
\mathcal F_h=
[\alpha_h^{\text{sink}},
\alpha_h^{\text{neighbor}},
\alpha_h^{\text{current}}].
$$

若指定恰好有 $N$ 个 dummy heads，作者把分类写成保留 attention mass 的优化问题：

$$
\max_{c_1,\ldots,c_H}
\sum_{h=1}^{H}f_h(c_h),
\qquad
\text{s.t. }
\sum_{h=1}^{H}\mathbf 1[c_h=\text{dummy}]=N,
$$

其中

$$
f_h(c_h)=
\begin{cases}
\mathcal F_{h,0}+\mathcal F_{h,2},&c_h=\text{sink},\\
\mathcal F_{h,1}+\mathcal F_{h,2},&c_h=\text{neighbor},\\
\mathcal F_{h,2},&c_h=\text{dummy}.
\end{cases}
$$

把一个 head 强制设为 dummy 的机会成本是

$$
\ell_h=\max(\mathcal F_{h,0},\mathcal F_{h,1}).
$$

因此最优分类可以用简单的 greedy procedure 得到：

```text
计算每个 head 的 frame attention score F_h
计算机会成本 ell_h = max(F_sink, F_neighbor)
把 ell_h 最小的 N 个 head 设为 dummy
其余 head：F_sink >= F_neighbor 则为 sink，否则为 neighbor
```

论文附录证明了这个 greedy 解对上述目标是最优的，复杂度主要来自排序，为 $O(H\log H)$。[Dummy Forcing, Sec. 4.2 与 Appendix A][df-src]

一个容易误解的细节是：论文实现并不是每个 AR step 都重新分类。作者抽样 25% query token 估计 attention map，在第三个 AR step、最后一个 denoising step 完成一次分类，之后固定复用；论文报告估计本身低于 10 ms，单次分类在 100 ms 内完成。[Dummy Forcing, Appendix D][df-src]

### 2.5 Context packing：为什么给 dummy head 加回一帧

若强行增加 dummy head 数量，部分处在分类边界上的 context-critical heads 会被误删，质量开始下降。作者因此让 packed dummy head 同时读取前一帧和当前帧：

$$
\text{pack-dummy}:
\operatorname{Attn}
(Q_i,[K_{i-1},K_i],[V_{i-1},V_i]).
$$

这看似多保留了一帧，却带来两个收益：

1. 给分类边界附近的 head 留下最必要的短期上下文；
2. packed dummy 与 sink head 的 context 长度都为两帧，可以合并执行，把三次 attention kernel call 减少为两次。

因此，方法可以把超过 50% 的 head 配成 dummy，同时没有明显的质量崩溃。[Dummy Forcing, Sec. 4.3][df-pdf]

### 2.6 实验结论：速度提升来自哪里

下表只摘录理解研究结论所需的代表性结果；速度均来自论文在单张 H100 上的报告。[Dummy Forcing, Tables 2–5][df-pdf]

| 场景 | Baseline | Dummy Forcing | 结论 |
| --- | --- | --- | --- |
| Self Forcing，5 s，832×480 | 17.56 FPS，VBench 84.00 | 24.30 FPS，83.90 | 1.4×，总分下降 0.10 |
| Self Forcing，30 s | 17.56 FPS，83.53 | 24.30 FPS，83.19 | 1.4×，总分下降 0.34 |
| LongLive，30 s | 17.57 FPS，82.74 | 24.30 FPS，82.57 | 1.4×，总分下降 0.17 |
| Self Forcing，720P | 5.6 FPS，84.20 | 9.1 FPS，84.14 | 1.6× |
| LongLive，1080P | 1.3 FPS，81.65 | 2.6 FPS，81.65 | 2.0×，报告总分不变 |

在长上下文实验中，LongLive 的滑动窗口 baseline 只缓存 36 帧，得到 17.57 FPS / 68.45 分；Dummy Forcing 把节省出的 cache 预算转给 neighbor heads，缓存 237 帧，仍达到 18.14 FPS / 69.48 分。与同样缓存 237 帧但不做压缩的 LongLive 相比，速度为 18.14 vs. 9.36 FPS，即 1.93×。[Dummy Forcing, Sec. 5.4 与 Table 5][df-pdf]

这篇论文最重要的结论不是“删掉 25% cache”，而是：

> KV cache 的最合理分配单位不一定是整个模型或整层，也可以细化到每个 attention head；省下来的预算既能换速度，也能换更长历史。

### 2.7 局限

- dummy head 的判断依赖对特定模型 attention 行为的 profiling；在新的架构、训练方式或数据分布上仍需重新验证。
- 方法给出的是 head 类型的经验规律，但尚未解释 dummy heads 为什么在训练中形成；作者把训练动态分析留作未来工作。
- 当前方案是 training-free。作者认为针对识别出的 dummy heads 做后训练可能进一步提高压缩率，但论文没有验证。
- 主要加速 self-attention；其收益会受到非 attention 模块占比、Triton 实现和具体序列长度影响。

来源：[Dummy Forcing, Appendix D、I 与 J][df-src]。

---

## 3. FAST-AR：Temporal Cache Compression 与 Sparse Attention

论文：[arXiv:2602.01801v2][fast-abs]；arXiv 记录为 ICML 2026 接收版本。

### 3.1 这项研究做了什么

FAST-AR 把分析粒度从“哪些 head 需要历史”继续推进到“历史中的哪些 token、哪些 query-key 配对和哪些 prompt token 真正有用”。作者识别三类长期存在的冗余，并分别设计一个组件：

| 冗余 | 组件 | 做法 |
| --- | --- | --- |
| 不同帧中存在近似重复的 cached keys | **TempCache** | 沿时间匹配并合并重复 KV |
| self-attention 的 Q/K 变化慢且具有语义聚类，很多配对权重很小 | **AnnSA** | 只在 ANN 找到的语义候选中计算 attention |
| 长 prompt 中每一帧只依赖少量文本 token | **AnnCA** | 为当前帧筛选相关 prompt token |

三个组件都是 training-free，可插入预训练 autoregressive video diffusion 或 world model。[FAST-AR 摘要、Sec. 1 与 Sec. 5][fast-pdf]

### 3.2 关键观察：三类冗余

作者在 Rolling-Forcing 上统计 dense attention：只保留约 30% 的最高 attention entries，仍可保留超过 85% 的 attention mass。这说明 autoregressive video diffusion 的 attention 本身具有明显稀疏性。[FAST-AR, Sec. 4][fast-pdf]

进一步的 PCA 与 cross-attention 可视化显示：

1. 相同物体或背景区域的 Q/K 在特征空间中形成语义簇；
2. 许多 key 会在相邻帧中近似重复；
3. 一帧通常只关注 prompt 中与当前内容有关的少量 token。

这三点分别对应 AnnSA、TempCache 和 AnnCA。[FAST-AR, Sec. 4][fast-pdf]

### 3.3 先把 attention 改写为 ANN 检索

Dense attention 对每个 query 都与全部 cached keys 做点积。FAST-AR 先用 approximate nearest neighbor 找到候选集合

$$
\mathcal N(q)\subseteq\{1,\ldots,|\hat K|\},
$$

再只在候选中计算：

$$
\operatorname{Attn}(q)
\approx
\operatorname{softmax}\!\left(
\frac{q\hat K_{\mathcal N(q)}^\top}{\sqrt d}
\right)
\hat V_{\mathcal N(q)}.
$$

论文使用两种轻量检索实现：

- **LSH**：把 Q/K 投影到共享的低维随机空间，并让 query 只搜索相同 hash bucket 中的 key；
- **Quantization**：把 Q/K 量化到低 bit 空间，在量化表示上完成近邻搜索。

候选选出后，再由 block-sparse kernel 执行 attention。论文实现使用 FAISS 做 ANN、FlashInfer 做 sparse attention。[FAST-AR, Sec. 5.1 与 Sec. 6.1][fast-pdf]

### 3.4 TempCache：沿时间合并重复 KV

对当前帧的 query，TempCache 用 ANN 找到过去 key 中的 top-1 匹配，把跨帧对应同一语义区域的 keys 分组，并为每组只保留最近的代表 key。[FAST-AR, Sec. 5.2][fast-pdf]

关键问题是：不能直接删掉重复 key。因为 softmax 中重复出现的次数也会影响归一化，而且每个重复 key 对应的 value 可能不同。论文给出一个精确合并引理。

假设组 $G_t$ 内所有 key 完全相同，组大小为 $m_t$，代表 key 为 $k'_t$，并定义平均 value：

$$
\tilde v_t=\frac{1}{m_t}\sum_{i\in G_t}v_i.
$$

那么原始 attention 与下面的分组 attention 完全相等：

$$
\operatorname{Attn}(q,K,V)
=
\sum_{t=1}^{g}
\frac{e^{\tilde s_t}}
{\sum_{u=1}^{g}e^{\tilde s_u}}
\tilde v_t,
\qquad
\tilde s_t=
\frac{q^\top k'_t}{\sqrt{d_k}}+\log m_t.
$$

因此，完全重复的 key 可以通过“保留一个代表 key、平均 value、在 logit 上加 $\log m_t$”实现无误差合并。[FAST-AR, Lemma 5.1 与 Appendix A][fast-src]

这里必须保留一个边界：真实视频特征通常只是 **近似重复**，不是完全相同。FAST-AR 在实践中用相似度阈值决定是否合并，所以实际 TempCache 是近似方法；引理只证明了 exact duplicate 的情形。没有检测到冗余时，方法退化回标准 attention。[FAST-AR, Sec. 5.2][fast-pdf]

### 3.5 AnnCA：每一帧只读取相关文本

AnnCA 把当前帧 latent queries 与 prompt keys 投影到同一个 LSH 或量化空间。如果一个 prompt token 的 bucket 中没有任何当前帧 query，它就不会参与这一帧的 cross-attention。

因此，它做的不是永久删掉 prompt 中的词，而是执行 **frame-adaptive prompt token selection**：角色出现时保留角色词，场景切换后再选择与新帧相关的词。[FAST-AR, Sec. 5.3][fast-pdf]

### 3.6 AnnSA：只计算语义相关的 self-attention

AnnSA 复用 ANN 得到的语义 bucket。每个 query 只与同 bucket 中的 keys 做 self-attention，而不是与全部历史 token 做全连接 attention：

```text
Q/K → LSH 或低比特量化 → 语义 bucket
对每个 query 找到候选 bucket
只取 bucket 内的历史 K/V
用 block-sparse kernel 计算 attention
```

这一步减少的是 query-key 边数；TempCache 减少的是缓存节点数。二者优化对象不同，因此可以组合。[FAST-AR, Sec. 5.4][fast-pdf]

### 3.7 实验结论：长 rollout 才是主战场

论文的长序列实验使用单张 H100，生成 3000 帧，且没有人为限制任何方法的 context window。稀疏 attention 在前 30% denoising steps 中关闭，并只用于作者观察到稀疏性的约 70% transformer blocks；量化默认使用 8 bit。[FAST-AR, Sec. 6.1][fast-pdf]

Rolling-Forcing / LongVBench 的代表性结果如下：[FAST-AR, Table 1][fast-pdf]

| 方法 | Density | Recall | VBench | 组件 / 端到端速度 |
| --- | ---: | ---: | ---: | ---: |
| Dense FA3 | 100% | 100% | 84.08 | 1.0× |
| TempCache-Quant | 16.2% | 91.4% | 84.19 | 6.9× / 3.2× |
| AnnSA-Quant | 28.0% | 92.6% | 83.29 | 5.2× / 2.8× |
| AnnCA-LSH | 33.1% | 94.2% | 83.23 | 2.2× / 1.2× |
| Full FAST-AR-Quant | — | — | 83.99 | 10.8× 端到端 |

在 3000 帧 rollout 图中，dense FA3 随 cache 增长持续掉速和增加显存，而 FAST-AR 的吞吐与峰值显存近似保持平坦。LongVie2 世界模型上，完整方法报告 6.3×–6.9× 速度；但 LongVGenBench 为 64.91 / 63.69，低于 dense FA3 的 69.67，因此“保持质量”仍要结合具体指标理解，不能只看速度摘要。[FAST-AR, Fig. 5；Supplementary Table 2][fast-src]

TempCache 在其他 AR 视频模型上也显示较强加速：MAGI-1 为 4.11×，SkyReels-V2 为 9.25×，后者 VBench 为 83.82%，接近 vanilla 的 83.84%。[FAST-AR, Supplementary Table 3][fast-src]

### 3.8 短视频上的反例：稀疏不一定更快

在 5 秒 HunyuanVideo 和 Wan2.1-14B 实验中，AnnSA 的质量与其他稀疏方法相当，但最低 latency 仍来自 STA + FlashAttention-3。论文给出的原因是：短序列上，稀疏 kernel 的索引、bucket 和调度开销较大，而且优化程度通常不如 FlashAttention；只有上下文足够长、dense attention 与 cache growth 成为主导瓶颈时，FAST-AR 的优势才明显。[FAST-AR, Supplementary Table 4 与 Sec. C][fast-src]

### 3.9 局限

- 精确合并引理只覆盖完全重复 key；近似 key 的合并误差由阈值控制，但论文没有给出通用误差上界。
- ANN、量化位宽、相似度阈值和 sparse density 都存在质量—速度折中。论文消融中，更激进的合并会显著降低 attention recall。
- 稀疏 kernel 有固定开销，短视频不一定优于高效 dense attention。
- 5×–10× 的主要结论来自单张 H100、指定模型和超参数；换硬件、kernel 或模型结构后需要重新寻找 break-even point。
- AnnCA 的收益与 prompt 长度和逐帧文本选择性有关；短 prompt 下 cross-attention 本身可能不是主瓶颈。

来源：[FAST-AR, Sec. 6 与 Supplementary Sec. C–D][fast-src]。

---

## 4. 两篇论文的关系

| 维度 | Dummy Forcing | FAST-AR |
| --- | --- | --- |
| 共同目标 | 对预训练 AR video diffusion 做 KV / attention 推理加速 | 同左，并扩展到 world model |
| 主要发现 | 历史上下文在 head 之间利用不均 | KV token、Q-K 配对和 prompt token 都有冗余 |
| 优化粒度 | **head × frame group** | **token / KV group / attention edge** |
| 核心组件 | HMA、DHP、context packing | TempCache、AnnSA、AnnCA |
| 如何选内容 | 一次 attention profiling 后分类 head | 每次通过 LSH 或量化 ANN 找候选 |
| 如何省显存 | 不同 head 缓存不同长度；也可把预算转成长 context | 合并跨帧近似重复 KV，使 cache 在长 rollout 中保持有界 |
| 如何省计算 | 缩短每个 head 的 K/V 长度并减少 kernel call | 缩短 cache，同时稀疏 SA 与 CA |
| 理论支撑 | 分类目标的 greedy 最优性 | 完全重复 key 的无误差合并引理 |
| 训练要求 | training-free | training-free |
| 最适合的场景 | head 分工明显；短/长视频和高分辨率均可获益 | 上下文很长、cache growth 成为主要瓶颈的 rollout |
| 主要风险 | 错分 context-critical head | ANN 漏检、近似合并误差、短序列 sparse overhead |

两者不是互斥方案。一个自然的组合是：

$$
\boxed{
\text{先用 Dummy Forcing 决定每个 head 需要哪类历史}
\rightarrow
\text{再对保留下来的历史使用 TempCache / AnnSA}
}
$$

例如 dummy heads 根本不需要执行历史 ANN；neighbor heads 可以在长时间窗口内使用 TempCache；sink heads 只保留少量全局 anchor。这个组合尚不是两篇论文已经验证的结论，而是可以继续研究的方向。

---

## 5. 可以形成的研究问题

1. **Head-level 与 token-level 压缩能否叠加？** 先做 head routing，再只在 neighbor heads 中运行 TempCache / AnnSA，ANN 开销是否会进一步下降？
2. **统一预算如何分配？** 给定总 KV budget，应该把多少预算分给 sink、neighbor、dummy heads，以及每类 head 内部保留多少 token？
3. **dummy head 为什么形成？** 它来自训练目标、因果 mask、网络深度，还是 diffusion timestep 的分工？
4. **近似 key 合并的误差能否被界定？** 能否把 $\|k_i-k_j\|$、query norm 与 attention output error 联系起来？
5. **长程一致性是否真的受益？** cache 更长不仅要看 VBench，还应测试角色离开后重新出现、场景回访和动作因果关系。
6. **短序列的 break-even point 在哪里？** 在不同 GPU、分辨率、帧数和 prompt 长度下，ANN/sparse kernel 从哪一刻开始快于 FA3？
7. **一次 head 分类是否足够？** 场景切换或 prompt 改变后，head 类型是否应重新规划？分类频率与质量、开销如何折中？

---

## 6. 建议的可复现实验

### 实验 A：先验证 FAST-AR 的精确合并引理

不需要视频模型，先构造小型 Q/K/V：

1. 人工复制若干完全相同的 keys，但令 values 不同；
2. 计算 dense attention；
3. 按组平均 values，并给 logit 加 $\log m_t$；
4. 检查两者最大误差是否接近浮点误差；
5. 再逐步给 duplicate keys 加噪声，绘制 key similarity 与 output error 曲线。

这是成本最低、最适合先复现的实验。

### 实验 B：复现 dummy-head profiling

在一个可运行的 AR video diffusion checkpoint 上：

1. 保存若干层/heads 的 attention map；
2. 计算 $\alpha^{\text{sink}}$、$\alpha^{\text{neighbor}}$、$\alpha^{\text{current}}$；
3. 画出各层 dummy head 比例；
4. 比较不同 prompt、AR step、denoising step 下 head index 的交集；
5. 分别做 random pruning 与 dummy-head pruning，比较质量和延迟。

### 实验 C：复现长 cache 的时间—显存曲线

先只对 attention module 做 microbenchmark：

```text
固定当前帧 query 数
逐渐增加缓存帧数：8, 16, 32, 64, 128, ...
比较 dense / per-head window / TempCache-like merge / ANN sparse
记录 latency、peak memory、density、recall 与 output error
```

重点不是立刻追求论文中的 10×，而是确认四条曲线分别在什么长度开始分离。

### 实验 D：组合两篇方法

设置四组：

1. dense baseline；
2. Dummy Forcing only；
3. TempCache / AnnSA only；
4. head routing + token compression。

固定同一模型、prompt、seed 和 context length，比较：

- 端到端 FPS 与单层 attention latency；
- KV cache peak memory；
- attention recall；
- 短视频质量与长 rollout 漂移；
- ANN 与 head classification 自身的额外开销。

如果组合组只减少理论 FLOPs，却没有降低 wall-clock time，问题大概率在 kernel launch、索引整理或稀疏度尚未超过硬件 break-even point。

---

## 7. 当前应记住的结论

1. 长视频的效率问题不只是 diffusion steps 多，还包括 **AR rollout 中不断增长的 attention context**。
2. KV cache 不应该被看作一整块同等重要的历史：它可以按 **head、帧、token 和语义配对**进一步拆分。
3. Dummy Forcing 证明了 head-wise 历史利用不均；FAST-AR 进一步利用时间重复和语义稀疏。
4. training-free 不代表没有假设：两篇方法都依赖预训练模型内部已经形成稳定的 attention 结构。
5. 稀疏方法的真实价值必须看端到端 wall-clock、峰值显存和长 rollout；只看 FLOPs 或短视频结果可能得出错误结论。

---

## 8. 一手来源

- Dummy Forcing：[arXiv v1 摘要][df-abs]、[PDF][df-pdf]、[TeX source][df-src]、[作者项目页][df-project]、[作者代码仓库][df-code]。
- FAST-AR：[arXiv v2 摘要][fast-abs]、[PDF][fast-pdf]、[TeX source][fast-src]、[作者项目页][fast-project]。
- 版本核对日期：2026-07-24。笔记中的实验数字均按上述 arXiv 版本的正文或补充材料记录。

## 延伸阅读与视频

- 先读[Diffusion Forcing](paper_reading.md#diffusion-forcing)与[Self Forcing](paper_reading.md#self-forcing)导读，区分噪声安排与训练历史来源。
- 配套观看[Boyuan Chen 的 Diffusion Forcing 作者报告](video_courses.md#diffusion-forcing)，再回本页讨论 cache 与端到端效率。

[df-abs]: https://arxiv.org/abs/2601.20499v1
[df-pdf]: https://arxiv.org/pdf/2601.20499v1
[df-src]: https://arxiv.org/src/2601.20499v1
[df-project]: https://csguoh.github.io/project/DummyForcing/
[df-code]: https://github.com/csguoh/DummyForcing
[fast-abs]: https://arxiv.org/abs/2602.01801v2
[fast-pdf]: https://arxiv.org/pdf/2602.01801v2
[fast-src]: https://arxiv.org/src/2602.01801v2
[fast-project]: https://dvirsamuel.github.io/fast-auto-regressive-video/
