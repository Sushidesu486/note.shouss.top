# 论文与图源

<p class="reading-meta">核对日期 2026-09-10 · 一手论文、官方仓库与可定位实现</p>

本页保存原始文献与图源；逐篇阅读重点见[论文导读](paper_reading.md)，配套录像见[视频课程](video_courses.md)。

## 视频建模与因果生成补充

新增导读核对日期：2026-09-13。

| 论文 | 本轮固定版本 | 导读 |
| --- | --- | --- |
| Video Diffusion Models | [2204.03458v2](https://arxiv.org/abs/2204.03458v2) | [时空建模](paper_reading.md#video-diffusion) |
| Stable Video Diffusion | [2311.15127v1](https://arxiv.org/abs/2311.15127v1) | [视频数据与训练](paper_reading.md#stable-video-diffusion) |
| Diffusion Forcing | [2407.01392v1](https://arxiv.org/abs/2407.01392v1) | [各 token 的噪声水平](paper_reading.md#diffusion-forcing) |
| Self Forcing | [2506.08009v1](https://arxiv.org/abs/2506.08009v1) | [自生成历史](paper_reading.md#self-forcing) |

## 基础论文

| 论文 | 在本系列中解决的问题 | 首读位置 |
| --- | --- | --- |
| [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) · Kingma & Welling | VAE、ELBO、重参数化 | §2、Appendix B |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) · Vaswani et al. | Transformer、Q/K/V、多头注意力 | Figure 1–2、§3 |
| [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) · Ho et al. | 加噪、噪声预测、反向采样 | Figure 2、Algorithm 1–2、§2–3 |
| [Denoising Diffusion Implicit Models](https://arxiv.org/abs/2010.02502) · Song et al. | DDIM 与更少时刻的采样 | §3–4 |
| [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) · Rombach et al. | 为什么在潜空间生成 | Figure 3、§3 |
| [Scalable Diffusion Models with Transformers](https://arxiv.org/abs/2212.09748) · Peebles & Xie | DiT 与 adaLN-Zero | Figure 3、§3 |
| [Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747) · Lipman et al. | 条件速度场、ODE、概率路径 | §3 |
| [Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow](https://arxiv.org/abs/2209.03003) · Liu et al. | Rectified Flow 与线性路径 | §2 |
| [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) · Ho & Salimans | 条件引导 | §3 |
| [RoFormer](https://arxiv.org/abs/2104.09864) · Su et al. | 旋转位置编码 | §3 |
| [FlashAttention](https://arxiv.org/abs/2205.14135) · Dao et al. | 精确注意力的 IO 优化 | §3、Algorithm 1 |

这些论文承担不同层次的解释；建议沿[学习地图](index.md)逐步阅读，不必按发表年份从头读到尾。

## 模型一手来源

### HunyuanVideo

- [HunyuanVideo: A Systematic Framework For Large Video Generative Models](https://arxiv.org/abs/2412.03603)，本次图源固定 `v1`。
- [官方仓库快照](https://github.com/Tencent-Hunyuan/HunyuanVideo/tree/e748c73ac064728bf6bd15b1cdb8161e55a4f331)，本次核验 HEAD 为 `e748c73ac064728bf6bd15b1cdb8161e55a4f331`。
- [主干与默认配置](https://github.com/Tencent-Hunyuan/HunyuanVideo/blob/e748c73ac064728bf6bd15b1cdb8161e55a4f331/hyvideo/modules/models.py)：双流拼接 QKV、单流块、20+40 层、patch 配置。
- [文本编码器准备脚本](https://github.com/Tencent-Hunyuan/HunyuanVideo/blob/e748c73ac064728bf6bd15b1cdb8161e55a4f331/hyvideo/utils/preprocess_text_encoder_tokenizer_utils.py)：语言模型部分与 tokenizer 的处理。

### Wan

- [Wan: Open and Advanced Large-Scale Video Generative Models](https://arxiv.org/abs/2503.20314)，本次图源固定 `v1`。
- [Wan 2.1 快照](https://github.com/Wan-Video/Wan2.1/tree/9737cba9c1c3c4d04b33fcad41c111989865d315)，核验 HEAD 为 `9737cba9c1c3c4d04b33fcad41c111989865d315`。
- [Wan 2.1 主干](https://github.com/Wan-Video/Wan2.1/blob/9737cba9c1c3c4d04b33fcad41c111989865d315/wan/modules/model.py)：self-attention、cross-attention、共享时间调制和每层偏置。
- [Wan 2.1 任务配置](https://github.com/Wan-Video/Wan2.1/tree/9737cba9c1c3c4d04b33fcad41c111989865d315/wan/configs)：1.3B / 14B 的层数、宽度与 VAE stride。
- [Wan 2.2 快照与官方技术说明](https://github.com/Wan-Video/Wan2.2/tree/42bf4cfaa384bc21833865abc2f9e6c0e67233dc)，核验 HEAD 为 `42bf4cfaa384bc21833865abc2f9e6c0e67233dc`。
- [Wan 2.2 任务配置](https://github.com/Wan-Video/Wan2.2/tree/42bf4cfaa384bc21833865abc2f9e6c0e67233dc/wan/configs)：A14B 使用旧 VAE；TI2V-5B 使用 $4\times16\times16$ 新 VAE。

### MiniMax-H3

- [官方发布博客](https://www.minimax.io/blog/minimax-h3)，页面发布日期 2026-07-31。
- [官方仓库固定快照](https://github.com/MiniMax-AI/MiniMax-H3/tree/d21241f0a4b3acbb34c97dae47fa417b7065e438)，commit `d21241f0a4b3acbb34c97dae47fa417b7065e438`。
- [原始 Transformer 配置](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/FL2VA/transformer/config.json)、[VisualVAE 配置](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/vae/config.json)、[AudioVAE 配置](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/audio_vae/config.json)。
- [官方模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3)与[许可原文](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)。
- [SGLang 主干源码](https://github.com/sgl-project/sglang/blob/12771786f23190b1845db33366eba09cb5eacf41/python/sglang/multimodal_gen/runtime/models/dits/minimax_h3.py)，commit `12771786f23190b1845db33366eba09cb5eacf41`：attention 内部扩维、主块调制、非因果 dense 路径。
- [SGLang packed sequence](https://github.com/sgl-project/sglang/blob/12771786f23190b1845db33366eba09cb5eacf41/python/sglang/multimodal_gen/runtime/pipelines_core/stages/model_specific_stages/minimax_h3/packed_sequence.py)：区间组织、padding、update mask。
- [SGLang scheduler](https://github.com/sgl-project/sglang/blob/12771786f23190b1845db33366eba09cb5eacf41/python/sglang/multimodal_gen/runtime/models/schedulers/scheduling_minimax_h3_euler_ancestral.py)：RF velocity 转换和 Euler 更新。

本次未找到 H3 正式技术报告入口。公开推理实现是一手实现证据，但不是训练报告；完整训练 loss、噪声耦合、同步目标等未公开细节保留为未知。

## 14 处论文截图

下表页码为 **PDF 文件页序，从 1 开始**。截图保留原论文图示，仅裁去无关正文；中文解读为本笔记整理，不属于原作者原文。论文和图片版权归各作者或相应权利人，本笔记不赋予它们新的许可。

| 截图 | PDF 版本与页码 | 使用位置 |
| --- | --- | --- |
| DDPM Figure 2 | `2006.11239v2`，p.2 | [Diffusion](diffusion_flow.md) |
| DDPM Algorithm 1 / 2 | `2006.11239v2`，p.4 | [Diffusion](diffusion_flow.md) |
| Transformer Figure 1 | `1706.03762v7`，p.3 | [Transformer](transformer_dit.md) |
| Transformer Figure 2 | `1706.03762v7`，p.4 | [Transformer](transformer_dit.md) |
| LDM Figure 3 | `2112.10752v2`，p.4 | [VAE](video_vae.md) |
| DiT Figure 3 | `2212.09748v2`，p.3 | [DiT](transformer_dit.md) |
| HunyuanVideo Figure 5 | `2412.03603v1`，p.5 | [学习地图](index.md) |
| HunyuanVideo Figure 6 | `2412.03603v1`，p.6 | [VAE](video_vae.md) |
| HunyuanVideo Figure 8 | `2412.03603v1`，p.7 | [模型架构](architectures.md) |
| HunyuanVideo Figure 9 | `2412.03603v1`，p.9 | [文本编码](architectures.md) |
| Wan Figure 5 | `2503.20314v1`，p.10 | [VAE](video_vae.md) |
| Wan Figure 6 | `2503.20314v1`，p.11 | [特征缓存](video_vae.md) |
| Wan Figure 9 | `2503.20314v1`，p.13 | [模型架构](architectures.md) |
| Wan Figure 10 | `2503.20314v1`，p.14 | [Wan block](architectures.md) |

精确裁切区域、渲染比例、PDF SHA-256 与来源记录在[截图清单](../../assets/video_generation/paper_figures.json)。

## 两张官方原图

| 原图 | 固定来源 | 使用位置 |
| --- | --- | --- |
| H3 overview | [官方 `assets/overview.png`](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/assets/overview.png) | [H3 完整系统](minimax_h3.md) |
| H3 full architecture | [官方 `assets/full-arch.png`](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/assets/full-arch.png) | [H3-Base](minimax_h3.md) |

上述两图原样保留，明确标注为官方仓库图。归属：MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax. All Rights Reserved. [许可副本](../../assets/video_generation/h3_license.txt)与[NOTICE](../../assets/video_generation/h3_notice.txt)随图保存。

## 如何复核一条结论

优先检查本页固定版本和对应章节。若是论文披露的训练方式，回到论文；若是层数、张量或 attention 具体操作，回到任务配置与源码；若是本文标注的“推导”，把数字代入公式重新计算。模型生成质量和加速效果没有在本轮笔记整理中运行实验验证。
