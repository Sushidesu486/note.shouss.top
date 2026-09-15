# 06 · 架构对照与自测

<p class="reading-meta">把概念变成能画出来、算出来、在源码里找到的知识。</p>

## 1. 三种基础架构，先记住这张表

| 比较维度 | HunyuanVideo 初版 13B T2V | Wan 2.1 T2V | MiniMax-H3 Base |
| --- | --- | --- | --- |
| 本章比较的生成目标 | 视频 | 视频 | 视频 + 立体声音频 |
| 主要条件编码 | MLLM 序列 + CLIP pooled 向量 | umT5-XXL 文本序列 | H3-Encoder（Qwen3-VL-32B），参考视觉/音频另有 VAE |
| 文本进入主干的方式 | joint attention | cross-attention | packed 多模态 self-attention |
| 主干组织 | 20 双流 + 40 单流 | 视频 self-attention → 文本 cross-attention → FFN | 50 层单流，共享 attention/FFN，模态专属 AdaLN |
| 视频 VAE stride $(t,h,w)$ | $(4,8,8)$ | $(4,8,8)$ | $(4,16,16)$ |
| 视频 latent channels | 16 | 16 | 24 |
| 视频 patch $(t,h,w)$ | $(1,2,2)$ | $(1,2,2)$ | $(1,2,2)$ |
| 视频 token 有效空间步幅 | 16 | 16 | 32 |
| 本文的速度预测依据 | 论文 Flow Matching 目标 | 论文 Flow Matching 目标 | 公开推理代码 RF velocity 路径；完整 loss 未确认 |

表的依据分别是 [HunyuanVideo §4][hy]、[Wan §4][wan]与 [H3 官方发布配置][h3] / [SGLang scheduler][h3sched]。只比较列出的主模型，不对整个家族的全部音频、I2V 或后续产品下结论。HunyuanVideo 与 Wan 的技术报告也讨论了其他音频相关扩展，那与此处选定的基础 T2V 主干不是同一比较对象。

一句话复述可以是：**HunyuanVideo 分阶段融合图文，Wan 2.1 让视频主序列读取外部文本，H3 则将音视频与条件组织成共享主干里的多模态序列。** 这描述信息流，不是画质排名。

## 2. Wan 2.2 要单独分成两行

| 模型 | 专家结构 | 视频 VAE stride | 要记住的变化 |
| --- | --- | --- | --- |
| Wan 2.2 T2V-A14B / I2V-A14B | 高/低噪声两个专家，按时刻切换 | $(4,8,8)$ | 总参数约 27B，每步激活约 14B |
| Wan 2.2 TI2V-5B | dense 单模型 | $(4,16,16)$ | 更高压缩；统一文本/图像条件生成 |

依据：[Wan 2.2 官方说明][wan22]、[T2V-A14B 配置][a14]、[TI2V-5B 配置][ti5]。同一个家族的新版本里，也可能同时存在不同主干和 VAE 组合。

## 3. 从四个层次定位一个术语

| 层次 | 回答的问题 | 术语 |
| --- | --- | --- |
| 表示 | 视频/音频用什么数值空间表示？ | VAE、latent、压缩、patchify |
| 网络 | 一次预测怎样处理这些数？ | Transformer、DiT、attention、FFN、AdaLN |
| 生成过程 | 学什么目标、怎样生成样本？ | Diffusion、Flow Matching、噪声预测、速度预测、ODE |
| 执行 | 如何把计算跑得快、放得下？ | FlashAttention、并行、量化、offload、cache |

这是一种用于阅读论文的分类方法。例如“用了 FlashAttention，所以不是 diffusion”把执行层与生成过程混到了一起；“用了 VAE，所以不是 Transformer”则把表示层与网络层混到了一起。[概念依据：LDM][ldm]、[DiT][dit]、[FlashAttention][flash]

## 4. 术语速查

| 术语 | 简明含义 | 常见误解 |
| --- | --- | --- |
| latent | 编码器学习出的数值表示 | 等同于低分辨率 RGB |
| token | 网络序列中的一个位置及其向量 | 必须是离散单词 |
| patchify | 把网格划成块并映射成向量序列 | 等同于 VAE 压缩 |
| timestep | 在本系列多数生成公式中指噪声时刻 | 等同于视频第几帧 |
| self-attention | 同一序列产生 Q/K/V | 只能看同一帧 |
| cross-attention | query 从外部条件读取 K/V | 条件一定也被更新 |
| joint attention | 多模态组成同一 attention 序列 | 参数必须全部共享 |
| AdaLN | 条件生成归一化后的调制参数 | 每种实现都一样 |
| CFG | 混合有/无条件预测以增强引导 | 数值越大一定越好 |
| causal | 当前计算不读取指定意义下的未来 | 整个系统一定逐帧生成 |
| MoE | 按规则选择专家参与计算 | 一定是每个 token 的 FFN top-k 路由 |
| KV cache | 复用 attention 的 key/value 表示 | 固定输入的深层 K/V 总是固定 |

定义和适用边界见[基础 01](diffusion_flow.md)、[基础 02](transformer_dit.md)、[基础 03](video_vae.md)、[H3 的 mask 讨论](minimax_h3.md#5-attention-mask-mask)。

## 5. 五个能暴露理解漏洞的问题

??? question "A · 同一个网络执行 50 层、采样 30 步，一共只经过 50 个 block 吗？"
    不是。若每步一次完整 forward，主序列会执行 $50\times30=1500$ 次 block 计算。常规双路 CFG 会增加预测分支成本；若用 distilled guidance 或其他优化，调用数又不同。先统计采样循环，再统计一次 forward 内的层数。

??? question "B · 17 帧、544×960 的视频，Hunyuan 初版有多少视觉 tokens？"
    VAE 时间长度是 $1+(17-1)/4=5$，空间为 $68\times120$，patch 后为 $34\times60$，最终 $N_v=5\times34\times60=10200$。同样对齐的有效网格若用空间 stride 32，则 $N_v=5\times17\times30=2550$。后者是网格计算，不自动保证某个 H3 请求接受该输出尺寸；更不包含其音频、文本和参考 tokens。

??? question "C · Hunyuan 双流阶段，图像 query 看得见文本 key 吗？"
    看得见。各自投影后将 Q/K/V 拼接做 joint attention。两种模态的参数分开，并不代表连接被隔离。要看具体 attention 输入与 mask，不能只看框图上分成两列。

??? question "D · Wan 的文本很短，为什么模型还是很吃算力？"
    因为视频 self-attention 仍有 $N_v^2$ 的连接量。文本 cross-attention 的 $N_vN_t$ 较小，但没有替代视频内部的长序列计算。还要考虑 FFN、线性投影、层数与采样步数。

??? question "E · H3 的参考图像不变，可以照搬语言模型 KV cache 吗？"
    不能直接照搬。固定的是外层输入 latent；在联合 attention 内，参考 token 的深层表示可以依赖不断变化的生成目标。必须证明某个被缓存张量对当前变化无依赖，或接受近似复用并衡量质量损失。输入编码缓存、AdaLN 预计算、深层 attention KV 缓存是三种不同问题。

答案由上述模型的结构和形状推导得到，未进行模型生成实验。性能或质量判断需要实际测量。

## 6. 一段最小采样伪代码

```python
# 教学伪代码：s=0 为噪声，s=1 为数据；省略 CFG、归一化与多模态细节。
condition = text_encoder(prompt)
z = gaussian_noise(latent_shape)
for s_now, s_next in schedule:
    velocity = dit(z, noise_time=s_now, condition=condition)
    z = z + (s_next - s_now) * velocity
video = vae_decoder(z)
```

请先在代码中标出四种角色：文本编码器、生成状态、速度预测网络、数值积分；最后单独找到 decoder。再去读真实 pipeline 时，不会被大量调度、并行与 dtype 转换掩盖主线。这里是基础 Flow Matching 的示意代码，不能直接代替任一模型的可运行 pipeline。[Flow Matching][fm]

## 7. 建议怎样完成第一轮学习

1. 先读 DDPM 的概率图和两段算法，能解释训练与采样为何不同。
2. 读 Transformer 的 Q/K/V 图，再读 DiT Figure 3，标出时间条件进入的位置。
3. 手算一次 VAE → patch → token 的形状，不带计算器先完成 17 帧的例子。
4. 并排看 HunyuanVideo Figure 8 与 Wan Figure 10，用颜色标出视频 Q 与文本 K/V。
5. 最后读 H3 官方图，为每个框标记“编码”“条件”“生成目标”“主干”或“解码”。

完成后再读[已有源码推导](hunyuan_video.md)和[自回归视频扩散推理效率](ar_video_diffusion_efficiency.md)。不必第一遍就把训练集构建、分布式系统与全部论文附录一起学完。

[hy]: https://arxiv.org/html/2412.03603v1#S4
[wan]: https://arxiv.org/html/2503.20314v1#S4
[h3]: https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/README.md
[h3sched]: https://github.com/sgl-project/sglang/blob/12771786f23190b1845db33366eba09cb5eacf41/python/sglang/multimodal_gen/runtime/models/schedulers/scheduling_minimax_h3_euler_ancestral.py
[wan22]: https://github.com/Wan-Video/Wan2.2
[a14]: https://github.com/Wan-Video/Wan2.2/blob/42bf4cfaa384bc21833865abc2f9e6c0e67233dc/wan/configs/wan_t2v_A14B.py
[ti5]: https://github.com/Wan-Video/Wan2.2/blob/42bf4cfaa384bc21833865abc2f9e6c0e67233dc/wan/configs/wan_ti2v_5B.py
[ldm]: https://arxiv.org/abs/2112.10752
[dit]: https://arxiv.org/abs/2212.09748
[fm]: https://arxiv.org/abs/2210.02747
[flash]: https://arxiv.org/abs/2205.14135
