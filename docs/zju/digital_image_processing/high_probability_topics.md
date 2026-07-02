# 图像信息处理高概率考点

> 基于 [20-21 回忆卷](20-21.md)、[21-22 回忆卷](21-22.md)、[22-23 Final 回忆卷](22-23final.md) 与 [23-24 Fall 试题解析](23_24_fall_exam.md) 汇总。出现频率只用于安排复习优先级，不等于押题保证。

## 复习优先级总表

| 优先级 | 高频模块 | 出现情况 | 必须会到什么程度 |
|--------|----------|----------|------------------|
| S | 图像基础、成像、BMP | 连续多卷出现 | 能填空、列结构、解释 padding / palette / 成像流程 |
| S | 形态学 | 每年都接近必考 | 会画 erosion / dilation / opening，能说明物理意义与对偶性 |
| S | 直方图 | 多卷反复出现 | 会均衡化表格、解释不均匀原因、写匹配步骤 |
| S | 深度学习基础 | 近几年稳定出现 | 会写 BP 流程、权重更新、pooling 作用 |
| A | 滤波与增强 | 多卷出现 | 会 log enhancement、median / Laplacian、bilateral / guided 对比 |
| A | 特征与拼接 | 多卷出现 | 会 SIFT/SURF、RANSAC、stitching pipeline、blending |
| A | 几何变换与插值 | 多卷出现 | 会 nearest / bilinear interpolation、morph、expression ratio |
| B | JPEG、RLE、颜色空间 | 隔年出现 | 会基本思想、优点、RGB/HSV/设备相关性 |
| B | AI 开放题 | 新卷出现 | 能从生成式 AI、多模态、deepfake 风险展开 |

## S 级：几乎必须准备

### 1. 图像基础、成像与 BMP

常见问法：

- 为什么数字图像是信息的主要展示方式？举成像方式。
- 数码相机如何生成图片？
- BMP 文件结构、行补齐、调色板作用。

答题模板：

- 数字图像/视频是视觉信息的主要表达形式，人类大量信息来自视觉。
- 成像方式可举 visible light、X-ray、ultrasound、infrared、MRI、radar。
- 数码相机流程：光线经镜头和光圈进入，CCD/CMOS 感光，光电转换，放大和 A/D 转换，DSP 处理，编码存储。
- BMP 结构：file header、information header、palette/color table、bitmap data。每行字节数补齐到 4 的倍数，24-bit 像素常按 BGR 存储。

易错点：BMP padding 是按“每行”补，不是按整个文件补；低位深图像才重点依赖 palette。

### 2. 形态学

常见问法：

- 给结构元素和二值图，画 erosion / dilation。
- 说明腐蚀、膨胀、开运算的物理意义。
- 证明或解释腐蚀和膨胀的对偶关系。

答题模板：

- Erosion：结构元素完全落在前景中才输出 1，效果是收缩前景、去小噪声、断开细连接。
- Dilation：结构元素与前景有交集就输出 1，效果是扩张前景、填小洞、连接断裂。
- Opening：先腐蚀后膨胀，去小突出和小噪声。
- Closing：先膨胀后腐蚀，填小洞和小裂缝。
- 对偶性：腐蚀与膨胀在补集和结构元素反射下互为对偶，可写为 `(A erode B)^c = A^c dilate B^s`。

做格子题时先标结构元素原点，再逐点判断“全包含”或“有交集”。

### 3. 直方图均衡化与匹配

常见问法：

- 填离散直方图均衡化表格。
- 为什么离散均衡化后不真正均匀？
- 写直方图匹配过程。

答题模板：

1. 统计 `n_k`，计算 `P(r_k)=n_k/n`。
2. 求累计分布 `s_k=sum_{i=0}^k P(r_i)`。
3. 将 `s_k` 量化到 `L` 个灰度级，如 `round((L-1)s_k)/(L-1)`。
4. 合并映射到同一输出灰度的像素数。

不均匀原因：灰度级是离散的，多个输入灰度可能映射到同一输出灰度，有些输出灰度可能没有像素，因此不可能严格均匀。

直方图匹配：分别求原图和目标图累计分布，再按最接近的累计概率建立 `r_k -> z_q` 映射。

### 4. BP、Pooling 与深度学习基础

常见问法：

- 写 Back-propagation 全过程。
- 说明 pooling 是什么、有什么作用。
- 给权重符号，说明如何迭代更新。

答题模板：

- 初始化权重，前向传播得到预测值，用 loss function 计算误差。
- 从输出层向前按链式法则计算梯度。
- 用梯度下降更新：`w^{k+1}=w^k-eta * partial E / partial w^k`。
- 重复训练直到收敛。
- Pooling 是降采样操作，可减少变量、扩大有效感受野、增强小位移鲁棒性，常见 max pooling 和 average pooling。

易错点：BP 不是“直接算出最优权重”，而是通过 loss 梯度逐步迭代。

## A 级：高概率拉分题

### 5. 滤波、增强与边缘

常见问法：

- 对数增强过程。
- 用 `3x3` 窗口算 median filter 和 Laplacian filter。
- 双边滤波 general idea，各项含义，与 Gaussian / guided filter 比较。
- 证明 SNF 中 `p=1` 是中值滤波，`p=2` 是均值滤波。

答题模板：

- Log enhancement：`s = c log(1+r)`，压缩高灰度动态范围、增强暗部细节。
- Median filter：窗口内排序取中值，适合去椒盐噪声。
- Laplacian：二阶微分锐化，增强边缘，也会放大噪声。
- Bilateral filter：权重同时考虑空间距离和灰度相似度，`W = S(distance) * R(intensity)`，比 Gaussian 更能保边。
- Guided filter：用局部线性模型引导输出，速度快，梯度保持较好，较少出现梯度反转。

### 6. SIFT、SURF、拼接与 RANSAC

常见问法：

- SIFT full version，如何实现旋转不变性。
- SURF 的基本步骤。
- 如何实现图像拼接和 image blending。
- RANSAC 步骤及迭代次数计算。

答题模板：

- SIFT：尺度空间极值检测，关键点定位，分配 dominant orientation，生成 `4x4x8=128` 维描述子。
- 旋转不变性来自 dominant orientation 对齐。
- SURF：Hessian detector、integral image 加速、Haar wavelet 描述，通常比 SIFT 更快。
- 拼接流程：特征检测，描述子匹配，RANSAC 去 outlier，估计 homography，warping，blending。
- Blending：简单加权平均或 multi-band blending；Gaussian pyramid 处理低频过渡，Laplacian pyramid 保留高频细节。

RANSAC 公式：

```text
K >= log(1-p) / log(1-w^n)
```

若 `w=0.8, n=3, p=0.95`，则 `K≈4.18`，至少取 `5` 次。

### 7. 插值、Morph 与表情比例图

常见问法：

- 最近邻插值或双线性插值过程。
- 给人脸 morph 图，说明如何 morph。
- 表情比例图 expression ratio image 方法。

答题模板：

- 插值一般用 inverse mapping，从输出像素反查原图位置，避免空洞。
- 最近邻：取最近整数坐标，速度快但有锯齿。
- 双线性：用四邻域按水平、垂直两次线性加权。
- Morph：先找对应特征点，计算中间形状，分别 warp 两张图，再按比例 cross-dissolve 颜色。
- Expression ratio：对齐 `A`、`A'` 和目标人脸 `B`，计算 `K=A'/A`，输出 `B'=K*B_g`。

## B 级：常见填空与说明题

### 8. JPEG、RLE 与颜色空间

JPEG 要点：利用人眼对低频更敏感的特点，尽量保留低频轮廓和颜色分布，压缩或丢弃高频纹理与噪声；优点是压缩比高，适合互联网图像。

RLE 要点：把连续相同像素写成 `(value, length)`，适合大面积相同灰度或二值图；对噪声多、变化频繁的图像压缩效果差。

颜色空间要点：

- RGB 是设备相关颜色空间，立方体中 `(0,0,0)` 到 `(1,1,1)` 的对角线表示灰度轴。
- HSV 中 `H` 是 hue，`S` 是 saturation，`V` 是 value；更接近人对颜色的直观描述。
- CIE XYZ / Lab 常作为设备无关颜色空间。

### 9. AI 开放题

可答方向：

- 技术特征：数据驱动、端到端、多模态、实时化、生成与理解结合。
- 颠覆应用：医学影像、自动驾驶、工业质检、遥感、AR/VR、AIGC 图像生成与编辑。
- 风险：deepfake、版权、隐私、偏见、可信溯源。

开放题不要只写“大模型很强”。应把传统图像处理的增强、分割、配准、拼接，与 AI 的识别、生成、交互能力联系起来。

## 最后一天背诵顺序

1. 先背 BMP、成像、颜色空间、JPEG、RLE 这类填空和短答。
2. 再练形态学格子题和直方图均衡化表格。
3. 然后过滤波计算、插值、morph、expression ratio。
4. 最后背 SIFT/SURF、拼接、RANSAC、BP/pooling 的流程题。

!!! warning "最容易丢分的点"
    不要只写算法名。DIP 回忆卷更常要求“过程、物理意义、为什么、计算结果”。每个高频题至少准备 3 到 5 个可直接写在卷面上的关键词。
