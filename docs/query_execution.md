# Query Execution 学习笔记

> CMU 15-445/645 Intro to Database Systems — Lecture #13 & #14

!!! tip "关于本笔记"
    本笔记基于 CMU 15-445/645 数据库系统课程的两节 Query Execution 课程的字幕整理而成，包含处理模型、进程模型、并行执行策略等核心知识点，以及 10 道 CMU 真题精练。

## 1 概述

当数据库系统接收到一条 SQL 查询后，它会将 SQL 转换为一个**查询计划（Query Plan）**——通常是一个由算子（Operator）组成的有向无环图（DAG）。大部分系统将其实现为**树结构**。叶节点是扫描算子（Seq Scan / Index Scan），中间节点是 Join、Filter、Projection 等算子，根节点负责输出最终结果。

本节的核心问题是：

1. **处理模型（Processing Model）**：数据如何在算子之间传递？每次传一个 tuple、全部传、还是分批传？
2. **控制流（Control Flow）**：从上往下拉取（Pull），还是从下往上推送（Push）？
3. **并行执行（Parallel Execution）**：如何利用多核 / 多节点加速查询？
4. **进程模型（Process Model）**：系统如何组织 Worker（线程 / 进程）来执行查询？

## 2 处理模型（Processing Model）

处理模型定义了 DBMS 如何执行查询计划，以及数据如何从一个算子移动到下一个算子。不同的处理模型在 OLTP 和 OLAP 场景下有各自的优势和劣势。每种模型都包含两个核心维度：

- **控制流（Control Flow）**：谁决定何时执行哪个算子？
- **数据流（Data Flow）**：算子的输出数据发往哪里，以什么形式发送？

### 2.1 迭代器模型（Iterator Model / Volcano Model / Pipeline Model）

迭代器模型是最经典、最广泛使用的处理模型。几乎所有行存储系统（PostgreSQL、MySQL、Oracle、DB2、MongoDB 等）都采用了这种模型。

!!! info "核心思想"
    每个算子实现一个统一的 API，包含三个函数：

    ```python
    class Operator:
        def Open():    # 初始化算子状态（如创建 B+ 树迭代器）
        def Next():    # 返回下一个 Tuple，若无更多数据则返回 null/EOF
        def Close():   # 清理算子资源
    ```

    父算子通过反复调用子算子的 `Next()` 来获取数据。每个 `Next()` 调用只返回**一个 tuple**。

???+ example "执行示例"
    考虑查询 `SELECT R.id, S.value FROM R JOIN S ON R.id = S.id WHERE S.value > 100`：

    ```text
             Project (R.id, S.value)
                      |
                  Hash Join
                 /         \
            Scan(R)      Filter (S.value>100)
                              |
                          Scan(S)
    ```

    执行过程：

    1. 根节点 Project 调用 `Join.Next()`
    2. Join 是 Hash Join，先调用 `Scan(R).Next()` 逐个获取 R 的所有 tuple，构建哈希表（Pipeline #1 = Build Side）
    3. 哈希表构建完成后，Join 调用 `Filter.Next()` → Filter 调用 `Scan(S).Next()` 获取 S 的 tuple
    4. 过滤后满足条件的 tuple 传给 Join 做 Probe，匹配成功的 tuple 逐个向上传递给 Project
    5. Project 每次收到一个 tuple，输出一行结果

    注意 Hash Join 在哈希表未完全构建前就开始 Probe 会产生 **false negative**（要匹配的 tuple 可能还没被插入哈希表），所以 Pipeline #1（Build Side）必须完成后才能开始 Pipeline #2（Probe Side）。

!!! tip "Pipeline Breaker（流水线断点）"
    Pipeline Breaker 是指必须等待所有数据到齐才能继续的算子边界。常见的 pipeline breaker 包括：

    - Hash Join 的 Build Side
    - Sort（ORDER BY）——无法在看到所有输入前确定排序
    - 未去关联的嵌套子查询

| 优点 | 缺点 |
|------|------|
| 实现简单，几乎所有数据库系统都支持 | 每个 tuple 都涉及一次虚函数调用，对内存数据库开销大 |
| 易于调试——可以逐步跟踪函数调用链 | 指令缓存局部性差——CPU 在不同算子的代码之间频繁跳转 |
| 输出控制容易——实现 `LIMIT 10` 只需在收到 10 个 tuple 后停止 | 难以从外部中断查询——控制流已深入递归调用栈中 |
| 算子之间完全解耦——父算子不关心子算子的实现细节 | |

该模型也称为 **Volcano Model**，得名于 Goetz Graefe 在 1990 年代初发表的 Volcano 论文。Graefe 同时也是 B+ 树经典教材的作者。

### 2.2 物化模型（Materialization Model）

物化模型是迭代器模型的对立面——每次调用不是返回一个 tuple，而是返回**所有 tuple**。

!!! info "核心思想"
    每个算子的 `Output()` 函数将所有输出 tuple 放入一个输出缓冲区，然后一次性返回：

    ```python
    class Operator:
        def Output():
            output_buffer = []
            for tuple in process_all_data():
                output_buffer.append(tuple)
            return output_buffer
    ```

这种模型的问题在于：如果 S 有 10 亿行但只有 2 行满足 `S.value > 100`，我们先把 10 亿行全部物化再过滤，浪费极大。

!!! tip "优化：算子融合（Operator Fusion）"
    将同一个 pipeline 中不需要阻断的算子内联合并。例如，Scan + Filter 可以合并为一次操作——扫描时就应用谓词，只把匹配的 tuple 放入输出缓冲区。可以用于 Projection、Filter、Limit（无 ORDER BY 时）等操作。

| 优点 | 缺点 |
|------|------|
| 减少了函数调用次数 | 对于 OLAP 分析查询（处理大量数据但中间结果也很大）会导致巨大的内存开销 |
| 对于只返回少量 tuple 的 OLTP 查询很高效 | 不适合需要处理大量中间结果的场景 |

!!! info "使用系统"
    MonetDB（CWI 阿姆斯特丹，1990 年代）、Hyper（初期版本）、VectorWise、CrateDB、RavenDB。DuckDB 的前身 MonetDBLite 也使用此模型。Hyper 后来放弃了此模型转而使用代码生成。

### 2.3 向量化模型（Vectorized / Batch Model）

向量化模型是迭代器模型和物化模型之间的折中——每次 `Next()` 调用返回**一批（batch）tuple**（通常是 128~1024 个）。

!!! info "核心思想"

    ```python
    class Operator:
        def Next():
            batch = []  # 固定大小的 batch，如 1024 个 tuple
            for i in range(BATCH_SIZE):
                tuple = get_next_tuple()
                if tuple is EOF: break
                batch.append(tuple)
            return batch
    ```

!!! tip "向量化模型的额外优势"

    - **SIMD 向量化**：对一批数据执行相同操作时，CPU 可以使用 SIMD 指令并行处理
    - **缓存友好**：批量处理同一列数据，CPU 缓存命中率更高
    - **列式压缩**：如果一列中有大量相同值（如 `id = 1` 出现 1000 次），可以用常量向量表示
    - **DuckDB 的优化**：自动检测常量向量、运行长度编码、Delta 编码等

| 优点 | 缺点 |
|------|------|
| 相比迭代器模型，函数调用开销摊薄到每个 batch | 实现比迭代器模型复杂 |
| 相比物化模型，内存占用可控 | 对于只返回极少量 tuple 的 OLTP 查询，仍有额外的 batch 管理开销 |
| 适合 OLAP 工作负载——Snowflake、Databricks 等现代分析数据库的选择 | |
| 启用 SIMD 加速 | |

!!! info "使用系统"
    DuckDB、ClickHouse、Snowflake、Databricks、VectorWise 等。该模型自 2006-2007 年开始流行。

### 2.4 三种处理模型对比

| 特性 | 迭代器模型 | 物化模型 | 向量化模型 |
|------|-----------|---------|-----------|
| 每次传递 | 1 个 tuple | 所有 tuple | 一批 tuple (128-1024) |
| 函数调用开销 | 最高 | 最低 | 中等 |
| 内存占用 | 最低 | 最高 | 中等 |
| SIMD 友好 | 不友好 | 友好 | 非常友好 |
| 适用场景 | OLTP (行存储) | OLTP | OLAP (列存储) |
| 典型系统 | PostgreSQL, MySQL | MonetDB, Hyper(早期) | DuckDB, ClickHouse, Snowflake |
| 输出控制(LIMIT) | 最容易 | 较难 | 容易 |

## 3 访问方法（Access Methods）

在查询计划的叶节点，数据通过以下方式从表中读出：

1. **顺序扫描（Sequential Scan / Table Scan）**：遍历表中的每一个 page，读取每一个 tuple。最简单但最"暴力"的方式。
2. **索引扫描（Index Scan）**：利用 B+ 树等索引结构直接定位到所需的 tuple，避免全表扫描。
3. **多索引 / 位图扫描（Multi-Index / Bitmap Scan）**：对多个条件分别使用索引，然后取交集。

!!! tip "索引扫描 vs 顺序扫描"
    索引扫描不总是优于顺序扫描。如果查询需要访问表中大部分数据，索引扫描反而会因为随机 I/O 而更慢。此外，索引扫描本身也有遍历 B+ 树的开销。

## 4 并行查询执行（Parallel Query Execution）

本课程之前的讨论假设只有一个单线程在执行查询。现代硬件提供了多种并行资源：多核 CPU、多 CPU 插槽、多个存储设备。我们需要利用这些资源来加速查询执行。

### 4.1 并行数据库 vs 分布式数据库

| 特性 | 并行数据库 | 分布式数据库 |
|------|-----------|------------|
| 资源距离 | 物理上紧密（同机/同机架） | 物理上分散（不同数据中心） |
| 通信 | 快速、可靠、低成本 | 慢速、可能不可靠、高延迟 |
| 故障处理 | 通常假设通信可靠 | 需要处理消息丢失、节点故障 |
| 算法假设 | 不需要考虑通信失败 | 必须在协议中处理故障 |

!!! tip "关键点"
    无论系统运行在单核笔记本还是千核分布式集群上，同一 SQL 查询应该产生相同的正确结果。这是**逻辑层和物理层分离**的体现。

### 4.2 进程模型（Process Model）

进程模型定义了系统如何组织 Worker 来执行查询。

#### 4.2.1 每个Worker一个进程（Process per Worker）

- 每个 Worker 是一个完整的操作系统进程（通过 `fork()` 创建）
- 拥有独立的地址空间
- Worker 之间通过 IPC（进程间通信）或共享内存通信

**优点**：一个进程崩溃不会影响其他进程。

**缺点**：进程创建开销大，通信成本高，依赖 OS 调度。

!!! info "使用系统"
    PostgreSQL（postmaster / postgress）、Oracle、DB2（早期版本）。

这些老牌系统选择进程而非线程，是因为它们起源于 1980-1990 年代，当时各 Unix 变体的线程库互不兼容——HP-UX、AIX、Solaris 各有不同实现。而 `fork()` 作为 POSIX 标准接口在所有系统上都可用，因此选择 Process per Worker 可以保证跨平台兼容性。

#### 4.2.2 每个Worker一个线程（Thread per Worker）

- 每个 Worker 是一个操作系统线程（如 pthreads）
- 所有线程共享同一个地址空间，通信成本极低
- DBMS 可以自行管理线程调度

**优点**：通信快、调度灵活、创建开销小。

**缺点**：一个线程崩溃可能导致整个系统崩溃。

!!! info "使用系统"
    几乎所有过去 20 年新建的数据库系统（MySQL、MariaDB、SQL Server 等）。DB2 和 Oracle 后来也添加了线程支持。

#### 4.2.3 嵌入式数据库（Embedded DBMS）

- 数据库以库（Library）形式嵌入应用程序中
- 没有独立的 dispatcher，使用调用方的线程执行查询

!!! info "使用系统"
    SQLite、Berkeley DB、RocksDB、DuckDB（也支持多线程）。Berkeley DB 是最早的嵌入式数据库之一（UC Berkeley，80 年代末 / 90 年代初），2016 年被 Oracle 收购。

!!! tip "重要区分"
    支持多个 Worker 不等于支持**查询内并行（Intra-Query Parallelism）**。例如 MySQL 虽然是多线程的，但一条查询只能由一个线程执行完（不支持查询内并行）。PostgreSQL 和 Redis 的 fork 版本也是如此。

### 4.3 查询间并行（Inter-Query Parallelism）

多个查询同时执行，每个查询被分配给不同的 Worker。

- 最常见的并行方式
- 调度策略通常是 FIFO（先来先服务）
- 高级系统（如 DB2）支持基于用户/事务优先级的调度
- 如果所有查询都是只读的，实现很简单——不需要协调不同查询
- 挑战：如果有写操作，需要并发控制机制（后续课程覆盖）

### 4.4 查询内并行（Intra-Query Parallelism）

将一条查询拆分为多个任务，分配给多个 Worker 同时执行。

#### 4.4.1 水平并行 / 算子内并行（Intra-Operator / Horizontal Parallelism）

- 同一个算子的多个实例在不同数据子集上并行运行
- 将输入数据划分为多个不重叠的分区（partition），每个 Worker 处理一个分区
- **不需要** Worker 之间协调——每个 Worker 处理的是不相交的数据子集
- **最常见**的查询内并行方式

!!! info "Exchange 算子"
    当并行执行的算子需要将结果合并时，使用 **Exchange 算子**。它充当一个**同步屏障（Barrier）**——必须等待所有子 Worker 完成后才能继续。

    - 不对应任何关系代数操作
    - 在 PostgreSQL 中称为 **Gather** 节点
    - 类似 MapReduce 中的 shuffle/reduce 阶段
    - 概念来自 Goetz Graefe 的 Volcano 论文（1990 年代）

???+ example "并行 Hash Join 执行示例"
    查询：`SELECT * FROM A JOIN B ON A.id = B.id WHERE A.value > 10 AND B.value < 50`

    ```text
    执行过程：
    1. 表 A 被分为 3 个分区 → 3 个 Worker 并行执行：Scan(A) → Filter(A.value > 10) → Projection
    2. 所有 Worker 的结果通过 Exchange 算子合并，构建全局 Hash Table
    3. 表 B 同样并行扫描、过滤
    4. Probe 阶段，结果通过 Exchange 输出
    ```

!!! tip "分治复用"
    可以在并行执行中充分利用之前学过的分治算法。例如 Grace Hash Join 的分桶阶段，不同桶可以由不同 Worker 独立处理。

#### 4.4.2 垂直并行 / 算子间并行（Inter-Operator / Vertical Parallelism）

- 不同的算子/流水线同时运行
- 通过显式的依赖图协调执行顺序
- 在流式处理系统中更常见

#### 4.4.3 丛生并行（Bushy Parallelism）

- 水平并行和垂直并行的组合
- 只有高端系统支持
- 多个独立的子树可以完全并行执行

!!! info "这三种并行策略并不互斥，高端系统可以混合使用。"

### 4.5 I/O 并行（I/O Parallelism）

除了 CPU 并行，还可以利用多个存储设备进行 I/O 并行：

- 将数据划分到多个磁盘/存储设备上
- 每个设备可以独立进行 I/O 操作
- 常见划分方式：Round-Robin、Hash Partitioning、Range Partitioning
- 可以与上述 CPU 并行方式组合使用

## 5 处理写操作（Handling INSERT / UPDATE / DELETE）

对于修改数据的查询：

- **INSERT**：算子不需要子节点扫描数据，而是直接插入新 tuple
- **UPDATE/DELETE**：通常需要先扫描找到目标 tuple，记录修改前的值（用于 undo/回滚），然后执行修改
- 需要考虑并发控制——多个事务同时修改相同数据时如何保证正确性
- 需要维护索引——如果修改了索引列，索引结构也需要更新

## 6 谓词评估（Predicate Evaluation）

执行 `WHERE a = 1` 这样的条件时，系统需要评估谓词：

- **简单条件**：直接比较
- **复杂条件**：可能需要调用函数（如 `UPPER(name) = 'ALICE'`）
- **优化**：将谓词尽可能下推（push down）到靠近叶节点的位置，减少需要传递的数据量

## 7 系统设计哲学

!!! tip "Andy Pavlo 的核心观点"
    **DBMS 总是比操作系统更适合做出执行决策。**

    操作系统看到的只是"盲目的"线程和进程，它不了解查询的语义、数据的分布、pipeline 的结构。而 DBMS 了解查询的完整上下文，可以做出更优的调度决策。因此高端系统（Oracle、SQL Server 等）甚至重写了操作系统的调度器，由数据库自己管理所有资源。

## 8 CMU 15-445 考题精练

题目 1–5 来自 CMU 15-445/645 Fall 2022 Homework #3, Question 3: Query Execution（[原题](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-clean.pdf) | [参考答案](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-sols.pdf)）。题目 6–10 为基于 Lecture #13 & #14 内容编写的练习题。

### 题目 1：Processing Model Working Buffer

**来源**: [Fall 2022 HW3 Q3(a)](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-clean.pdf) [6 points]

!!! question "Which processing model has on average the smallest working buffer per operator invocation? Ignore optimizations like projection pushdown. Select only one answer."
    中文翻译：哪种处理模型在每次算子调用时的平均工作缓冲区最小？（忽略投影下推等优化）

=== "选项"
    - [ ] A. Iterator
    - [ ] B. Materialization
    - [ ] C. Vectorization

=== "答案与解析"
    **A. Iterator**

    > The iterator model processes a single tuple at a time. The materialization model processes its input all at once and emits its output all at once. The vectorization model emits batches of tuples. A single tuple is smaller than multiple tuples.
    >
    > — CMU 15-445/645 Fall 2022 HW3 Solutions

    中文解析：迭代器模型每次只处理一个 tuple，因此需要的缓冲区最小。物化模型需要存储所有输出 tuple，向量化模型需要存储一批 tuple。

### 题目 2：Iterator Model Independence

**来源**: [Fall 2022 HW3 Q3(b)](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-clean.pdf) [6 points]

!!! question "In the iterator processing model, the logic of an operator is independent of its children and parents. (i.e., the code does not case on what type of iterator the children or parents are)"
    中文翻译：在迭代器处理模型中，算子的逻辑是否独立于其子算子和父算子的类型？（即代码不根据子算子或父算子的类型做分支）

=== "选项"
    - [ ] A. True
    - [ ] B. False

=== "答案与解析"
    **A. True**

    > Iterators receive tuples as input and emit tuples as output. Consequently, iterators compose cleanly. Any iterator can be used as input or output to any other iterator, without writing custom code for each possible iterator configuration.
    >
    > — CMU 15-445/645 Fall 2022 HW3 Solutions

    中文解析：迭代器模型的核心优势之一就是算子之间的解耦。每个算子只需要实现 `Open/Next/Close` 接口，不需要知道调用方或被调用方的具体类型。

### 题目 3：Vectorized Model & Multi-threading

**来源**: [Fall 2022 HW3 Q3(c)](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-clean.pdf) [6 points]

!!! question "In the vectorized processing model, each operator that receives input from multiple children requires multi-threaded execution to generate the Next() output tuples from each child."
    中文翻译：在向量化处理模型中，每个需要从多个子节点获取输入的算子是否需要多线程执行来生成 Next() 的输出 tuple？

=== "选项"
    - [ ] A. True
    - [ ] B. False

=== "答案与解析"
    **B. False**

    > Iterators couple dataflow with control flow. When Next() returns a batch of tuples in the dataflow graph, control is returned too. Subsequently, the entire query plan can be executed with only one thread.
    >
    > — CMU 15-445/645 Fall 2022 HW3 Solutions

    中文解析：向量化模型中的多子节点算子（如 Join）不需要多线程来分别从子节点获取数据。它可以在单个线程中依次调用各个子节点的 `Next()`。

### 题目 4：Iterator Model & Instruction Cache

**来源**: [Fall 2022 HW3 Q3(d)](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-clean.pdf) [6 points]

!!! question "The iterator processing model often leads to good code locality (in the instruction cache sense)."
    中文翻译：迭代器处理模型是否能带来良好的代码局部性（从指令缓存的角度）？

=== "选项"
    - [ ] A. True
    - [ ] B. False

=== "答案与解析"
    **B. False**

    > Iterators are typically implemented in a generic way. For example, processing a tuple may involve calling another function to first interpret the tuple's contents, and the Next() function itself is usually virtual or invoked by a function pointer. This results in frequent long jumps, which leads to poor code locality.
    >
    > — CMU 15-445/645 Fall 2022 HW3 Solutions

    中文解析：迭代器模型中，每次只处理一个 tuple 就在不同算子之间切换，导致 CPU 在不同代码段之间频繁跳转，指令缓存命中率低。

### 题目 5：Index Scan vs. Sequential Scan

**来源**: [Fall 2022 HW3 Q3(e)](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-clean.pdf) [6 points]

!!! question "An index scan is always better (fewer I/O operations, faster run-time) than a sequential scan, regardless of the processing model."
    中文翻译：索引扫描是否总是比顺序扫描更好（更少 I/O、更快运行时间），无论使用什么处理模型？

=== "选项"
    - [ ] A. True
    - [ ] B. False

=== "答案与解析"
    **B. False**

    > An index scan may require multiple I/O operations (look up the row in the index, look up the row in the heap) whereas a sequential scan will just go through the heap. Moreover, a sequential scan may benefit more from pre-fetching pages. PostgreSQL's optimizer defaults to picking sequential scans over index scans if it thinks that you're asking for more than (very approximately) 10% of all rows in the table.
    >
    > — CMU 15-445/645 Fall 2022 HW3 Solutions

    中文解析：如果查询需要访问表中大部分数据，顺序扫描的顺序 I/O 可能比索引扫描的随机 I/O 更快。PostgreSQL 优化器在估计查询超过约 10% 的表行时会默认选择顺序扫描。

### 题目 6：Pipeline Breaker Identification

**来源**: 基于 Lecture #13 & #14 课程内容编写

!!! question "For the following query plan, which operators are pipeline breakers?"
    中文翻译：对于以下查询计划，哪些算子是 pipeline breaker？

    ```text
             Sort (ORDER BY R.value)
                      |
                  Hash Join
                 /         \
            Scan(R)      Scan(S)
    ```

??? success "答案"
    **Sort** and the **Hash Join's Build Side** are both pipeline breakers.

    - Sort must see all inputs before determining the final order — it cannot produce output early.
    - Hash Join's Build Side (Scan(R) → build hash table) must complete the hash table before the Probe phase can begin.

    中文解析：Sort 必须在看到所有输入后才能确定排序顺序，无法提前输出。Hash Join 的 Build Side 必须在哈希表完全构建后才能开始 Probe。

### 题目 7：Exchange Operator

**来源**: 基于 Lecture #14 课程内容编写

!!! question "What is the primary function of the Exchange operator in parallel query execution?"
    中文翻译：在并行查询执行中，Exchange 算子的主要功能是什么？

??? success "答案"
    The Exchange operator acts as a **synchronization barrier** in parallel execution. It collects outputs from all parallel workers and waits for all sub-tasks to complete before passing results to upper operators. This ensures operations like Hash Join don't start the Probe phase until all parallel partitions are complete, avoiding false negatives.

    中文解析：Exchange 算子充当并行执行的同步屏障（Barrier）。它收集所有并行 Worker 的输出，等待所有子任务完成后才将结果传递给上层算子。

### 题目 8：Processing Model & Workload Matching

**来源**: 基于 Lecture #13 课程内容编写

!!! question "Match each scenario with the most suitable processing model:"
    中文翻译：将以下场景与最适合的处理模型匹配：
    1. OLTP 系统处理点查询
    2. OLAP 系统对 TB 级数据做聚合分析
    3. 嵌入式数据库在移动设备上处理小规模查询

    1. An OLTP system handling point queries (e.g., `SELECT * FROM users WHERE id = 42`)
    2. An OLAP system performing aggregation analysis on TB-scale data
    3. An embedded database processing small queries on a mobile device

??? success "答案"
    1. **Iterator Model** or **Materialization Model** — OLTP point queries typically return few tuples; per-tuple processing is efficient, and materialization overhead is minimal for small outputs.
    2. **Vectorized Model** — OLAP analyzes massive data; vectorized processing enables SIMD acceleration and high throughput via batch processing.
    3. **Materialization Model** — Small-scale query outputs are typically modest, making materialization overhead manageable.

### 题目 9：Parallelism Strategy

**来源**: 基于 Lecture #14 课程内容编写

!!! question "Which parallelism strategy replicates the same operator across multiple workers, with each worker processing a different subset of data?"
    中文翻译：以下哪种并行策略是将同一个算子复制到多个 Worker，每个 Worker 处理不同的数据子集？

=== "选项"
    - [ ] A. Inter-Operator Parallelism
    - [ ] B. Intra-Operator Parallelism
    - [ ] C. Bushy Parallelism

=== "答案与解析"
    **B. Intra-Operator Parallelism**

    This strategy (also called horizontal parallelism) partitions the data so that multiple instances of the same operator process their respective data partitions in parallel.

    中文解析：算子内并行 / 水平并行。这种策略将数据分区，同一个算子的多个实例并行处理各自的数据分区。

### 题目 10：Process Model History

**来源**: 基于 Lecture #14 课程内容编写

!!! question "Why do legacy database systems like PostgreSQL and Oracle use Process per Worker instead of Thread per Worker?"
    中文翻译：为什么 PostgreSQL、Oracle 等老牌数据库使用 Process per Worker 而不是 Thread per Worker？

??? success "答案"
    These systems originated in the 1980s–1990s, when thread libraries across Unix variants (HP-UX, AIX, Solaris) were mutually incompatible. The `fork()` system call, as a POSIX standard interface, was universally available across all platforms, making Process per Worker the portable choice. Modern systems (past 20 years) generally adopt Thread per Worker since POSIX threads (pthreads) have been standardized.

    中文解析：因为这些系统起源于 1980-1990 年代，当时各 Unix 变体的线程库互不兼容。`fork()` 作为 POSIX 标准接口在所有系统上都可用，因此选择 Process per Worker 可以保证跨平台兼容性。

## 9 知识图谱总结

```text
Query Execution
├── Processing Model（数据传递方式）
│   ├── Iterator Model（1 tuple/次）— Volcano/Pipeline — OLTP 主流
│   ├── Materialization Model（全部 tuple/次）— 早期 OLAP
│   └── Vectorized Model（batch tuple/次）— 现代 OLAP 主流
│
├── Process Model（Worker 组织方式）
│   ├── Process per Worker — 老系统（PG, Oracle）
│   ├── Thread per Worker — 现代主流（MySQL, SQL Server）
│   └── Embedded DBMS — SQLite, DuckDB
│
├── Parallelism（并行策略）
│   ├── Inter-Query（查询间并行）— 多查询并发
│   └── Intra-Query（查询内并行）
│       ├── Intra-Operator（水平并行）— 数据分区 + Exchange
│       ├── Inter-Operator（垂直并行）— 不同 pipeline 并行
│       └── Bushy（丛生并行）— 组合
│
└── I/O Parallelism（存储并行）
    └── 多设备数据划分（Round-Robin / Hash / Range）
```

## 10 关键术语对照表

| 英文术语 | 中文翻译 | 简要说明 |
|---------|---------|---------|
| Query Plan | 查询计划 | SQL 经优化器转换后的算子树/DAG |
| Operator | 算子 | 查询计划中的基本执行单元 |
| Pipeline | 流水线 | 数据无需中断即可连续通过的一组算子 |
| Pipeline Breaker | 流水线断点 | 必须等待所有数据到齐才能继续的算子 |
| Iterator Model | 迭代器模型 | 每次传递一个 tuple 的处理模型 |
| Volcano Model | 火山模型 | 迭代器模型的别称，源自 Graefe 的论文 |
| Materialization Model | 物化模型 | 每次传递所有 tuple 的处理模型 |
| Vectorized Model | 向量化模型 | 每次传递一批 tuple 的处理模型 |
| Operator Fusion | 算子融合 | 将同一 pipeline 中的算子合并执行 |
| Exchange Operator | 交换算子 | 并行执行中的同步屏障 |
| Worker | 工作单元 | 执行查询的计算单元（线程/进程） |
| Intra-Query Parallelism | 查询内并行 | 单个查询被拆分到多个 Worker 执行 |
| Inter-Query Parallelism | 查询间并行 | 多个查询同时执行 |
| SIMD | 单指令多数据 | CPU 向量指令，可并行处理多个数据 |

---

## 参考资料

- CMU 15-445/645 Lecture #13 - Query Execution Part 1: [YouTube](https://www.youtube.com/watch?v=HNtlew7mCc4) | [Slides (Fall 2022)](https://15445.courses.cs.cmu.edu/fall2022/slides/12-queryexecution1.pdf)
- CMU 15-445/645 Lecture #14 - Query Execution Part 2: [YouTube](https://www.youtube.com/watch?v=E-UUd6cB57w)
- CMU 15-445/645 Lecture Notes (Spring 2024): [PDF](https://15445.courses.cs.cmu.edu/spring2024/notes/13-queryexecution1.pdf)
- CMU 15-445/645 Fall 2022 Homework #3 (含 Query Execution 题目): [Homework](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-clean.pdf) | [Solutions](https://15445.courses.cs.cmu.edu/fall2022/files/hw3-sols.pdf)
- CMU 15-445/645 Fall 2024 Final Exam Guide: [Link](https://15445.courses.cs.cmu.edu/fall2024/final-guide.html)
- Goetz Graefe, "Volcano—An Extensible and Parallel Query Evaluation System": [PDF](https://cs-people.bu.edu/mathan/reading-groups/papers-classics/volcano.pdf)
- Query Processing Notes (GitBook): [Link](https://zhenghe.gitbook.io/open-courses/cmu-15-445-645-database-systems/query-processing)
- Georgia Tech Query Execution Slides: [PDF](https://faculty.cc.gatech.edu/~jarulraj/courses/4420-f20/slides/21-query-execution-1.pdf)
