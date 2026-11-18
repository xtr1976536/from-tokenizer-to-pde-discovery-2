# 阶段 2 第一个主实验：仿真 Cylinder v1

状态：**语料准备与上游词表选择已完成，生成器和数值后端尚未接入，不能开展主实验**。对应 2026-11-15 的主实验方案。

本轮准备版为212条基础结构（三变量80条），按来源/近似结构分组为168/22/22，训练增强4978条；上游候选词表950/1000/1050（含三个控制符）。准备材料、逐条数学复审、公式PDF与最终检查见 `outputs/eqgpt-research/stage2-corpus-2026-11-15/PREPARATION_REPORT.md`。老师的参数意见尚待落实；本轮未启动生成器预训练。

本目录独立于 `ast_bpe_multifield_v4`；旧 EQGPT、解析器、语料和 baseline 源码均不修改。新的三变量 EQGPT、三方程数值后端以后接入。仿真数据准备工具和 mmap 读取器已加入本目录。没有把旧两变量方程补零或硬编码成 Navier–Stokes。

## 来源与调整

审阅服务器 `ast_bpe_multifield_v4/seen_tasks/run_multitrajectory_nopinn.py`、`run_validation_only400.py`、`train_cosine_early.py`、`sft_cosine_early.py` 及 `experiments_v2/window_stream.py`、`round_reward.py`、`round_search.py`。保留“生成—拟合—预测—评分—SFT”的思路，另写新版控制流程，避免覆盖旧代码。

旧实现存在每个候选遍历整个训练集、正式验证数据参与搜索 reward、SFT 验证早停等分支；这些均不直接沿用。配置以主实验计划为准。

## 已实现

- 五个按时间隔离的数据角色：`train_fit`、`reward_holdout`、`validation_select`、`validation_stop`、`test`。检查完整 40 帧窗口，并对同一轨迹的跨角色窗口保留至少 40 帧额外间隔；当前为seen协议：每条轨迹均有五类窗口，完整40帧不交叉，跨角色留至少40帧。
- 所有训练窗口每 epoch 恰好遍历一次，每批 32 个，尽量混合轨迹，最后不足 32 的批次保留。
- 每批重新采样并成功评分 400 个候选；只在该批候选中选 Top10，SFT 后延续权重。统计尝试、成功、拒绝、结构数量与评分积分通过率，达不到预算时明确失败。
- 三种 reward 权重为 0.5、0.2、0；分别启动独立输出目录和独立初始模型，不能串用已更新权重。
- 拟合 R²：每窗口每方程计算，先对窗口等权平均，再对三方程等权平均。预测 reward：原始物理量 SSE/目标能量，稀疏惩罚使用三方程总项数。
- 每 epoch 末另采样 50 个成功候选，在候选选择集按惩罚后预测分数选唯一结构，再在早停集计算误差。
- 保存实际最低归一化联合 RMSE 对应的生成器和方程；早停参考值每累计下降至少 1% 才更新，连续 10 epoch 不满足则停，上限 50 epoch。每批保存恢复状态；保存新权重后才提交恢复指针。
- 测试单独调用，训练入口不读测试窗口；冻结结构后逐窗口只用前 20 帧拟合系数再预测后 20 帧。
- 外框一格、圆柱实体及 8 邻域一格界面排除；依据真实坐标确认几何后才能冻结。各任务共用同一掩码。训练尺度只由 `train_fit` 可见帧估计，同一存储帧不重复计入。

## EQGPT 和数值后端接入边界

`contracts.py` 定义生成器和数值后端接口。未来工厂 `module:function` 返回 `(generator, numerics)`；入口核对二维、三变量、三方程能力，旧两变量 EQGPT 会被拒绝。该版本不改生成器内部实现，预训练与 SFT 参数写在 `config.json`，由后续替换的生成器遵守。

生成器须实现采样、固定 5 epoch 余弦 SFT（1e-5→1e-7，无早停、无回滚）、完整状态保存与恢复。预训练应单独实现 1e-4→1e-6、最多 200 epoch、公式验证 token CE、patience 15、min_delta 1e-5，并返回最佳模型。

数值后端须支持新的方程表示，提供解析、结构键、三条方程项数、可见帧系数拟合和预测。**本次未实现或声称已具备三方程通用求解器。** 不要求压力显式演化，也不强制不可压缩。隐式/代数方程处理、压力规范、外边界闭合、导数模板及积分稳定性必须随新后端单独审计。域外边界值不能读取未来真值。

项数暂定三方程规范化代数项的 LHS+RHS 总和，空间模板展开前计数，Laplacian 不按 x/y 分拆；这一口径必须和新语料/表示核对，当前 readiness 为 false。数值后端只将已知的候选无效/积分失败转换为 `InvalidCandidate`，不能吞掉编程错误。

## 数据接入

`data.py` 接受一个经过审计的 manifest，以及逐轨迹 NPZ 交换格式。每个 NPZ 提供对齐的 `[T,H,W]` 的 `u,v,p`、递增 `t`、一维坐标或二维网格 `x,y`、二维 `solid_mask`。这不是对尚未下载 Arrow 内容的猜测；正式导入器见 `prepare/process_cylinder.py`，它输出下面的 mmap 目录格式；NPZ 仅保留兼容用途。

manifest 字段：

- `branch: numerical`、`revision` 为配置固定版本。
- `official_indices_audited`、`geometry_frozen`、`split_policy_frozen`、`source_alignment_verified`、`pressure_gauge_frozen` 均须为 true。
- `isolation_gap_frames` 至少 40。
- `trajectories` 是 ID 到 `{path, sha256}` 的映射；path 相对 manifest。
- `roles` 包含上述五个角色，每项为 `{trajectory, start}`；每个窗口完整 40 帧。

同一有效区域用于辨识、拟合与预测评价。导数必须先在有足够邻域支撑的原网格计算，再取有效点。替换的数值后端负责保证这一点。

## 实际仿真数据格式与固定协议

数据只放在服务器 `/data1/users/liugang/src/eq-bpe/project/data/`，不下载到本地。

- 原始发布文件：`realpdebench/cylinder/hf_dataset/numerical/`，固定版本的92个Arrow分片。
- 处理入口：`prepare/download_ranges.py`、`process_cylinder.py`、`verify_data.py`。
- 处理目录：`cylinder_numerical_stage2_v1/`；最终入口为该目录 `manifest.json`，只有全量处理完成后才写出。
- 实测原始形状为3990×128×256，u/v/p是float32，坐标和时间是float64。空间按步长2取样为64×128，外框裁1格，存为3990×62×126的逐通道 `.npy`，方便内存映射。
- 实测时间间隔0.005秒，保留原始时间值，不按概况页0.0025秒重造时间轴。
- 圆柱中心由第一条训练参考轨迹前20帧的静态零速度实体支撑区域确定；直径采用官方30mm几何，另排除一格8邻域界面。固定掩码每帧有效点7660；两轮审计检查所有轨迹的几何一致性。
- 裁掉的空间外框单独存为同帧halo。`prepared_data.reconstruct_context` 只重建可见20帧的64×128上下文。三类模型得到相同可见信息；监督、损失与最终评价统一在62×126的有效掩码上。禁止求解时读取未来halo。
- **当前只做seen预测**，92条轨迹都出现在拟合、内部reward、候选选择、早停和测试中，不再整条留出未见轨迹。
- 沿用官方seen的250帧时间块思路，按每条轨迹16块划分（末块240帧），种子525独立随机分配：拟合11块、reward1块、选择1块、早停1块、测试2块。训练池／验证／测试的选中窗口比例为75%／12.5%／12.5%。这是加入严格隔离后的修订协议，不是原样复制官方重叠索引。
- 每块两端各20帧不采样，所有角色窗口步长40。完整40帧窗口在同组内和跨组均不重叠；跨角色窗口实际至少相隔50个未使用帧。
- 每条轨迹窗口数55／5／5／5／10，全体为5060／460／460／460／920；每组都有92条轨迹。每条轨迹有790帧作为隔离边缘或不足窗口而不参与采样，实际数组仍完整保留3990帧。
- baseline使用拟合+reward的同一训练池，共92条轨迹、5520窗口；checkpoint用validation_stop，测试用相同test。原始baseline源码、架构、优化器和更新预算不修改。
- 归一化只用新train_fit窗口前20帧的去重观测，共每条1100帧，不能沿用原整轨迹划分的统计量。
- 活动入口仍为`data/cylinder_numerical_stage2_v1/manifest.json`。旧整轨迹方案与50/25/25的seen方案及其统计量只作历史元数据保存在`history/whole_trajectory_20261115/`、`history/seen50_25_25_20261115/`，不是当前协议。
- 不增加时间滤波、平滑、插值、噪声、压力丢弃或压力规范变换。压力以发布值保留。归一化仅统计新train_fit可见历史中的去重帧与有效空间点，实际字段保留物理量。
- 两轮检查结果以服务器 `maintenance/stage2-seen75-20261115/check-round1.json` 和 `check-round2.json` 为准；没有PASS文件不能把下载／数据审计当作完成。

`data.SimulationData` 根据manifest格式自动选择 mmap 或NPZ读取器。旧EQGPT的唯一保留参考在 `legacy_eqgpt/`，它仍然只有两变量、两方程，与这里准备好的三通道数据不混淆。

## Baseline

保留 `baseline_code` 和 `baseline_configs` 原文件。审阅到的 clean 配置：U-Net batch 12、10000 次更新；FNO batch 32、4000 次更新。其余架构、优化器、调度配置仍由原 YAML 决定。后续为仿真任务单独建立适配入口，使输入输出统一为 u/v/p、20→20，训练目标和评价都用本目录相同区域及划分。**本次未改 baseline，也未将旧两通道 baseline 宣称为已支持三通道。** checkpoint 公平选择规则仍须冻结后才能启动主实验。

## 检查和使用

在项目根目录：

```bash
python3 -m stage2_main_v1 check
python3 -m unittest discover -s stage2_main_v1/tests -v
python3 -m unittest discover -s stage2_main_v1/prepare -p 'test_*.py' -v
```

`check` 只显示准备状态，不导入 torch、不触碰 GPU、不下载数据。当前配置有意保留未就绪标记。不能仅把标记改为 true 来绕过真实审计。

未来接入后训练格式（当前不能执行）：

```bash
python3 -m stage2_main_v1 train --manifest DATA_MANIFEST --factory ADAPTER_MODULE:factory --output NEW_RUN_DIR --weight 0.5
```

另为 0.2、0.0 从同一初始生成器独立启动。恢复使用原命令加 `--resume`；训练冻结后用 `test` 子命令显式评估，禁止根据测试结果重新挑选权重配置。数据、语料、掩码与源码版本应在正式执行前整体冻结。
