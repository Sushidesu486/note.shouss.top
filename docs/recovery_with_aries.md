# Recovery with ARIES 学习笔记

> CMU 15-445/645 Intro to Database Systems — Recovery II: ARIES

!!! tip "关于本笔记"
    本讲承接 Database Logging，说明系统崩溃后如何利用 WAL、LSN、Dirty Page Table 和 Active Transaction Table 恢复数据库。ARIES 的核心是：先重复历史，再撤销不该留下的修改。

## 1 ARIES 概述

**ARIES** 全称是 *Algorithms for Recovery and Isolation Exploiting Semantics*，是数据库崩溃恢复的经典算法。它假设系统使用：

- Steal + No-Force buffer pool policy。
- Write-Ahead Logging。
- 单版本事务模型，通常配合 strict 2PL 讨论。

ARIES 的三个核心思想：

1. **Write-Ahead Logging**：数据页落盘前，对应日志必须先落盘。
2. **Repeating History During Redo**：REDO 阶段重放崩溃前发生过的历史，包括后来要回滚的事务。
3. **Logging Changes During Undo**：UNDO 也写日志，使用 Compensation Log Record (CLR) 记录撤销进度。

## 2 LSN 与基础元数据

**Log Sequence Number (LSN)** 是日志记录的全局递增编号，用来表示日志顺序。

| 名称 | 含义 |
|------|------|
| `LSN` | 当前日志记录的编号 |
| `prevLSN` | 同一事务上一条日志记录，用于反向遍历 |
| `pageLSN` | 页面上最近一次修改对应的 LSN |
| `flushedLSN` | WAL 已经刷到磁盘的最大 LSN |
| `recLSN` | 某页变脏后第一条修改它的日志记录 |
| `lastLSN` | 某事务最近一条日志记录 |
| Master Record | 记录最近一次成功 checkpoint 的位置 |

页面能否写回磁盘的关键判断：

```text
pageLSN <= flushedLSN
```

如果 `pageLSN` 大于 `flushedLSN`，说明页面包含的某些修改还没有日志落盘，直接刷页会违反 WAL。

## 3 日志记录类型

| 类型 | 作用 |
|------|------|
| `BEGIN` | 事务开始 |
| `UPDATE` | 记录一次页面修改，包含 before/after image |
| `COMMIT` | 事务决定提交；刷到磁盘后可向客户端确认 |
| `ABORT` | 事务开始回滚 |
| `CLR` | 记录一次 UNDO 的补偿操作 |
| `END` | 事务彻底结束，可从内部表移除 |
| `BEGIN_CHECKPOINT` / `END_CHECKPOINT` | fuzzy checkpoint 的边界 |

`COMMIT` 和 `END` 不同：`COMMIT` 表示事务对外成功；`END` 是系统内部清理完成的标记。提交记录必须及时刷盘，`END` 可以随之后的日志批量刷出。

### 3.1 Compensation Log Record

CLR 是“撤销某条 update”的日志记录。它有两个特点：

- CLR 会在 REDO 阶段重放。
- CLR 不会再次被 UNDO。

CLR 中的 `undoNextLSN` 指向该事务下一条仍需撤销的日志记录。这样即使系统在 UNDO 过程中再次崩溃，下一次恢复也能跳过已经撤销过的部分。

## 4 内存表

ARIES 恢复过程中维护两张关键表：

| 表 | 内容 | 作用 |
|----|------|------|
| Active Transaction Table (ATT) | `txn_id -> status, lastLSN` | 找到崩溃时仍未结束的事务 |
| Dirty Page Table (DPT) | `page_id -> recLSN` | 找到可能没有刷盘的页面，以及 REDO 起点 |

事务状态通常包括：

- `RUNNING`：正常执行。
- `COMMITTING`：已经看到 commit，但还没看到 end。
- `RECOVERY_ABORTING`：恢复过程中需要回滚。
- `COMPLETE`：已经写入 end，可移出 ATT。

## 5 Fuzzy Checkpoint

阻塞式 checkpoint 会暂停事务，性能太差。ARIES 使用 **fuzzy checkpoint**：

1. 写入 `BEGIN_CHECKPOINT`。
2. 记录 checkpoint 开始时的 ATT 和 DPT。
3. 事务继续运行，checkpoint 后台完成。
4. 写入 `END_CHECKPOINT`，其中包含 ATT/DPT 快照。
5. `END_CHECKPOINT` 刷盘后，更新 master record 指向 `BEGIN_CHECKPOINT`。

Fuzzy checkpoint 不保证 checkpoint 期间页面完全静止，因此恢复时仍需从日志中分析 checkpoint 前后的变化。

## 6 三阶段恢复流程

### 6.1 Analysis

Analysis 从 master record 指向的最近 checkpoint 开始，向前扫描到日志末尾，重建 ATT 和 DPT。

主要规则：

- 遇到事务日志记录，把事务加入 ATT，并更新 `lastLSN`。
- 遇到 `UPDATE` 或 `CLR`，如果页面不在 DPT 中，加入并设置 `recLSN` 为当前 LSN。
- 遇到 `COMMIT`，把事务状态改为 `COMMITTING`。
- 遇到 `END`，从 ATT 中移除事务。
- 扫描结束后，仍在 ATT 中且未提交的事务是 **loser transactions**，需要 UNDO。
- 已提交但没有 `END` 的事务是 **winner transactions**，可补写 `END` 并移除。

Analysis 结束后：

- ATT 告诉系统哪些事务崩溃时还没结束。
- DPT 告诉系统哪些页面可能需要 REDO。

### 6.2 Redo

Redo 的目标是把数据库恢复到“崩溃瞬间”的状态。它从 DPT 中最小的 `recLSN` 开始向前扫描，并重放必要的 `UPDATE` 和 `CLR`。

对一条日志记录 `r`，只有满足以下条件才需要 redo：

1. `r` 修改的页面在 DPT 中。
2. `r.LSN >= DPT[page].recLSN`。
3. 从磁盘读入该页后，`pageLSN < r.LSN`。

如果 `pageLSN >= r.LSN`，说明该修改已经在磁盘页中，不需要重复应用。重放时直接应用 after image 或 CLR 的补偿修改，然后把页面的 `pageLSN` 设为 `r.LSN`。

!!! info "为什么要重复历史"
    ARIES 即使知道某个事务最终要回滚，也会先在 REDO 阶段重放它的修改。这样可以先还原崩溃时的完整状态，再由 UNDO 阶段按统一规则清理 loser transactions。

### 6.3 Undo

Undo 处理 Analysis 后仍留在 ATT 中的 loser transactions。系统通常维护一个按 LSN 倒序处理的集合 `ToUndo`：

1. 初始化为每个 loser transaction 的 `lastLSN`。
2. 取最大的 LSN，找到对应日志记录。
3. 如果是普通 `UPDATE`，应用 before image 反向修改页面，并写入 CLR。
4. 如果该记录还有 `prevLSN`，把 `prevLSN` 加入 `ToUndo`；否则写入 `END`。
5. 如果遇到 CLR，沿 `undoNextLSN` 继续跳转，不再撤销 CLR 本身。

UNDO 每撤销一步就追加 CLR，因此恢复过程可以重复崩溃。下一次 REDO 会重放已经写出的 CLR，新的 UNDO 只需要从尚未完成的位置继续。

## 7 恢复中再次崩溃

| 崩溃位置 | 处理方式 |
|----------|----------|
| Analysis 中崩溃 | 不需要特殊处理，重新开始恢复 |
| Redo 中崩溃 | Redo 是幂等的，重新开始即可 |
| Undo 中崩溃 | 已写出的 CLR 会在下一次 Redo 中重放，Undo 继续剩余部分 |

这就是 CLR 的价值：它让系统能够记录“已经撤销到哪里”，避免每次崩溃后从头回滚同一批修改。

## 8 小结

ARIES 把崩溃恢复拆成清晰的三步：Analysis 先弄清崩溃时系统状态，Redo 重放历史到崩溃点，Undo 再清除 loser transactions。配合 WAL、LSN、fuzzy checkpoint、ATT、DPT 和 CLR，数据库可以在 Steal + No-Force 的高性能策略下仍然保证原子性和持久性。
