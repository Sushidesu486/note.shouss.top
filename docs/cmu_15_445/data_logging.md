# Database Logging 学习笔记

> CMU 15-445/645 Intro to Database Systems — Recovery I: Database Logging

!!! tip "关于本笔记"
    本讲解释数据库系统在**正常运行时**需要额外记录什么信息，才能在崩溃后恢复到正确状态。下一讲的 ARIES 会使用这里介绍的 WAL、LSN、Checkpoint 等机制完成真正的恢复流程。

## 1 恢复问题

数据库通常采用 disk-oriented 架构：页面从非易失存储读入 buffer pool，在内存中修改，再异步写回磁盘。问题在于内存会在崩溃时丢失：

- 已提交事务的修改可能只在内存中，违反 **Durability**。
- 未提交事务的部分修改可能已经写入磁盘，违反 **Atomicity**。

恢复算法包含两部分：

1. **正常运行时**：记录足够的日志和元数据，为崩溃恢复做准备。
2. **崩溃后**：根据日志判断哪些修改需要重做，哪些修改需要撤销。

### 1.1 UNDO 与 REDO

| 操作 | 目标 | 典型场景 |
|------|------|----------|
| UNDO | 移除未成功提交事务的影响 | 未提交事务的脏页已经落盘 |
| REDO | 重新应用已提交事务的影响 | 已提交事务的脏页尚未落盘 |

!!! info "核心判断"
    是否需要 UNDO/REDO，不取决于事务本身，而取决于 buffer pool 是否允许脏页提前落盘，以及提交时是否强制刷脏页。

## 2 Buffer Pool 策略

恢复复杂度由两组策略决定：

| 策略 | 含义 | 恢复影响 |
|------|------|----------|
| Steal | 允许未提交事务修改过的脏页被写回磁盘 | 需要 UNDO |
| No-Steal | 未提交事务修改过的脏页不能写回磁盘 | 不需要 UNDO |
| Force | 事务提交前必须把所有修改页写回磁盘 | 不需要 REDO |
| No-Force | 提交时只保证日志落盘，不强制刷所有数据页 | 需要 REDO |

组合结果：

| 组合 | 需要 UNDO | 需要 REDO | 特点 |
|------|-----------|-----------|------|
| No-Steal + Force | 否 | 否 | 恢复最简单，但运行时开销最大 |
| No-Steal + No-Force | 否 | 是 | 不能提前回收脏页 |
| Steal + Force | 是 | 否 | 提交慢，仍要处理未提交修改 |
| Steal + No-Force | 是 | 是 | 性能最好，现代系统常用 |

## 3 Shadow Paging

Shadow Paging 是 No-Steal + Force 的一种实现方式。它不依赖 WAL 来恢复页面，而是通过 copy-on-write 同时维护两个数据库版本：

- **Master Page Table**：只指向已提交版本。
- **Shadow Page Table**：事务修改时通过 copy-on-write 复制页面，并把新版本挂到 shadow table。

### 3.1 基本流程

1. 事务开始时，shadow page table 复制 master page table 的映射关系；此时两者都指向同一批物理页。
2. 当事务第一次修改某个页面时，DBMS 复制该页，修改复制后的页面，并让 shadow page table 指向新页。
3. 读事务仍通过 master page table 读取旧的已提交版本；写事务只修改 shadow 版本。
4. 事务提交时，DBMS 先把 shadow page table 和所有 shadow dirty pages 刷到磁盘。
5. 最后原子地切换 master pointer，使其指向 shadow page table。切换完成后，shadow 版本成为新的 master 版本。
6. 如果事务回滚，直接丢弃 shadow page table 和 shadow pages，master pointer 不变。

!!! info "为什么恢复简单"
    崩溃后只需要检查 master pointer。若提交时的原子切换已经完成，master 指向新版本；若没有完成，master 仍指向旧版本。因此不需要 REDO，也不需要对未提交事务执行 UNDO。

### 3.2 树状 page table

直接复制整张 page table 代价很高。实际实现通常把 page table 组织成树，根节点是固定位置上的一个小页面或根指针：

- master root 指向当前已提交数据库版本。
- shadow root 指向事务的临时版本。
- 修改叶子页时，只复制从根到该叶子的路径和被修改的数据页，不需要复制整棵树。
- 提交时的关键动作是把固定位置的 root 原子更新为 shadow root。

这种设计的本质是把“事务是否提交”压缩成一次 root 切换：root 切换前，所有 shadow 更新都不是数据库的正式状态；root 切换后，这些更新整体生效。

### 3.3 成本与局限

| 优点 | 缺点 |
|------|------|
| 回滚和恢复简单 | 复制 page table 和脏页开销高 |
| 不需要复杂日志 | 提交时必须刷出所有修改 |
| 崩溃后只需看 master pointer | 会造成磁盘碎片，不利于顺序扫描 |
| 适合单写者场景 | 多事务并发提交难处理 |

Shadow Paging 的提交开销集中在两件事上：刷出被修改的新页面，以及刷出 page table 或 root 相关页面。由于新页面往往分布在磁盘不同位置，它会破坏原本连续的数据布局，导致顺序扫描退化。旧版本页面还需要后续垃圾回收，否则空间会持续膨胀。

SQLite 早期的 rollback journal 与该思路相近：修改页面前先把原始页面写入 journal，崩溃后用 journal 把未完成事务的页面拷贝回去。

## 4 Write-Ahead Logging

现代数据库通常使用 **Write-Ahead Logging (WAL)**。WAL 把随机数据页写入转换成顺序日志追加：事务修改页面前先生成日志记录，提交时只需保证相关日志已写入非易失存储。

WAL 有两条关键规则：

1. 数据页写回磁盘前，必须先把该页对应的日志记录写入磁盘。
2. 事务返回 commit 成功前，必须先把该事务的所有日志记录和 commit record 写入磁盘。

典型日志记录包含：

```text
<txn_id, object_id/page_id, before_value, after_value>
```

其中 `before_value` 支持 UNDO，`after_value` 支持 REDO。真实系统还会记录 LSN、校验和、时间戳、页面偏移、slot 等信息。

!!! example "提交流程"
    `T1` 更新 `A` 和 `B` 时，系统先把两条 update log record 追加到 log buffer，再修改 buffer pool 中的页面。`T1` 提交时追加 commit record，并把日志刷到磁盘。即使数据页还没落盘，崩溃后也能通过 WAL 重放 `A` 和 `B` 的修改。

### 4.1 Group Commit

如果每个事务提交都单独 `fsync`，磁盘延迟会成为瓶颈。Group commit 会把多个事务在短时间窗口内的日志一起刷盘：

- 第一个事务可能多等几毫秒。
- 多个提交共享一次顺序写和一次 flush。
- 吞吐量提高，但提交延迟可能略微增加。

## 5 日志粒度

| 类型 | 记录内容 | 优点 | 缺点 |
|------|----------|------|------|
| Physical Logging | 页面/字节级 before/after image | 恢复确定，易重放 | 日志量大 |
| Logical Logging | 原始 SQL 或逻辑操作 | 日志量小 | 需要确定性重放，恢复可能很慢 |
| Physiological Logging | 指定 page，再记录 page 内逻辑位置或 slot | 折中，最常见 | 仍需维护页面级元数据 |

多数磁盘型 DBMS 采用 physiological logging：跨页面时保持物理定位，页面内部允许通过 slot array 等结构重新组织。

## 6 Checkpoint

WAL 不能无限增长，否则崩溃后可能要重放多年日志。**Checkpoint** 的作用是缩短恢复起点：

### 6.1 为什么需要 Checkpoint

如果没有 checkpoint，恢复时必须从日志开头扫描到崩溃点：

- 找出哪些事务已经提交，哪些事务没有完成。
- REDO 已提交但可能尚未落盘的修改。
- UNDO 未提交但可能已经落盘的修改。

长期运行的系统会产生大量 WAL。即使很多老事务的修改早已刷到数据页，恢复仍要重复扫描这些无用历史，恢复时间不可控。Checkpoint 的目标就是把“确定已经安全的历史”变成恢复时可以跳过的边界。

### 6.2 Consistent Checkpoint

最直接的方案是 consistent checkpoint，也就是阻塞式检查点：

1. 阻止新事务开始。
2. 等待当前活跃事务结束，或暂停所有事务更新。
3. 将 log buffer 刷入稳定存储。
4. 将 buffer pool 中所有 dirty pages 刷到磁盘。
5. 写入 checkpoint record，其中记录 checkpoint 时仍活跃的事务集合。
6. 允许事务继续执行。

如果某个事务在 checkpoint 之前已经提交或中止，并且它的脏页也已经在 checkpoint 中落盘，那么恢复时不需要再处理它。恢复只需要关注：

- checkpoint record 中仍活跃的事务。
- checkpoint 之后才开始的事务。

对于这些事务：

- 如果日志中没有 `COMMIT` 或 `ABORT`，崩溃恢复时需要 UNDO。
- 如果日志中有 `COMMIT` 或 `ABORT`，恢复时需要按日志 REDO，保证历史状态完整。

!!! example "日志截断边界"
    如果 checkpoint 记录中有活跃事务集合 `L`，那么早于 `L` 中最早事务 `BEGIN` 的历史日志通常不再参与恢复。系统可以在确认没有备份、复制或审计需求后回收这部分日志空间。

Consistent checkpoint 的问题是停顿时间不可控。只要有长事务未结束，checkpoint 就必须等待；如果系统强行暂停事务，在线请求会被阻塞。

### 6.3 Fuzzy Checkpoint

Fuzzy checkpoint 的目标是减少 stop-the-world 时间。它允许 checkpoint 进行时事务继续运行，但必须额外记录系统状态：

| 结构 | 记录内容 | 用途 |
|------|----------|------|
| Active Transaction Table (ATT) | 活跃事务、状态、最近日志位置 | 恢复时判断哪些事务需要提交完成或回滚 |
| Dirty Page Table (DPT) | 尚未落盘的脏页及其 `recLSN` | 恢复时确定 REDO 的最早起点 |

典型流程：

1. 写入 `BEGIN_CHECKPOINT`。
2. 快速复制当前 ATT 和 DPT 的快照。
3. 后台继续刷出 dirty pages；普通事务可以继续产生新日志和新脏页。
4. 写入 `END_CHECKPOINT`，其中包含 ATT/DPT 快照。
5. `END_CHECKPOINT` 安全落盘后，更新 master record，让它指向这次 checkpoint 的起点。

Fuzzy checkpoint 不保证磁盘上的数据页在 checkpoint 结束时形成一个完全一致的快照，因为 checkpoint 期间事务仍可能修改页面。因此恢复不能简单地从 checkpoint 后开始重放，而要利用 DPT 的 `recLSN` 找到可能最早未落盘的修改，再从那里开始 REDO。

!!! warning "WAL 约束仍然存在"
    即使是 fuzzy checkpoint，刷出某个 dirty page 之前，也必须先保证导致该页变脏的相关日志已经落盘。否则崩溃后无法判断该页上的修改应该保留还是撤销。

### 6.4 Checkpoint 频率

Checkpoint 是运行时开销和恢复时间之间的权衡：

- 太频繁：后台刷页和日志写入压力变大，正常事务吞吐下降。
- 太稀疏：WAL 变长，崩溃后需要扫描和重放更多日志。
- 长事务越多：日志截断越困难，因为必须保留能撤销这些事务的历史。

因此系统通常会结合日志大小、dirty page 数量、目标恢复时间和当前负载来决定 checkpoint 时机，而不是只依赖固定时间间隔。

## 7 WAL 的额外用途

WAL 不只用于恢复，也常用于 **Change Data Capture (CDC)** 和复制。系统可以把 WAL 发送到 Kafka、数据仓库或备库，由下游按顺序重放变更。这类机制复用了数据库为恢复已经生成的变更流。

## 8 小结

WAL + Steal + No-Force 是现代数据库的主流选择：运行时可以灵活回收 buffer pool 页面，提交时只需顺序刷日志；代价是崩溃后必须同时支持 REDO 和 UNDO。Checkpoint 则用于限制恢复要扫描的日志范围。

## 参考资料

- [NoughtQ：Lec 15: Recovery System](https://note.noughtq.top/sys/db/15)
