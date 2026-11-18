# 多变量 PDE 200条：去参数与显式函数版本

当前使用：`equations.jsonl`（可计算AST与来源），`FORMULAS.md`（逐条公式），`index.csv`（索引），`validation.json`（核验统计），`revision_map.jsonl`（与旧版200条对应）。

## 处理规则

- 从原始论文源码中的方程和上下文确认未知场与系数。各系统内统一未知场u/v/w/p，保留原始表达和映射。
- 标量乘法系数表达式整体规范化为单位幅值，保留原式的正负号。不是把每个参数逐个代1；例如(1-gamma)作为一个整体系数，不使其微分项意外消失。
- 非线性场幂次、分母中的场、乘积中的场和导数阶数保留。未知的参数指数不擅自指定数值，相关记录更换。
- f(u,v)、chi(v)、D(u)等场依赖函数不能当成常数系数删除。论文明确给出反应项时展开，否则剔除或更换。
- 原例1的论文0812.4623明确给出Gierer–Meinhardt和Lengyel–Epstein两套反应项；已按原文分别展开。两者是原文定义的不同模型，不是任意函数填充。
- 原例2的四场病毒治疗模型保留，去除mu、D等系数后逐项比对通过。
- 不明外力、控制函数、压力或额外状态变量不当作常系数抹去；相关记录更换。
- 两条热弹性记录只保留原文完整闭合的耦合子系统，省略的独立波动方程不提供任何闭合或强迫，记录中保留这一说明。

## 检查

200条均通过源码档案哈希、成员哈希和公式位置重验；无未绑定参数、无未知函数。各式提供残差AST，可在给定场与物理坐标上直接求值。两组平滑正场数值探针全部有限；导出LaTeX重新解析与AST符号残差一致。

去系数后重新进行了微分展开、时间导数主系数归一及符号残差去重，保留200个不同残差系统。这是语料结构的规范化版本，不复现原论文参数下的物理轨迹。分母非零、对数正值等数学定义域要求依然适用。数值探针通过不表示任何初边值问题都稳定或可解。

## 300词表

`tokenizer300.json`和对应backend文件是新语料的compact AST-BPE；总ID300=38个初始字符+3个控制符+259个合并词条。按论文来源分组，178条训练、22条验证；合并训练不使用验证记录。`initial_vocabulary.json`和`vocabulary300.json`提供可读词表。

## 重建

使用当前工作区的Python依赖运行：

```sh
python ast_bpe_multifield_v2/audit_coefficient_free_pool.py
python ast_bpe_multifield_v2/expand_explicit_reactions.py
python ast_bpe_multifield_v2/validate_coefficient_free.py
python ast_bpe_multifield_v2/export_coefficient_free200.py
python ast_bpe_multifield_v2/verify_coefficient_free.py
python ast_bpe_multifield_v2/prepare_coefficient_free300.py
```
