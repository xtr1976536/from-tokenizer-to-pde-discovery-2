# 阶段2预训练参数调整依据

本轮不自动选择词表，也未启动正式预训练。8:1:1和6:2:2都是主实验；参数模板分别用于用户随后选定的词表。

## 阶段1实际证据

核对用户提供论文所指仓库，固定提交912bdad07938d0506abe5f76cc54dc597985ad00，共读取60份正式预训练日志。其中212条语料的9次AST-BPE训练，最佳epoch为7–12，中位数9；停止epoch为22–27，中位数24。其他语料规模的AST-BPE最佳epoch中位数为7–9，停止epoch中位数为22–24。详细数值和每份来源的SHA-256见stage1-training-evidence.json。

原代码为Adam、初始LR1e-4、最小LR1e-6、余弦T_max200、最大200epoch、patience15、min_delta1e-5。周期过长，使大多数训练在学习率还接近初值时就已停止。

老师的截图建议作为经验依据：小数据训练通常10–30epoch早停，学习率偏小可能拖到100epoch以后，可以调整L2。这不是必须在第30epoch停止的硬规则。

## 本轮配置

|参数|阶段1/原计划|阶段2准备配置|
|---|---|---|
|初始学习率|1e-4|2e-4|
|最小学习率|1e-6|1e-6|
|余弦退火周期|200epoch|25epoch|
|周期结束后|原长周期|保持最小学习率，不再次升高|
|最大epoch|200|60|
|早停patience|15|8|
|最小改善|1e-5|1e-4（验证token CE的绝对变化）|
|最早停止|未单列|至少10epoch|
|L2|Adam未设weight_decay|1e-4，仅矩阵参数；bias/归一化参数不衰减|
|梯度裁剪|1|1|
|batch|128|最多128，并限制每批约8192token|
|最大上下文|72|2048，不截断超长公式|
|模型层数/宽度|6层，d_model768|保留阶段1配置|

使用Adam的耦合weight_decay实现L2梯度，避免把AdamW的解耦衰减直接称为同一种L2。L2用于预训练；在线SFT保持5epoch、1e-5→1e-7余弦、无早停、weight_decay0。验证集用于最佳checkpoint和早停，测试不参与。

短周期与增大学习率的目的，是在阶段1实测有效区间内完成主要学习率调整。阶段2语料更复杂，最终是否在10–30epoch早停必须由验证曲线决定；这些参数不是已经经过正式训练证明最优的结果。

## 实现与验证

生成器提供真实预训练入口、在线SFT、最佳模型保存、完整optimizer/RNG恢复与断点续训。小模型CPU测试核对更新发生、SFT执行及中断恢复与连续训练完全一致。未将两epoch的小模型smoke运行当作正式预训练结果。

正式入口示例（词表由用户选定后替换V）：

```bash
python -m stage2_main_v1.pretrain --split 811 --vocab V --settings outputs/eqgpt-research/stage2-preparation-2026-11-16/pretraining-settings.json --output NEW_RUN_DIR --device DEVICE
```

6:2:2使用--split622；种子由--seed指定，默认525。设备由用户配置，不自动占用GPU。
