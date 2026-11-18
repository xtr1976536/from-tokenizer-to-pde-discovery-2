# 阶段 2 盘点、新版流程与清理记录

日期：2026-11-15。服务器项目：`/data1/users/liugang/src/eq-bpe/project`。

## 盘点

- 主体代码在 `ast_bpe_multifield_v4`，依赖 `ast_bpe_multifield_v1`、`ast_bpe_multifield_v2`。有原联合 PINN、多轨迹无 PINN、逐窗口系数重拟合、预测 reward、不同轨迹分组等历史分支。
- baseline 源码和配置在 `baseline_code`、`baseline_configs`。原 clean 配置为 U-Net batch 12/10000 次更新、FNO batch 32/4000 次更新。
- 旧数据为 `data/realpdebench/cylinder/hf_dataset/real`，约 33.62 GiB；`seen_tasks` 有约 8.18 GiB 真实轨迹导出缓存。旧 baseline adapter 内名为 numerical 的链接实际指向 real，已按旧数据清理。
- 真正 numerical 分支仅有 `state.json`、`dataset_info.json` 和 train/val/test 索引，未下载轨迹分片。它们和 `version.json`、`channels.json` 已保留并纳入哈希保护。
- 本地旧 Cylinder 样本包括 v2 的 Arrow/NPZ、v3/v4 的窗口副本、seen_tasks 导出轨迹和协议审计用原始 H5，已清理。

## 新版本

本地 `stage2_main_v1/` 与服务器同名目录。使用独立模块，不覆盖原 EQGPT、解析器或 baseline。

已实现五角色窗口隔离、有效区域构建、训练尺度估计、32 窗口在线批次、400 个成功候选、当前批 Top10 SFT 调用、三种 reward 权重、epoch 末 50 个候选与双验证集、归一化 RMSE 早停、每批恢复检查点、冻结后单独测试入口。原三种 reward 方案需要分别从同一初始生成器独立启动。

当前是可审阅和测试的**主流程代码**，不是完整可运行的三方程系统。数据导入器、新 EQGPT 和三方程数值后端通过显式接口接入；未伪造三变量生成器或数值求解结果。预训练和 SFT 配置遵循计划，但生成器内部训练实现按用户要求留待单独修改。项数口径、边界闭合、压力规范、通用隐式方程处理及 baseline 新任务适配需随后续接入审计。默认 `check` 明确报告 PREPARED_NOT_RUNNABLE。

数值后端接口有意不预设 Navier–Stokes、不强制不可压缩，也不要求压力必须显式演化。详细接入契约见 `stage2_main_v1/README.md` 和 `contracts.py`。

## 清理结果

| 位置 | 删除文件数 | 逻辑大小 |
|---|---:|---:|
| 服务器 | 9,561 | 100.78148 GiB |
| 本地 | 586 | 1.94873 GiB |

删除范围为旧真实 Cylinder 数据及派生窗口/索引、核实的阶段 2 旧运行结果、模型权重、日志、预测缓存、基线旧训练产物。逐文件 unlink，不使用整个项目目录的递归删除；运行目录中混放的源码、配置和文档保留。空目录保留，避免破坏旧代码结构。

两轮清理各有逐文件清单和回执；每次删除前执行两次身份与源文件哈希核对，删除后再次校验。服务器 1,993 个、本地 23,388 个受保护源码/配置/共享数据文件纳入最终保护清单。所有目标确认不存在，受保护文件未变。最终按清理策略复扫待删文件数均为 0。

以下范围未清理：阶段 0/1 内容、共享公式语料和词表、阶段 3 及其教师/学生运行产物、旧 EQGPT 和 baseline 源码、实验配置和说明文档。`runs/corpus_retrain_*` 等共享公式预训练产物保留，避免把跨阶段资源归入旧 Cylinder 运行产物误删。

## 验证和审计文件

本地及服务器在清理前后均运行 7 项单元/流程测试，全部通过。测试使用极小的替身生成器/数值后端，检查控制流程、数据角色隔离、预算失败、能力拒绝、SFT 更新、恢复状态和冻结测试屏障；没有真实训练或积分验证。

本目录包含：

- `server-delete-manifest.json`、`server-residual-manifest.json` 和对应回执；
- `local-delete-manifest.json`、`local-residual-manifest.json` 和对应回执；
- `local-final-inventory.json`、`server-final-inventory.json`；
- `summary.json`、`local-final-tests.txt`、`server-final-tests.txt`；
- `maintenance.py`：本次明确路径策略与两次检查的清理工具。

服务器审计目录为 `maintenance/stage2-refresh-20261115/`。本次没有下载仿真轨迹，没有启动 GPU 任务，没有修改 baseline 或旧 EQGPT。
