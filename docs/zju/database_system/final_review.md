# 数据库系统期末总复习

> 浙江大学《数据库系统》期末复习课录音整理。本文按考试安排、复习策略和章节知识点重排；具体通知以课程群、教务系统和 PPT 为准。

!!! tip "使用方式"
    先看考试与提交安排，再按章节清单回到 PPT、教材、quiz 和作业定位原题。A4 纸只适合放公式和易混规则，不能替代理解。

## 1 考试与提交安排

| 项目 | 内容 |
|------|------|
| 考试时间 | 7 月 2 日 8:00-10:00 |
| 考试地点 | 紫金港东教学楼 EA205 |
| 试卷语言 | 英文卷；答题可用中文或英文 |
| 题型 | 选择题、判断题、填空题 |
| 计算题 | 大计算题大概率不单独出，但代价估算、SQL 片段、算法字段可能放入填空或选择 |
| 范围 | 不超出 PPT 与教材范围 |
| 携带材料 | 可带一张 A4 纸，正反面可写；建议手写 |
| 平时材料 deadline | 7 月 1 日 24:00 |
| MiniSQL 验收 | 周四 8:00 开始，地点以课程群通知为准 |

!!! warning "卷面底线"
    录音中出现“50 分/40 分”的混杂表述，随后明确强调卷面不到 40 分会影响通过。复习时按“卷面最低线非常重要”处理，不要只依赖平时成绩。

## 2 复习顺序

1. 完整过 PPT：概念、算法流程、数据结构字段、公式来源和适用场景都要理解。
2. 做完 5 个 quiz：每题都很典型，答案已上传 FTP；不要只背选项。
3. 回看作业与历年题：重点稳定，但今年也会加入新概念和新场景。
4. 对比同类方法：RAID level、文件组织、buffer 策略、selection 方法、join 方法、恢复策略等都适合考“场景 + 优缺点 + 代价”。
5. 最后整理 A4：优先放公式、判定规则、SQL 模板和容易混淆的结论。

## 3 历年题目考点分析

资料来源：[2018final.pdf](2018final.pdf)。该文件名保留为原始文件名，但内部实际包含多套历年卷、回忆卷与参考答案。图形题中的 B+ 树、Buffer Tree 图需要回到 PDF 原图练习。

### 3.1 PDF 内题目整理

| 卷面 | 大题结构 | 重点信号 |
|------|----------|----------|
| 2017-2018 | SQL/关系代数、ER、函数依赖与 BCNF、XML、B+ 树、查询处理、并发控制、ARIES | 校园卡场景贯穿 SQL、XML、代价估计；ARIES 考 redo 起点、undo 终点、DPT 和 CLR。 |
| 2018-2019 | Movie SQL、足球比赛 ER、BCNF、XML、B+ 树、BNLJ/INLJ、cascadeless 与 2PL、ARIES | “最高平均值”“所有用户评分都更高”这类聚合和全称查询是 SQL 高频模板。 |
| 2019-2020 | 软件项目 SQL、视频网站 ER、FD/BCNF、XML、B+ 树带 bucket、hash join、strict 2PL、fuzzy checkpoint | 查询处理开始强调 buffer 数、hash join 是否递归分区，以及 checkpoint 时间线。 |
| 2020-2021 | SRTP SQL 建表、ER specialization、FD/BCNF、XML、B+ 树与 primary index、hash join、2PL lock conversion、logical undo | 建表约束、继承/分类实体、recoverable 条件和 logical undo 需要会解释。 |
| 2022-2023 及整理卷 | 选择题/判断题、SQL、数据库设计、并发控制、ARIES、Buffer Tree、LSM Tree | 题型更碎，覆盖存储、索引、外部排序、hash join、死锁、Buffer Tree 与 LSM Tree。 |

### 3.2 高频考点与复习优先级

1. **SQL 与关系代数**：每套卷都考，重点是自连接、`GROUP BY/HAVING`、`>= all`、`not exists`、`distinct`、外键级联、`check` 约束和建表语句。看到“最多/最高”优先想到聚合子查询，看到“所有/每个”优先想到全称查询或反例消除。
2. **ER 与关系模式转换**：常见场景包括外卖、足球、视频平台、SRTP、旅游平台、会议系统。画图时先找实体，再找联系的基数、联系属性、多值属性、弱实体或 specialization，最后转换为 schema 并标主键、外键。
3. **函数依赖与范式**：几乎固定考 candidate key、canonical cover、BCNF decomposition 和 dependency preserving。解题顺序是先算属性闭包，再化简依赖，最后按违反 BCNF 的依赖逐步分解。
4. **索引与 B+ 树**：插入、删除、节点分裂/合并、树高估计、dense/sparse、primary/secondary、clustering/non-clustering、bucket 和 LRU 缓冲读块数都出现过。近年还加入 Buffer Tree、LSM Tree，要会说明“延迟写入、顺序 I/O、合并代价”。
5. **查询处理代价**：稳定考 selectivity、block 数、B+ 树高度、index scan、block nested-loop join、indexed nested-loop join、hash join、external merge sort。答案通常要同时给 block transfers 和 seeks。
6. **并发控制**：核心是 precedence graph 判 conflict serializable，再判断 2PL、strict 2PL、cascadeless、recoverable、deadlock。不要只写结论，要指出环或等待关系。
7. **恢复系统**：ARIES 每年都很像，必须熟练 Analysis 重建 transaction table/DPT、Redo 从最小 `recLSN` 开始、Undo loser transactions、写 CLR。fuzzy checkpoint 和 logical undo 是旧卷中较难的变体。
8. **XML/XPath/XQuery**：2017-2021 连续出现，近年回忆卷中权重下降。若今年 PPT 仍包含 XML，至少会写 DTD、`ID/IDREF(S)`、`id()` 路径跳转和简单 XQuery join。

!!! tip "做历年题的顺序"
    先独立完成 SQL、FD、B+ 树、查询代价、并发图和 ARIES 六类题，再对答案。ER/XML 可以按模板整理，但 ARIES 和代价估计一定要手算一遍，因为评分细则通常按中间步骤给分。

!!! warning "复习取舍"
    历年题说明恢复、并发、索引和查询处理非常稳定；Buffer Tree、LSM Tree、列存储、外部排序、稀疏/稠密索引等更像近年选择题考点，适合放进 A4 纸的“易混判断”区。

## 4 章节复习清单

### SQL 与 Advanced SQL

- 掌握 `CREATE TABLE`、`SELECT`、`UPDATE`、`DELETE` 的基本格式。
- 熟悉数据类型：`char`、`int`、`date/time`、`BLOB`、`CLOB` 等。
- 完整性约束：`PRIMARY KEY`、`FOREIGN KEY`、`UNIQUE`、`NOT NULL`、`CHECK`。
- key 概念：super key、candidate key、primary key、foreign key。
- 外键动作：`ON DELETE CASCADE`、`ON UPDATE CASCADE` 等。
- 授权：`GRANT`、`REVOKE`、`WITH GRANT OPTION`、角色、view 权限。
- 聚合函数：`COUNT`、`MAX`、`MIN`、`AVG`、`SUM`。
- 区分 `WHERE` 与 `HAVING`：涉及聚合结果的过滤放在 `HAVING`。
- 能读懂长 SQL，判断 `FROM`、`WHERE`、`GROUP BY`、`HAVING`、`ORDER BY` 是否符合查询需求。
- 全称条件常用 `NOT EXISTS` 或 `EXCEPT` 表达“没有反例”，不能简单改成局部比较。

!!! example "高频题型"
    求最低平均评分电影的 director：按 movie 分组求 `AVG(grade)`，再用 `HAVING` 做聚合比较。  
    找至少重修三门不同课程的学生：`GROUP BY` + `COUNT` + `HAVING`。

### ER Model

- 会判断实体、关系、属性，以及一对一、一对多、多对一、多对多。
- 属性类型：simple/composite、single-valued/multivalued、derived attribute。
- 弱实体依赖强实体存在，主键通常由 partial key 与强实体主键组合。
- 区分 total participation 与 partial participation，注意 ER 图中的双线。
- ER 转 relational schema：
  - 多对多关系通常转成单独关系表。
  - 一对多关系可合并到“多端”实体表。
  - 关系带属性时，转表时不要漏掉该属性。
  - 弱实体转换时要带上所依赖强实体的主键。

### 关系模式设计与范式

- 给定 schema 和函数依赖，能用属性闭包求 candidate key。
- 掌握 Armstrong 公理及其推论，理解 `F+` 的含义。
- canonical cover/minimal cover：删除冗余属性和冗余依赖，必要时合并左端相同的依赖。
- 会判断 1NF、2NF、3NF、BCNF。
- 分解题关注三件事：lossless join、dependency preserving、是否满足目标范式。
- BCNF 分解按违反 BCNF 的函数依赖逐步分解；两个属性的关系通常满足 BCNF。

!!! note "易混结论"
    3NF 综合分解通常可同时做到无损连接和依赖保持；BCNF 分解可做到无损连接，但不一定依赖保持。若 PPT 有不同表述，以课程材料为准。

### Storage 与文件组织

- 存储层次：primary storage、secondary storage、tertiary storage。
- 磁盘访问时间按 seek time、rotational latency、transfer time 理解。
- DBMS 在磁盘和内存之间通常以 block 为单位传输数据。
- RAID 0-5 的冗余方式、性能特点和适用场景要能比较；RAID 1 是镜像，适合坏盘后不中断访问。
- record 存储：
  - fixed-length records。
  - variable-length records：offset、length、实际数据。
  - slotted page header 中记录数量、空闲空间位置等字段。
  - fixed-length record 删除方法和 free list 维护。
- 文件组织：heap file、sequential file、hashing file、clustering file / multitable clustering。
- buffer management：hit/miss、LRU、MRU、pinned block、pin count、toss-immediate strategy、forced output。

### Indexing

- B+ 树是索引部分最重要考点，重点练插入、删除、高度、节点数量和查询代价。
- 插入时先放入叶节点，溢出后分裂；内部节点和根节点可能递归分裂。
- 删除时可能向兄弟节点借 key，也可能合并；内部节点 separator key 可能要更新为右子树最小值。
- B+ 树高度估计：
  - 节点尽量满时高度最小。
  - 节点刚满足最低占用时高度最大。
  - 内部节点最大 fanout `n` 满足 `(n - 1)K + nP <= B`。
- 查询代价要区分索引 block 与数据 block；范围扫描中后续连续数据块通常增加 transfer，不一定增加 seek。
- 区分 primary index 与 secondary index，以及主键/非主键检索代价。
- LSM Tree 适合高写入吞吐场景；也要了解 hash index、ISAM、buffer tree、learning index 的基本机制和适用场景。

### Query Processing

- 查询处理流程：SQL 输入、parser/translator、relational algebra expression、optimizer、execution plan、execution engine。
- selection operation 方法：linear scan、binary search、primary index、secondary index。
- external merge sort：初始 run、归并轮数、block transfer、seek 数都可能考。
- join 算法：
  - nested-loop join。
  - block nested-loop join。
  - indexed nested-loop join。
  - merge join。
  - hash join。
- 每种 join 都要知道适用场景和代价公式。
- materialization 与 pipelining 要比较优缺点。
- hash join 的 transfer/seek 公式要核对教材，注意是否计入构造 hash partitions 的代价。

### Query Optimization

- 优化目标：找到等价 relational algebra expression，并选择估算代价更低的计划。
- 熟悉选择、投影、并、交、差、连接等操作的等价变换规则。
- 长表达式可画 expression tree 辅助判断是否等价。
- cardinality estimation / selectivity：
  - 等值选择可用 `|r| / V(A, r)` 估计。
  - 范围选择按取值区间比例估计。
  - 复合条件要会组合选择率。
- tuple 数、block 数和 selectivity 是后续代价估计的基础。

### Transaction 与 Concurrency Control

- transaction 的 ACID：Atomicity、Consistency、Isolation、Durability。
- schedule 概念：serializable、conflict serializable、view serializable、recoverable、cascadeless。
- conflict serializable 是 serializable 的子集；“serializable 一定 conflict serializable”是错的。
- conflict serializability 判定：
  - 找同一数据项上的冲突操作，且至少一个是 write。
  - 建 precedence graph。
  - 图中有环则不是 conflict serializable；无环则是。
- cascading rollback：事务读到另一个未提交事务写出的值，可能随后者失败级联回滚。
- 2PL / two-phase locking：理解 growing phase 和 shrinking phase，以及 basic 2PL、strict 2PL 等协议分别保证什么性质。
- shared lock 是读锁，exclusive lock 是写锁/排他锁。
- deadlock 用 wait-for graph 判断；还要会说明检测、解决和预防。
- starvation 指事务长期得不到资源，可通过 timeout 等机制缓解。

### Recovery System

- failure 类型：transaction failure、system crash、disk failure。
- log-based recovery：理解 WAL、UNDO、REDO。
- deferred database modification 与 immediate database modification 的流程和日志记录。
- database buffering policy：steal/no-steal、force/no-force。
- checkpoint 的作用是减少恢复时需要扫描的日志，并辅助判断哪些事务需要 UNDO/REDO。
- ARIES 是重要考点：
  - analysis：重建 transaction table 和 dirty page table。
  - redo：从合适的 `recLSN` 开始重复历史。
  - undo：撤销 loser transactions。
  - 重点字段：LSN、prevLSN、recLSN、transaction table、dirty page table、CLR。
- CLR 是 compensation log record，用于记录撤销操作，保证恢复过程中再次崩溃也能正确继续。

## 5 A4 纸建议内容

- SQL：`SELECT` 执行顺序、`GROUP BY/HAVING`、建表约束、外键级联、授权语句。
- ER：关系基数、全/部分参与、弱实体、ER 转关系模式规则。
- 函数依赖：Armstrong 公理、属性闭包、candidate key、canonical cover、lossless/dependency preserving、3NF/BCNF 结论。
- Storage：RAID 对比、存储层次、block/sector、record 组织、slotted page、buffer 策略、文件组织方式。
- Index：B+ 树插入删除规则、fanout/高度公式、primary/secondary index 代价。
- Query：selection/sort/join 代价公式、external merge sort、hash join 注意点、selectivity/cardinality estimation。
- Concurrency：ACID、调度性质、precedence graph、2PL、锁兼容、deadlock/starvation。
- Recovery：WAL、UNDO/REDO、deferred/immediate、checkpoint、ARIES 三阶段和关键字段。

## 6 时间线摘要

| 时间段 | 内容 |
|--------|------|
| 00:10-07:55 | 主讲老师说明考试时间地点、提交 deadline、A4 纸规则 |
| 07:55-11:23 | SQL 与 Advanced SQL 复习范围 |
| 11:28-14:51 | ER Model 复习范围 |
| 15:04-16:59 | 关系规范化、candidate key、canonical cover、分解 |
| 17:06-20:07 | Storage、RAID、buffer、文件组织 |
| 20:18-22:24 | B+ 树、索引、LSM Tree、learning index |
| 22:24-24:26 | Query Processing 与 Query Optimization |
| 24:35-28:47 | Transaction、Concurrency、Recovery |
| 34:00-48:13 | 助教串讲 SQL 题 |
| 52:06-70:30 | 助教串讲 SQL 细节与 ER Model |
| 70:41-86:48 | 助教串讲函数依赖、范式与分解 |
| 87:14-105:52 | 助教串讲 Storage |
| 105:53-121:49 | 助教串讲 Indexing 与 B+ 树 |
| 122:06-130:05 | 助教串讲 Query Processing 与 Optimization |
| 130:16-137:50 | 助教串讲 Transaction 与 Concurrency |
| 138:37-144:00 | 助教串讲 Recovery 与 ARIES |

## 7 相关站内笔记

- [Query Execution](../../cmu_15_445/query_execution.md)
- [Database Logging](../../cmu_15_445/data_logging.md)
- [Recovery with ARIES](../../cmu_15_445/recovery_with_aries.md)
