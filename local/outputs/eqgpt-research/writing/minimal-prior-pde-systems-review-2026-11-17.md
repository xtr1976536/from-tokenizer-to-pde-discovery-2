# 仅知道观测维数的 PDE 系统发现：第二轮定向调研

日期：2026-11-17。依据用户明确要求：不提供目标物理语义、具体物理项、对称性、守恒律、方程数量或演化/约束角色。本文件取代上一轮报告中的物理结构约束建议；上一轮报告保留作历史记录。未修改主实验，未启动服务器计算。

## 范围与证据

这是定向研究，不是穷尽性系统综述。搜索关键词包括 implicit PDE systems、unknown number of equations、null space、independent equations、identifiability、Seq-SVF、D-CIPHER、SINDy-PI。检索原始来源为出版社页面、会议论文和 arXiv。Seq-SVF 核对到出版社摘要、Problem setup/Method 等公开节选及 Crossref 元数据，尚未取得完整正文；其他重点工作的结论依据正文或明确指出的附录。没有依据本次检索宣称首创或不存在竞争方法。

## 结果矩阵

| 工作 | 相关机制 | 未满足愿景的边界 | 阅读优先级 |
|---|---|---|---|
| Seq-SVF，Wu et al., 2023 | SVD、强秩揭示 QR、列子集选择、逐次奇异值筛选；不预先指定方程数和左端项 | 仍需构建有限候选项/导数数据矩阵；完整闭合外推证据未核实 | 最高 |
| D-CIPHER，NeurIPS 2023 | 无需预设演化形式；弱式与符号搜索；讨论系统不确定性 | 导数相关部分受字典限制；系统例使用不同字典引导发现不同方程 | 最高，特别是 F.2 |
| SINDy-PI，2020 | 多个候选左端并行拟合隐式关系 | 预设库；不能据此认定未知数量的完整系统已解决 | 高 |
| Scholl et al., arXiv:2210.08342，2026 v10 | 不同函数类下的可辨识性、独立性与数值诊断 | 理论均相对于指定模型类；不是任意 PDE 系统恢复算法 | 最高 |
| He, Zhao & Zhong，FoCM 2024 | 解轨迹的信息量、局部回归与全局一致性 | 有特定算子/模型类假设 | 高 |
| Mechanistic PDE Networks，ICML 2025 | 将可微求解嵌入发现 | 二维实验只发现耦合系统的一条方程；NS 给定压力梯度 | 对照 |
| Symbolic Recovery of PDEs from Measurement Data，2026 v2 | 符号网络与函数空间重建、条件性唯一恢复 | 指定一阶时间演化；系统例选择各自拉普拉斯特征和架构 | 理论参考 |
| FoundPDE，2026-10 预印本 | 数据到符号预训练；时间阶数亦为输出 | 本文是一维单场规范 PDE 家族；未展示未知数量多变量隐式系统 | 生成模型对照 |

## 1. 最直接的相关工作：Seq-SVF

Zhetong Wu, Hongfei Ye, Hongwu Zhang, Yonggang Zheng. *Seq-SVF: An unsupervised data-driven method for automatically identifying hidden governing equations*. Computer Physics Communications 292 (2023), 108887. DOI: https://doi.org/10.1016/j.cpc.2023.108887 。出版社：https://www.sciencedirect.com/science/article/abs/pii/S0010465523002321 。正式出版信息已用 Crossref 核实；另有不同 DOI 的 SSRN 预印本，不应混为正式论文 DOI。

公开节选明确说明其目标包含未知方程数和未知左端项。候选项组成数据矩阵，多条关系对应其近零空间，通过 SVD/sRRQR 与列筛选寻找独立、简洁关系。它应当作为我们直接相关工作，而不能说无人研究未知方程数量。作者“无需先验”的表述不应原样扩大：Problem setup 仍然列举导数与非线性候选项。对其噪声阈值细节、候选库规模、代码及系统自由外推，本次未取得足够证据。

## 2. D-CIPHER 明确指出系统发现的歧义

Kacprzyk, Qian & van der Schaar. *D-CIPHER: Discovery of Closed-form Partial Differential Equations*. NeurIPS 2023. 正文与附录：https://arxiv.org/html/2206.10586 ，会议记录：https://papers.neurips.cc/paper_files/paper/2023/hash/57c30b677add9aa78e1745f0643104d0-Abstract-Conference.html 。

F.2 讨论同一场同时满足方程的线性组合及微分后果，Cauchy–Riemann 与拉普拉斯关系是具体例子。系统实验需要用不同字典引导；作者没有声称开箱即用地恢复任意完整系统。对我们而言，这要求区分：常数可逆线性组合下的等价系统，以及只保留部分微分后果造成的信息损失。后者可能放宽解集合，不能简单判作等价。

## 3. 隐式拟合与可辨识性

Kaheman, Kutz & Brunton. *SINDy-PI: a robust algorithm for parallel implicit sparse identification of nonlinear dynamics* (2020). https://arxiv.org/html/2004.02322 ，DOI: https://doi.org/10.1098/rspa.2020.0279 。可借鉴多个候选锚点与规范化比较，不固定让某个物理通道承担时间演化角色。仍依赖候选库，不应把隐式单关系恢复视作完整系统闭合。

Scholl, Bacho, Boche & Kutyniok. *Symbolic Recovery of Differential Equations: The Identifiability Problem*, arXiv:2210.08342v10 (2026-07-07). https://arxiv.org/html/2210.08342 。该条目早期标题为 *Well-definedness of Physical Law Learning: The Uniqueness Problem*，相关 ICASSP 2023 会议论文为 *The Uniqueness Problem of Physical Law Learning*，DOI https://doi.org/10.1109/ICASSP49357.2023.10095017 。不同版本不可当成三个独立方法。

文中说明唯一性依赖允许的函数类，并用特定行波可同时满足复杂方程和简单输运关系说明歧义。数值微分误差甚至会把理论上相关的列变成看似独立，故一次 SVD 的秩判定不充分。我们的启示是联合查看导数方法、尺度与重采样下的关系稳定性；这只是诊断，不能冒充唯一恢复的数学保证。

He, Zhao & Zhong. *How Much Can One Learn a Partial Differential Equation from Its Solution?* Foundations of Computational Mathematics 24 (2024), 1595–1641. 作者机构记录：https://math.duke.edu/publications/how-much-can-one-learn-partial-differential-equation-its-solution ；https://arxiv.org/abs/2204.04602 。分析算子和初始数据如何决定可学习信息。对我们的参考：更长的重复轨迹不必然等于更多独立信息；应测多窗口、多轨迹是否真的增加候选特征的有效信息。

## 4. 新近方法的先验核查

Pervez, Gavves & Locatello. *Mechanistic PDE Networks for Discovery of Governing Equations*, ICML 2025. https://proceedings.mlr.press/v267/pervez25a.html ，正文 §6.2：https://arxiv.org/html/2502.18377 。正文明确二维耦合例只发现其中一条方程，NS 压力梯度已给定。它支持求解器参与发现的机制，但不能作为完整系统自由发现已解决的证据。

Morina, Scholl & Holler. *Symbolic Recovery of PDEs from Measurement Data*, arXiv:2602.15603v2 (2026-04-27). https://arxiv.org/html/2602.15603 。最新 v2 包含二维系统，不能沿用旧摘要说只有一维实验；但 Brusselator 即使标为 unconstrained，也为两方程分别提供 (Δu,u,v) 与 (Δv,u,v)，并预设一阶时间演化。膜输运还按方程结构选择符号架构。理论上恢复可表示的合格规律与在附加可辨识条件下恢复唯一真规律是不同结论。

Liu et al. *FoundPDE: A generative foundation model for data-driven symbolic discovery of partial differential equations*, arXiv:2610.26963 (2026-10). https://arxiv.org/html/2610.26963 。§2.1 为一维单场 PDE，时间导数阶数可选一或二；预训练规范家族和数据到符号机制值得参考，但不是本任务的完整竞争实现。本文按预印本标识，不假定已同行评审。

## 5. 对我们方法的建议：保留少先验目标

以下是本次综合后的研究提案，尚未实现，且不声称已被文献证明有效。

1. **EQGPT 提出关系与子项，联合系数层组织系统。** 从匿名通道 q1…qm 与各坐标的通用运算生成候选，把候选子项取并集，统一在同一批可见数据上评价。避免每次独立生成三条并分别追求高 R²。
2. **估计有限搜索范围内的关系空间。** 令 Θ 的列为规范化候选项，研究 ΘC≈0。关系数应写为给定候选库、导数阶数及误差阈值下的稳定维数，不能直接称为真实基本 PDE 数量。必须排查乘积法则恒等式、数据偶然相关和微分后果。
3. **对关系组而非三条独立回归打分。** 检查规范化、非零性、常数线性独立性、跨窗口留出残差，再挑简洁的基。齐次残差须限制系数范数或规范化，防止零系数获高分；小能量列也需独立尺度处理。
4. **评估“新增关系是否增加约束信息”。** 符号去重只是第一层；还需检测某关系是不是已有关系的乘积、组合或低阶微分后果。常数系数秩不等于微分独立性，数值 Jacobian 满秩不等于适定。
5. **跨数据检验与条件性共享。** 对同一物理参数下不同初值的数据堆叠辨识；若轨迹参数未知，可比较共享系数、分组系数或低维参数化，不能把共享当作已知事实。不能要求在离开观测流形后的任意人工扰动上仍然成立；无真值扰动仅可检验数值敏感性。
6. **将闭合与预测作为单独验收。** 未知约束角色可从最高时间导数依赖与局部一致性分析中提出候选分类；不能强制每个通道有时间导数。预测必须用系统自己产生的耦合场；边界闭合也要明确从哪些可见数据推断。失败需区分残差未收敛、数值失稳、欠约束和预测错误，不能统一视作公式无效或统一归因于求解器。

## 6. 最小验证设计

先做匿名双通道耦合演化、演化加约束、含冗余通道/重复关系三类合成系统；对方法隐藏类型和方程数，统一算子预算、阈值选择及通道预处理。逐级扩展通用导数/表达式预算，观察稳定关系数、冗余率、恢复系统的解集合关系、外推通过率和运行成本。通道重命名/排列不应改变映射回原通道后的结论。

Cylinder 仍保留作目标任务，但不靠单个系统调出一套专用规则。先在离线候选池比较当前逐方程拟合与联合关系筛选；不必立刻重训。真实方程只供独立诊断与最终恢复评价，不进生成、候选库裁剪或阈值选择。

## 7. 研究定位结论

本轮未找到并核实一项同时覆盖“不知道变量语义、不知道方程数、不指定演化/约束角色、自由符号结构、完整系统自由外推”的成熟方案。但这不构成不存在此类方法或我们必然首创的证明。未知方程数已有 Seq-SVF 等直接先例；无预设演化形式已有 SINDy-PI/D-CIPHER 等先例。可争取的贡献在这些能力的结合、关系冗余与闭合的处理，以及对有限数据可辨识边界的可靠报告。
