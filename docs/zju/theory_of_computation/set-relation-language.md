# Ch1 . Set, Relation, and Language

>离散数学复习课

## Set

- 集合
    - 元素不重复，且顺序无关
- 集合运算
    - 交 (intersection)：$A \cap B = \{x \mid x \in A \land x \in B\}$
    - 并 (union)：$A \cup B = \{x \mid x \in A \lor x \in B\}$
    - 差 (difference)：$A - B = A \setminus B = \{x \mid x \in A \land x \notin B\}$
    - 补 (complement)：$\overline{A} = U - A$，其中 $U$ 为全集

- 集合的性质
    - Idempotent Law（幂等律）：$A \cup A = A$ ；$A \cap A = A$
    - Commutative Law（交换律）：$A \cup B = B \cup A$ ；$A \cap B = B \cap A$
    - Associative Law（结合律）：$(A \cup B) \cup C = A \cup (B \cup C)$ ；$(A \cap B) \cap C = A \cap (B \cap C)$
    - Distributive Law（分配律）：$A \cap (B \cup C) = (A \cap B) \cup (A \cap C)$ ；$A \cup (B \cap C) = (A \cup B) \cap (A \cup C)$
    - Absorption Law（吸收律）：$A \cup (A \cap B) = A$ ；$A \cap (A \cup B) = A$
    - De Morgan's Law（德摩根律）：$\overline{A \cup B} = \overline{A} \cap \overline{B}$ ；$\overline{A \cap B} = \overline{A} \cup \overline{B}$

!!! tip Why some problems can be solved by employing computational models ?
     - Problem <--> Sets or Languages
     - Automated solution <--> Problem can be Identified <--> The problem is computable

- Power Set (幂集)：$2^A = \{S \mid S \subseteq A\}$；若 $|A| = n$，则 $|2^A| = 2^n$
- Partition（划分）：由 $A$ 的一族非空子集 $\Pi = \{S_1, S_2, \ldots\}$ 构成，满足
    - $S_i \neq \emptyset$（各部分非空）
    - $S_i \cap S_j = \emptyset,\ \forall i \neq j$（两两不交）
    - $\bigcup_i S_i = A$（并起来覆盖全集）

## Relations and Functions

- Ordered Pair（有序对）：$(a, b)$，满足 $(a,b) = (c,d) \iff a = c \land b = d$

- Binary Relation
    - Cartesian Product（笛卡尔积）：$A \times B = \{(a,b) \mid a \in A \land b \in B\}$
    - Binary Relation（二元关系）：$A \times B$ 的一个子集 $R \subseteq A \times B$，记作 $a R b \iff (a,b) \in R$

- Operations of Relations
    - inverse（逆关系）：$R^{-1} = \{(b,a) \mid (a,b) \in R\}$

    - Composition（复合）：若 $R \subseteq A \times B,\ S \subseteq B \times C$，则
      $$S \circ R = \{(a,c) \mid \exists b \in B,\ (a,b) \in R \land (b,c) \in S\}$$

    - ordered tuple

    - sequence

    - n-folds Cartesian product

    - n-ary relation


- Fuction
    - Def

    - Note

    - One-to-one

    - onto

    - One-to-one correspondence
        - one-to-one + onto

!!! tip memorize with figure
    // zcode 请帮我补全


## Special Types of Binary Relations

- Directed Graph

- Matrix

    - R can be represented by the logical matrix M whose row and column idices idnex the elements of logical 0 and 1

