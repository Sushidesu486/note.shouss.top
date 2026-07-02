# 图像信息处理期末重点复习

> 浙江大学《图像信息处理》课程录音与 PPT 整理。本文重点参考 2026-06-04、2026-06-11、2026-06-18 最后三次课，并按一天冲刺复习重排。

!!! tip "使用方式"
    先把“必会题型”过一遍，再按章节清单回看 PPT 例题和作业。老师多次强调这门课偏实践，能不能把算法步骤、符号含义和局部计算结果写清楚，比背整页公式更重要。

## 1 考试与作业信息

| 项目 | 内容 |
|------|------|
| 考试日期 | 7 月 3 日 |
| 作业占比 | 40 分，占比很大；未交作业会明显影响总评 |
| 作业补交 | 录音中提到未完成作业最迟 7 月 3 日发给助教，具体以课程群通知为准 |
| 最后安排 | 6 月 11 日先做总复习；6 月 18 日讲 Transformer、deepfake 风险并答疑 |
| 计算题 | 双线性插值、滤波、RANSAC 迭代次数等可能需要手算；录音中提到可用计算器，考场要求以正式通知为准 |

## 2 一天复习路线

| 时间 | 任务 |
|------|------|
| 0.5 h | 过考试信息、作业提交、下面的“必会题型”。 |
| 1.5 h | 复习图像格式、BMP、相机成像、颜色与颜色空间。 |
| 2 h | 复习二值化、形态学、直方图、几何变换与插值。 |
| 2 h | 复习卷积、滤波、Laplacian、双边滤波、guided filter、Fourier。 |
| 2 h | 复习 Harris、SIFT、SURF、图像拼接、RANSAC。 |
| 1.5 h | 复习 CNN、BP、softmax、cross entropy、Transformer。 |
| 1 h | 回看作业代码和 PPT 例题，补齐符号含义和手算过程。 |

## 3 必会题型

1. **BMP 文件结构**：能说出 file header、image information header、palette、bitmap data；知道 BMP 像素通常倒置存储，每行字节数按 4 的倍数补齐。
2. **二值化**：会写人工阈值、Otsu、大津算法的前景/背景分离思想，以及局部自适应阈值为什么能处理光照渐变。
3. **形态学格子题**：给结构元素和二值图，能画 erosion、dilation、opening、closing 的结果；会说明腐蚀和膨胀的对偶性。
4. **直方图均衡化**：会算离散灰度的概率、累计分布、变换结果；知道均衡化后不一定严格均匀。
5. **插值与 morph**：最近邻要反向映射取值；双线性插值用 `g(x,y)=ax+by+cxy+d` 或四邻域加权；morph 要分别处理 RGB 通道。
6. **滤波小计算**：会做一维/二维离散卷积、中值滤波、均值滤波、Laplacian 增强；合并 Laplacian 与原图时注意符号。
7. **双边滤波**：能解释空间域 `S` 与灰度域 `R`，权重同时考虑距离和像素相似性；知道它相对 Gaussian smoothing 的保边优势。
8. **Fourier**：重点看 FFT 的简单推导，以及 magnitude 和 phase 哪个对图像结构更关键。
9. **局部特征**：Harris 角点公式推导思路、两个特征值的含义、尺度敏感性；SIFT 的 dominant orientation、128 维描述子；SURF 的 Hessian 近似和 integral image 加速。
10. **RANSAC**：会按 `K >= log(1-p) / log(1-w^n)` 估计迭代次数；知道 outlier 比例越高、每次采样点数 `n` 越大，迭代次数越多。
11. **图像拼接**：完整流程是特征点检测、特征描述、匹配、RANSAC 去 outlier、估计 transformation、warping、blending；blending 重点是 Gaussian pyramid 与 Laplacian pyramid。
12. **CNN 基础**：会算 feature map 尺寸，理解 receptive field、filter 数量、stride、pooling、softmax、cross entropy、BP 和 learning rate。
13. **Transformer 概念**：会解释 self-attention 的 `Q/K/V`、dot-product attention、multi-head、positional encoding，以及它和 CNN、RNN 的差异。

## 4 章节重点清单

### 图像基础与成像

- 知道可见光、X 光、超声、红外等成像方式及应用场景，例如医疗、安防、工业探伤。
- HDR、panorama、VR/MR、blur 等概念要能用自己的话解释，并举出图像处理任务。
- 相机部分要能从光路讲到数字图像：镜头、光圈、CCD/光电二极管、放大器、A/D 转换、DSP、存储。
- 光圈不是越小越好；要说明大/小光圈对进光量和景深的影响。

### 图像格式、颜色与压缩

- 图像格式要区分无压缩、有损压缩、无损压缩，并能举例。
- JPEG 底层是 DCT；基本思想是优先保留低频结构和颜色分布，按压缩比丢弃更多高频信息。
- JPEG 的详细字段不用硬背，但 metadata 大概存什么、JPEG 的局限性要知道。
- TIFF 常用于扫描仪、CAD、GIS；run-length coding 要掌握基本思想。
- RGB 的物理意义、rod/cone cell、Weber law、hue/saturation/value、device-dependent 与 device-independent color space 要能解释。
- HSV、YUV 等颜色空间字母含义要清楚；颜色空间转换公式不用死记，知道查表后能实现即可。

### 二值图像与形态学

- 二值化分三层：手设阈值、Otsu 自动阈值、局部自适应阈值。
- Otsu 的核心不是“背公式”，而是选一个阈值让前景和背景分得更开。
- 形态学四操作：腐蚀缩小前景，膨胀扩大前景，opening 先腐蚀后膨胀，closing 先膨胀后腐蚀。
- 应用要能说：验证码去噪、工业裂缝/焊接探伤、从噪声中保留目标结构。

### 灰度增强与几何变换

- 灰度增强重点是 log transform、直方图均衡化、直方图匹配。
- 直方图是 global feature，也可以切块后作为 local feature，提高对局部变化的鲁棒性。
- 直方图匹配记住三步：原图均衡化、目标图均衡化、建立两者映射。
- 几何变换要知道 translation、rotation、scaling、warping 等基本形式。
- 最近邻插值和双线性插值都要会算；老师明确提到可能给数值让算中间位置灰度。
- Expression ratio image 重点是 Lambertian model、feature point alignment、ratio image 和重建步骤，不需要背复杂推导。

### 滤波、卷积与频域

- 卷积是加权求和；图像是离散数据，重点掌握离散卷积例题。
- 平滑滤波是低通滤波，代表方法是 Gaussian smoothing；中值滤波属于统计排序滤波。
- 中值滤波窗口不一定必须是奇数中心窗口，关键是排序取中间值。
- 图像锐化重点掌握 Laplacian，注意 4 邻域和 8 邻域 mask，以及增强时的正负号。
- 双边滤波同时考虑空间接近度和灰度相似度，所以比普通 Gaussian 更能保边。
- Guided filter 通过梯度约束保梯度；与 bilateral filter 对比时重点说 gradient preserving。
- Fast bilateral filter 重点理解为什么能加速，不必陷入每个推导细节。

### 特征、匹配与拼接

- Harris：会从局部窗口平移导致灰度变化的思想讲起，理解小特征值也大时才是角点。
- Harris 对尺度敏感；Harris-Laplace 通过找响应最大的尺度缓解尺度问题。
- SIFT：通过 dominant orientation 实现旋转不变性；128 维 descriptor 的构造过程要知道。
- SURF：核心看 detector、Hessian 近似、integral image；要能说明为什么比 SIFT 更快。
- 图像拼接重点不是单个算法名，而是 pipeline 和每一步解决什么问题。
- RANSAC 优点是通用、易实现；缺点是 outlier 过高时迭代次数暴涨，超过 50% 时往往不划算。

### CNN 与深度模型

- 从 handcrafted feature 转到 learnable feature 是主线：以前手工设计 SIFT/SURF，现在让模型从数据中学习 filter。
- CNN 成功的原因包括参数共享、局部感受野、feature map、pooling 降采样和 GPU 训练。
- Pooling 有空间域和特征域两个方向；作用是突出显著特征、减少变量、扩大有效感受野，并对小位移/小旋转更鲁棒。
- 神经元是加权求和加 activation；常见 activation 包括 sigmoid、ReLU。
- BP 基本步骤：随机初始化权重、前向计算、计算误差、按梯度更新 `W_k = W_{k-1} - eta * dE/dW`，直到收敛。
- Learning rate 很关键：太大可能不收敛，太小收敛慢或卡住。
- 分类器重点看 `softmax(WX)`、`argmax`、cross entropy；`-log p_c` 越小表示真类概率越高。
- CNN feature map 尺寸题要看输入尺寸、filter 大小、stride、padding 和 filter 数量。

### Transformer 与生成式 AI

- Self-attention 的目的：学习序列中不同 vector/token 的上下文关系，找出关键 token。
- Dot-product attention 重点关注 `Q` 与 `K` 的相似度，softmax 后作为权重加权 `V`。
- Multi-head 表示用多个视角学习同一序列的不同关系。
- Self-attention 本身没有位置信息，所以要加 positional encoding。
- CNN 主要看局部 receptive field；self-attention 可以看整个 sequence 的上下文。
- RNN 依赖前序结果，不容易并行；self-attention 更适合并行训练。
- 图像中可把 patch/feature 拉成 sequence；DETR、ViT 等把 CNN 特征或图像 patch 接入 Transformer。
- GAN、VAE、diffusion model 只需掌握基本思想和优缺点；deepfake 风险要能举例说明。

## 5 低优先级与易混点

- 颜色空间之间的具体转换公式不用背，理解含义和实现路径即可。
- JPEG/TIFF 的每个文件字段不用逐项记；BMP 文件结构要非常熟。
- 语音例子中的 MFCC 细节不用管，它只是说明序列数据也可转成 vector set。
- GAN 加 self-attention 的旧方法不作为重点，最后一课明确说不用关心上面那部分；更该知道 DETR/ViT 和 diffusion 的基本概念。
- 看到“公式推导”不要只背结果：老师更看重你能解释变量含义、算法步骤和适用场景。

## 6 最后三次课信号

| 日期 | 重点信号 |
|------|----------|
| 6 月 4 日 | 提醒作业占 40 分，未完成要尽快补；复习前先把 CNN 的 BP、cross entropy、feature map 和 pooling 搞清楚。 |
| 6 月 11 日 | 系统串讲全课重点，是期末复习主线；大量强调“会算”“会画结果”“能解释符号”。 |
| 6 月 18 日 | 确认 7 月 3 日考试；讲 Transformer、DETR/ViT、生成式 AI、deepfake，并留出答疑。 |

!!! warning "冲刺取舍"
    若只剩一天，优先保证手算题和算法步骤题：BMP、二值化、形态学、直方图、插值、滤波、Harris/SIFT/SURF、RANSAC、CNN。Transformer 和 deepfake 更偏概念理解，别把时间全部花在大模型科普细节上。
