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

Shadow Paging 采用 No-Steal + Force。系统维护两个 page table：

- **Master Page Table**：只指向已提交版本。
- **Shadow Page Table**：事务修改时通过 copy-on-write 复制页面，并把新版本挂到 shadow table。

提交时，系统先把 shadow pages 刷盘，再原子地切换 master pointer。回滚时直接丢弃 shadow table。

| 优点 | 缺点 |
|------|------|
| 回滚和恢复简单 | 复制 page table 和脏页开销高 |
| 不需要复杂日志 | 提交时必须刷出所有修改 |
| 崩溃后只需看 master pointer | 会造成磁盘碎片，不利于顺序扫描 |
| 适合单写者场景 | 多事务并发提交难处理 |

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

1. 暂停或协调事务。
2. 把 log buffer 刷到磁盘。
3. 把 dirty pages 刷到磁盘。
4. 在 WAL 中写入 checkpoint record。
5. 恢复时从最近 checkpoint 附近开始分析。

最简单的 consistent checkpoint 会暂停所有事务，恢复逻辑简单但运行时影响大。Checkpoint 太频繁会拖慢正常请求；太少则会延长崩溃恢复时间。下一讲的 fuzzy checkpoint 通过记录 Active Transaction Table 和 Dirty Page Table，避免长时间 stop-the-world。

## 7 WAL 的额外用途

WAL 不只用于恢复，也常用于 **Change Data Capture (CDC)** 和复制。系统可以把 WAL 发送到 Kafka、数据仓库或备库，由下游按顺序重放变更。这类机制复用了数据库为恢复已经生成的变更流。

## 8 小结

WAL + Steal + No-Force 是现代数据库的主流选择：运行时可以灵活回收 buffer pool 页面，提交时只需顺序刷日志；代价是崩溃后必须同时支持 REDO 和 UNDO。Checkpoint 则用于限制恢复要扫描的日志范围。
