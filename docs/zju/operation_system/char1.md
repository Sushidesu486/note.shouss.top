# Introduction

## what is a OS?

- 硬件 (hardware)：包括 CPU、内存、I/O 设备等，为系统提供了基本的计算资源
- 操作系统(operating system)：控制硬件，并协调其在不同应用程序之间，以及不同用户之间的使用
- 系统程序 (system programs) 和应用程序 (application programs)：定义了用硬件资源解决用户计算问题的方法，比如字处理器、电子表格、编译器、网页浏览器等
- 用户 (user)：人、机器或其他计算机
![os](assets/1.1.png)

图中的 **operating system**，此时应该称为 **kernel**

- 教科书式的字面定义：**A program that acts as an intermediary between a user of a computer and the computer hardware**（在用户与计算机硬件之间充当媒介的一个程序）
    - 目标：execute user programs and make solving user problems easier；make the computer system convenient to use；use the computer hardware in an efficient manner
    - 这个定义非常抽象、"摸不着"——只说了 OS 是一个程序、是个媒介，没说它到底做了什么

- 一个更直观的理解：**把其他所有程序都关掉，还始终在运行的那个程序**，就是操作系统
- 它干两件事：一方面给用户提供**方便性**，另一方面把计算机的**资源管理起来**——最大程度地利用内存、处理器、硬盘、各种 I/O 设备，以高效的方式向用户提供服务
- 更精确一点的定义（OS 包括什么）：
    - **resource allocator（资源分配器）**：管理计算机硬件的各种资源（有时甚至包括软件资源）
    - **control program（控制程序）**：控制程序的运行与停止，控制用户对计算机的使用（如你点了一下鼠标，应用程序怎么知道？是操作系统的一种服务告诉它的）
- 注意：OS 没有公认的定义 (no universally accepted definition)；"厂商发行操作系统时给你的一切"是个不错的近似，但差异很大

### Kernel

- 定义：**the one program running at all times on the computer** —— 计算机开机后**始终**在内存中运行的那一个程序
    - 其余程序要么是 system programs，要么是 application programs，都不是一直在运行的
- Kernel 与 Operating System 的关系
    - 前文对 operating system 的定义（控制硬件，并协调其在不同应用程序之间、不同用户之间的使用）描述的是这一层的**职责**；真正直接与硬件打交道、承担这些职责的核心程序就是 **kernel**
    - 广义 operating system = **kernel + system programs**：内核之外还包括随系统发行的系统程序（shell、窗口系统、文件管理工具等），它们并不常驻内存
    - 狭义 operating system = **kernel**：图 1.1 中间那层 "operating system"，实际画的就是 kernel（所以图中称 operating system，此时应称为 kernel）
    - 对比总结
        - kernel：常驻内存、运行于最高硬件权限（kernel mode）的最小程序集合
        - operating system：更宽泛的概念，通常按"厂商发行了什么"界定，以 kernel 为核心

- "kernel 是一个 program"只是暂时的说法：随着逐步去开发一个 kernel，你会发现它**更像是一种服务 (service)**——kernel 里有大量代码和数据结构，可供外部程序调用

### Boot
- bootstrap program is loaded at power-up or reboot
    - Stored in ROM or EPROM, known an firmware
    - Initialize all aspects of system
    - Loads operating system kernel and starts execution
- boot = 穿上靴子（就能跑了）；bootstrap 本义是鞋拔子——在 OS 运行前把 OS 从存储介质加载进内存的那段小程序，存在于主板 ROM 芯片的固件里

### Computer Organization

- **memory**：所有指令和数据都存放在内存；指令从 memory 加载到处理器执行（取指, fetch）
- **CPU**：里面有一大堆**寄存器 (register)**——放指令、放操作数、维护 stack pointer 等关键信息；程序切换运行时要更新寄存器组 (register set)
- **I/O 设备**：显卡/GPU（最早用于绘图，"阴差阳错"变成通用 AI 计算）、USB 外设（鼠标、键盘）、硬盘等
    - 设备本身提供各种资源：磁盘是存储资源、内存是内存资源、鼠标键盘是 I/O 资源、GPU 含处理资源——连同处理器本身，都需要 OS 来管理
- **device driver（设备驱动程序）**：设备的控制器由软件来驱动管理，这个软件就是 device driver，是 OS 的一部分；装一个新设备，OS 里就多一个对应驱动
- CPU 本质上做的事情很简单：不停地在 memory ↔ register 之间搬数据、运行指令、给设备控制器发指令让它工作
- **中断 (interrupt)**：设备完成操作后通过中断通知 CPU——"我做完了，数据给你了，你来处理"；但中断打断的是**正在运行的程序**，所以 OS 必须及时介入，判断是哪个设备发出的中断、接下来干什么——**中断处理由 OS 提供**

### 设计哲学
- **Sharing（共享）**：OS 把计算资源分享给不同的用户、不同的程序（以后称为进程）
    - 例如处理器调度：CPU 定期或不定期地**释放自己正在处理的任务**，转去运行一段无关的代码，由这段代码选择下一个占用处理器的程序——以此实现 CPU 在多个程序之间的共享
- **Isolation（隔离）**：我的程序就是我的程序，你的程序就是你的程序；kernel 与 everything else 划清界限，但外部程序可以调用 kernel 提供的服务（如往屏幕输出文字）
- **Abstraction（抽象）**：进程、线程、文件、virtual memory、调度、文件系统……这些概念全是 OS 创造出来的，是人类智慧的结晶——有计算机之前它们并不存在
- Isolation 与 Sharing 是**相冲突**的：隔离 = 不要搞在一起，共享 = 要搞在一起。OS 通过 Abstraction 实现了这对**对立的统一**——既共享资源，又保证有序、互不搅和（现在没感觉没关系，越学越具体）

## Interrupt & Trap

- 中断处理流程（微观视角）：
    1. 中断发生，控制转到 OS——具体就是处理器跳转到**中断向量 (interrupt vector)**：一张存有所有中断服务程序地址的表，用下标 (index) 定位到对应表项
    2. 控制转到该地址指向的代码，即**中断服务程序 (interrupt service routine)**
    3. 以 I/O 中断为例：输入数据暂存在 kernel 里，中断从 kernel 返回用户程序时，再把数据拷贝给用户程序
- **An operating system is interrupt driven**——中断是 OS 极其重要的组成部分
- 中断的分类：
    - **interrupt（硬中断）**：由硬件触发
    - **trap（软中断）**：由软件引起，又分两种：
        - **error/异常**：程序运行出错，如除零 (divide by zero)，程序被终止
        - **system call（系统调用）**：用户程序**故意**调用系统提供的服务（如输出一段文本到 terminal）——这个词要牢牢记住，以后要自己实现
- **RISC-V 术语对照**（实验基于 RISC-V，看手册别被术语迷惑）：
    - RISC-V 把所有中断统称为 **traps**，下面分 **interrupts**（硬件中断）与 **exceptions & ecalls**（异常与系统调用）
    - 课本里的 system call 在 RISC-V 里叫 **environment call (ecall)**，对应指令就是 `ecall`——ecall = system call

## I/O

- I/O 与中断密切相关，宏观上由 OS 管理（也存在不牵涉具体物理设备的 I/O，以后会见到）
- 流程：用户程序通过 **system call** 发起 I/O 请求 → 设备执行 I/O → 完成后设备发起中断 → 控制转到中断处理程序 → 中断返回，用户程序拿到 I/O 结果继续运行
- 两种 I/O 模式：
    - **同步 (synchronous)**：I/O 操作**完成后**控制才返回调用程序（C 语言里的 `read` / `fread` 就是同步的）
    - **异步 (asynchronous)**：I/O 操作还没完成，控制就已经返回调用程序
- 同步/异步的概念也是在操作系统中形成的，下次课继续展开

![课件 · Two I/O Methods（同步 vs 异步）](assets/two_io_methods.png)
