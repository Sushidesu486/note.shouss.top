# Digital Image Processing Mock Exam

> This mock exam follows the style of recent DIP recall papers and covers the S/A-level topics in the [high-probability topic summary](high_probability_topics.md). Suggested time limit: 120 minutes. In answers, make the algorithm steps, physical meaning, and variable definitions explicit.

!!! note "Language note"
    This mock exam is written in English for practice. The 2022-2023 recall paper says the real paper was bilingual and answers could be written in Chinese or English. I did not find a clear statement in the lecture transcripts that this year's paper will be English-only.

## Part I. Fill in the Blanks

1. `()` is the main form to present information. For human beings, most information is obtained through `()`.

2. A BMP file usually consists of `()`, `()`, `()`, and `()`.

3. In BMP image data, the number of bytes in each row must be padded to a multiple of `()`. If one row contains `13 A1 17 19 18 15`, it should be stored as `()` in the file.

4. In the RGB color space, the diagonal line from `(0,0,0)` to `(1,1,1)` represents `()`.

5. In HSV, `H` means `()`, `S` means `()`, and `V` means `()`.

6. In RANSAC, assume the probability that one point is an inlier is `w`, each model requires `n` points, and the desired success probability is `p`. The minimum number of iterations satisfies `()`.

## Part II. Short Answer Questions

1. Describe the process by which a digital camera converts optical signals into a digital image.

2. What factors affect depth of field? Explain how each factor changes the depth of field.

3. What is the basic idea of JPEG compression? Why can JPEG discard high-frequency information while maintaining acceptable visual quality?

4. Explain the physical meanings of erosion, dilation, opening, and closing. What is opening commonly used for?

5. How can we obtain a high-quality binary image? Explain using Otsu thresholding and local adaptive thresholding.

6. Why does discrete histogram equalization usually fail to produce a perfectly uniform histogram?

7. Explain the basic idea of bilateral filtering. What is its advantage over Gaussian smoothing?

8. Describe the main steps of SIFT. How does SIFT achieve rotation invariance?

9. Describe the image stitching pipeline and explain the purpose of image blending.

10. What is pooling in CNNs? What are its main functions?

## Part III. Calculation Problems

### 1. Morphological Erosion

Given a binary image `X` and a structuring element `S`, where the origin of `S` is the middle element:

```text
X =
0 0 1 1 0
0 1 1 1 0
0 0 1 1 0
1 1 1 0 0
0 0 1 0 0

S =
1
1
1
```

Compute `X erode S`. Treat pixels outside the image boundary as `0`.

### 2. Discrete Histogram Equalization

An 8-level grayscale image has the following histogram. The total number of pixels is `3600`.

| `k` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|-----|---|---|---|---|---|---|---|---|
| `n_k` | 400 | 600 | 800 | 700 | 500 | 300 | 200 | 100 |

Perform the main steps of discrete histogram equalization: compute `P(r_k)`, compute the cumulative distribution `s_k`, and give the quantized gray-level mapping.

### 3. Median Filtering

Apply a `3x3` median filter to the center pixel of the following window:

```text
12 14 15
13 255 16
14 15 13
```

Find the output value and state what type of noise this filter is especially suitable for.

### 4. RANSAC Iterations

In RANSAC, `w = 0.75`, `n = 4`, and the required success probability is `p > 0.99`. What is the minimum number of iterations?

## Part IV. Comprehensive Questions

1. Given two images with an overlapping region, explain the complete procedure for generating a panorama, from feature point detection to final blending. Also explain what problem RANSAC solves in this pipeline.

2. Explain how back-propagation updates neural network weights. Your answer should include forward propagation, loss, gradient, learning rate, and weight update.

3. With the development of AIGC, deepfake, and multimodal models, what new characteristics will future image information processing have? List at least three application directions and two potential risks.

## Part V. Additional Review-Lecture Questions

These questions are added from the penultimate review lecture, where the emphasis was on computable examples, algorithm steps, and the meaning of each symbol.

1. In geometric transformation, why is inverse mapping usually preferred to forward mapping? What role does interpolation play after inverse mapping?

2. Bilinear interpolation: suppose four neighboring pixels are

    ```text
    I(1,1) = 20   I(2,1) = 40
    I(1,2) = 50   I(2,2) = 90
    ```

    Compute the interpolated value at `(1.25, 1.75)`.

3. Laplacian filtering: given the patch

    ```text
    10 10 10
    10 30 12
    10 14 10
    ```

    use the mask

    ```text
     0 -1  0
    -1  4 -1
     0 -1  0
    ```

    Compute the Laplacian response at the center. If sharpening is defined as `g = f + Laplacian`, what is the sharpened center value?

4. In Fourier-based image analysis, compare magnitude and phase. Which one usually preserves more structural information when reconstructing an image, and why?

5. Harris corner detection: explain how the two eigenvalues of the second-moment matrix indicate a flat region, an edge, or a corner.

6. What is the basic idea of Harris-Laplace? What problem of the original Harris detector does it try to solve?

7. Explain why SURF can be faster than SIFT. Your answer should mention Hessian-based detection and integral images.

8. CNN feature map calculation: an input image has size `32x32x3`. A convolution layer uses `16` filters, each of size `5x5`, with stride `1` and padding `2`. What is the output feature map size? How many trainable parameters does this layer have if each filter has one bias?

9. Explain the `Q/K/V` mechanism in self-attention. Why is positional encoding needed?

10. Describe the expression ratio image method. What assumption is required for the ratio transfer to be meaningful?

## Answer Key

### Part I. Fill in the Blanks

1. `Digital image` or `video stream`; `vision`.
2. `file header`, `information header`, `palette / color table`, `bitmap data`.
3. `4`; `13 A1 17 19 18 15 00 00`.
4. The grayscale axis, representing intensities from black to white.
5. `hue`, `saturation`, `value`.
6. `K >= log(1-p) / log(1-w^n)`.

### Part II. Short Answer Questions

1. Light enters through the lens and aperture. A CCD/CMOS sensor converts light into electrical signals. The analog signals are amplified and converted by A/D conversion. A DSP then performs operations such as color processing, denoising, compression, and encoding before the image is stored.

2. Aperture, focal length, and object distance are the main factors. A larger aperture gives a shallower depth of field; a smaller aperture gives a deeper depth of field. A longer focal length gives a shallower depth of field; a shorter focal length gives a deeper depth of field. A shorter shooting distance gives a shallower depth of field; a longer distance gives a deeper depth of field.

3. JPEG preserves low-frequency structure and color distribution while compressing or discarding high-frequency texture and noise. Human vision is more sensitive to low-frequency structures than to many high-frequency details, so acceptable visual quality can be preserved at a high compression ratio.

4. Erosion outputs foreground only when the structuring element is fully contained in the foreground; it shrinks foreground regions and removes small noise. Dilation outputs foreground when the structuring element intersects the foreground; it expands foreground regions and connects small gaps. Opening is erosion followed by dilation and is commonly used to remove small protrusions and isolated noise. Closing is dilation followed by erosion and is commonly used to fill small holes and cracks.

5. Otsu thresholding selects a global threshold that maximizes the separation between foreground and background, usually by maximizing between-class variance. If illumination is uneven, local adaptive thresholding estimates a separate threshold in each local window. Window size and noise level should be considered.

6. Gray levels are discrete. Multiple input gray levels may map to the same output gray level, while some output gray levels may receive no pixels. Therefore, the result can only be approximately uniform.

7. Bilateral filtering weights neighboring pixels using both spatial distance and intensity similarity, often written as a product of a spatial term `S` and a range/intensity term `R`. Compared with Gaussian smoothing, it can smooth noise while preserving edges better.

8. SIFT builds a scale space, detects extrema, localizes keypoints, assigns a dominant orientation, and builds a local gradient-orientation histogram descriptor. Rotation invariance comes from aligning the local patch according to the dominant orientation.

9. Image stitching usually includes feature detection, descriptor extraction, feature matching, RANSAC outlier rejection and homography estimation, warping into a common coordinate system, and blending. Blending reduces seams, brightness discontinuities, and ghosting in overlapping regions.

10. Pooling is a downsampling operation, such as max pooling or average pooling. It reduces variables and computation, increases the effective receptive field, and improves robustness to small translations.

### Part III. Calculation Problems

1. Erosion result:

    ```text
    0 0 0 0 0
    0 0 1 1 0
    0 0 1 0 0
    0 0 1 0 0
    0 0 0 0 0
    ```

    The vertical three-pixel structuring element requires the upper, center, and lower pixels to all be `1`. Boundary pixels are treated as `0`.

2. Histogram equalization:

    | `k` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
    |-----|---|---|---|---|---|---|---|---|
    | `P(r_k)` | 0.111 | 0.167 | 0.222 | 0.194 | 0.139 | 0.083 | 0.056 | 0.028 |
    | `s_k` | 0.111 | 0.278 | 0.500 | 0.694 | 0.833 | 0.917 | 0.972 | 1.000 |
    | `round(7s_k)` | 1 | 2 | 4 | 5 | 6 | 6 | 7 | 7 |

    Thus the mapping is `0->1`, `1->2`, `2->4`, `3->5`, `4->6`, `5->6`, `6->7`, and `7->7`. If a problem uses floor or ceiling instead of rounding, the mapping may differ slightly. The quantization rule must be stated.

3. Sorted values:

    ```text
    12, 13, 13, 14, 14, 15, 15, 16, 255
    ```

    The median is `14`. Median filtering is especially suitable for salt-and-pepper noise and is robust to isolated outliers.

4. RANSAC:

    ```text
    w^n = 0.75^4 = 0.3164
    K >= log(1-0.99) / log(1-0.3164)
      = log(0.01) / log(0.6836)
      ~= 12.11
    ```

    Therefore, at least `13` iterations are required.

### Part IV. Comprehensive Questions

1. For panorama generation, detect local features such as Harris, SIFT, or SURF; compute descriptors; match descriptors across the two images; use RANSAC to remove outliers and estimate a homography; warp the images into a common coordinate system using inverse mapping and interpolation; then apply average blending, weighted blending, or multi-band blending. RANSAC robustly estimates the geometric transformation in the presence of false matches.

2. Back-propagation starts with random weight initialization. During forward propagation, each layer output and the final prediction are computed. A loss function measures the difference between prediction and label. Gradients of the loss with respect to each weight are computed backward using the chain rule. Weights are updated by `w_new = w_old - eta * partial E / partial w`, where `eta` is the learning rate. The process repeats until the loss converges or the maximum number of training epochs is reached.

3. Future image information processing will be more data-driven, end-to-end, multimodal, real-time, and integrated with recognition, understanding, generation, and editing. Applications include medical image diagnosis, autonomous driving perception, industrial inspection, remote sensing, AIGC image generation and restoration, and AR/VR/MR. Risks include deepfake misuse, privacy leakage, copyright disputes, model bias, and difficulty in content provenance verification.

### Part V. Additional Review-Lecture Questions

1. Inverse mapping maps each output pixel back to a source-image coordinate. It is preferred because every output pixel is visited exactly once, so it avoids holes that may appear in forward mapping. Interpolation then estimates the source intensity at a non-integer coordinate, using nearest neighbor, bilinear interpolation, or another method.

2. Let `dx = 0.25` and `dy = 0.75`. Bilinear interpolation gives

    ```text
    I = (1-dx)(1-dy) * 20
      + dx(1-dy) * 40
      + (1-dx)dy * 50
      + dx dy * 90
      = 51.25
    ```

3. The Laplacian response is

    ```text
    4 * 30 - (10 + 12 + 10 + 14) = 74
    ```

    With `g = f + Laplacian`, the sharpened center value is `30 + 74 = 104`.

4. Magnitude describes how much energy each frequency component has, while phase describes the spatial alignment of those components. Phase usually preserves more image structure because edge positions and object layout depend strongly on phase alignment.

5. If both eigenvalues are small, the window is flat. If one eigenvalue is large and the other is small, the point is on an edge. If both eigenvalues are large, intensity changes strongly in both directions, so the point is a corner.

6. Harris-Laplace first finds Harris corner candidates across multiple scales, then uses a Laplacian or LoG response to select a characteristic scale. It addresses the scale sensitivity of the original Harris detector.

7. SURF uses a Hessian-based detector and approximates expensive filters with box filters. Integral images make rectangle-sum computation constant-time, so SURF can compute detector responses and Haar-wavelet-like features faster than the original SIFT pipeline.

8. The output width and height are

    ```text
    (32 - 5 + 2 * 2) / 1 + 1 = 32
    ```

    Therefore, the output feature map size is `32x32x16`. Each filter has `5 * 5 * 3 = 75` weights plus one bias, so the layer has `(75 + 1) * 16 = 1216` trainable parameters.

9. In self-attention, `Q` is the query vector, `K` is the key vector, and `V` is the value vector. The dot product between `Q` and `K` measures relevance; after softmax, the weights are used to combine the `V` vectors. Positional encoding is needed because self-attention alone is permutation-insensitive and does not know token or patch order.

10. The expression ratio image method aligns a neutral face `A`, its expression version `A'`, and the target face `B`. It computes a ratio image such as `K = A' / A`, warps the target face into the same geometry, and transfers the expression by `B' = K * B_g`. The key assumption is a compatible illumination model, often described by a Lambertian-style assumption with comparable surface-normal changes after alignment.
