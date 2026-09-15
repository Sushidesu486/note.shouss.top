# 视频课程与讲座

核对日期：2026-09-13。按学习用途筛选，优先采用讲师、课程官网或报告主办方提供的原始录像。下面的学习顺序、观看重点与自测是本笔记的建议；链接和标题已核对，未逐段审看全部录像，也未核实每个视频的字幕覆盖情况。

## 先选一条路线

- **想先建立直觉**：李宏毅的 Diffusion 入门 → 3Blue1Brown 的 Transformer 与 Attention → 回到[基础笔记](diffusion_flow.md)。
- **想把训练目标推导清楚**：MIT 6.S184 的 Lecture 1–4，配合官方讲义和 Lab 2、Lab 3。
- **想研究长视频与推理效率**：先完成基础和[论文导读](paper_reading.md)，再看 Boyuan Chen 的 Diffusion Forcing 报告。

这些视频有不同的任务背景。看 Transformer 的语言模型例子时，重点学习张量与注意力；看图像生成课程时，再把学到的生成方法与[视频时序建模](paper_reading.md#video-diffusion)连接起来。

## 中文入门 { #chinese }

### 李宏毅：淺談圖像生成模型 Diffusion Model 原理

[YouTube 原视频](https://www.youtube.com/watch?v=azBugJzmz-o) · 李宏毅 / Hung-yi Lee · 中文 · 2023

适合刚读[Diffusion 与 Flow Matching](diffusion_flow.md)时建立整体印象。先带着“训练时给模型看什么、生成时从什么出发”这两个问题观看，再去读 DDPM 的训练与采样算法。课程入口和配套投影片见[臺大官方课程页](https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php)。

需要进一步推导时，可从[Diffusion Model 原理剖析 1/4](https://www.youtube.com/watch?v=ifCDXFdeaaM)开始；其余三讲由同一课程页列出。

**看后自测**：不用“模型会去噪”这句话，描述一次训练迭代和一次采样迭代分别发生了什么。

## Transformer 的视觉直觉 { #transformer }

### 3Blue1Brown：Transformers, the tech behind LLMs

[YouTube · Deep Learning Chapter 5](https://www.youtube.com/watch?v=wjZofJX0v4M) · 3Blue1Brown / Grant Sanderson · 英文 · 2024

适合还不熟悉 token、embedding 和层间数据流时先看。把它当作[Transformer 与 DiT](transformer_dit.md)的预习，随后回到笔记辨认：图像 patch token 与文本 token 的构造方式有什么区别。

**看后自测**：画出 token、embedding、Transformer block、输出之间的数据流，并标记哪些部分属于语言任务。

### 3Blue1Brown：Attention in transformers, step-by-step

[YouTube · Deep Learning Chapter 6](https://www.youtube.com/watch?v=eMlx5fFNoYc) · 3Blue1Brown / Grant Sanderson · 英文 · 2024

重点看 Q/K/V 的角色和注意力如何汇总信息；可以对照作者的[图文版本](https://www.3blue1brown.com/lessons/attention/)。读 DiT 前，先用一个小矩阵例子把 attention 算通。

**看后自测**：若 Q 有 4 个 token、K/V 有 8 个 token，注意力分数矩阵是什么形状？再回笔记区分 self-attention 和 cross-attention。

## 系统课程：MIT 6.S184（2025） { #mit }

Peter Holderrieth 与 Ezra Erives 的课程官网同时提供录像、讲义和实验。本页固定 **2025 版**，以下四个 YouTube 链接直接取自[官方课程页](https://diffusion.csail.mit.edu/2025/)中的录像入口，避免把不同年度的讲次混用。授课语言为英文；宜具备线性代数、概率与微积分基础，做实验还需要 Python / PyTorch。

### Lecture 1：Flow and Diffusion Models { #mit-1 }

[YouTube · Generative AI with SDEs](https://www.youtube.com/watch?v=GCoP2w-Cqtg)

**适合阶段**：开始学习生成轨迹与采样。关注 ODE、SDE 和如何沿轨迹生成样本。

**看后自测**：随机初值与每一步注入随机噪声分别出现在哪里？配合官方 Lab 1，观察更改步长后的轨迹。

### Lecture 2：Constructing a Training Target { #mit-2 }

[YouTube · Constructing a Training Target](https://www.youtube.com/watch?v=yFD-JSSG-D0)

**适合阶段**：已经理解“给定向量场怎样采样”，接着追问训练标签从哪里来。重点辨认条件概率路径与边缘概率路径。

**看后自测**：训练样本已知时容易构造的目标，如何帮助学习生成时需要的向量场？先画图，再读[Flow Matching 导读](paper_reading.md#flow-matching)。

### Lecture 3：Training Flow and Diffusion Models { #mit-3 }

[YouTube · Training Flow and Diffusion Models](https://www.youtube.com/watch?v=HhfLo1_yza4)

**适合阶段**：对照 Flow Matching 和 score matching 的训练方式。观看时分别记下“输入、监督目标、损失、采样器”四项。

**看后自测**：完成官方 Lab 2 的二维玩具分布实验，说明训练循环与生成循环的区别；对应[DDPM 与 Flow Matching 导读](paper_reading.md)。

### Lecture 4：Building an Image Generator { #mit-4 }

[YouTube · Building an Image Generator](https://www.youtube.com/watch?v=nfrZ30mnwP0)

**适合阶段**：从训练目标连接到条件生成、guidance 和网络架构。搭配[LDM 导读](paper_reading.md#ldm)、[DiT 导读](paper_reading.md#dit)阅读。

**看后自测**：在官方 Lab 3 的条件生成实验中，指出条件输入在哪里进入模型；把整套流程拆成表示、主干和采样三个部分。

讲义、Lab 1–3 及参考解答均从[课程官网](https://diffusion.csail.mit.edu/2025/)进入；官方讲义另有[arXiv 版本](https://arxiv.org/abs/2506.02070)。实验使用课程的小规模任务即可，学习时无需先部署完整视频大模型。

## VAE 的概率基础 { #vae }

### Stanford CS236：Lecture 6 — VAEs

[YouTube 原录像](https://www.youtube.com/watch?v=8cO61e_8oPY) · Stefano Ermon / Stanford Online · 英文 · 2023 年课程，2024 年上传

作为[VAE 与视频潜空间](video_vae.md)的补充，适合已经接触概率分布和 ELBO、希望继续理解 VAE 的读者。它是课程中的第六讲，建议遇到前置概念时结合[原始 VAE 论文](https://arxiv.org/abs/1312.6114)回补。

**看后自测**：为什么普通自编码器的重建误差不足以定义这里的概率生成模型？先解释 encoder 和 decoder 的概率角色，再回到视频压缩。

## 作者报告：从全序列到因果生成 { #diffusion-forcing }

### Boyuan Chen：Diffusion Forcing — Next-token Prediction Meets Full-Sequence Diffusion

[YouTube 作者报告](https://www.youtube.com/watch?v=3dOFJKcBWX4) · Boyuan Chen / Valence Labs · 英文 · 2024

适合已经理解扩散噪声时间与序列时间的读者，配合[Diffusion Forcing 导读](paper_reading.md#diffusion-forcing)。这份报告由论文作者讲解，适合了解方法背后的问题设定，而不是只看生成效果。

主办方的视频说明列出了章节入口：[25:30 · Diffusion Forcing](https://www.youtube.com/watch?v=3dOFJKcBWX4&t=1530s)、[42:30 · DF with Causal Uncertainty](https://www.youtube.com/watch?v=3dOFJKcBWX4&t=2550s)。不熟悉背景时从头看。

**看后自测**：分别画出全序列共用一个噪声等级、各 token 使用独立噪声等级的示意图。之后读[Self Forcing 导读](paper_reading.md#self-forcing)，比较“噪声怎样分配”和“训练历史从哪里来”这两个问题。

## 每次观看留下什么

不用逐字抄字幕。每份材料留下一张数据流图、一句方法想解决的问题、一个尚未理解的推导，再用对应论文核对。完成一轮后回到[对比与自测](comparison_lab.md)，检查自己能否独立说明模型各部分的作用。
