# From Tokenizer to PDE Discovery — Stage 2

本仓库归档 **212 个公式的新 benchmark、上游词表选择和调参、预训练，以及原始阶段 2 下游实验的代码与已有结果**。这些文件来自本地研究目录和服务器的独立快照。

> 原始下游实验没有跑完，已经人工取消。以下结果是部分训练记录，不是完成的 epoch、最终测试集表现或成功发现 NS 的证明。正在运行的后续优化版实验不属于本次旧实验归档，也未因上传被停止。

## 实验数据：原发布/处理后配对样例

新增 [Cylinder数据处理说明与40帧配对轨迹](dataset_reference/README.md)：包含原发布128×256数组摘录、处理后62×126数组、可见halo、mask、精确相等验证与边界处理动机。

## 主要入口

|内容|路径|
|---|---|
|212 公式 benchmark（确认 212 行）|[`local/outputs/eqgpt-research/stage2-corpus-2026-11-15/frozen/base-structures.jsonl`](local/outputs/eqgpt-research/stage2-corpus-2026-11-15/frozen/base-structures.jsonl)|
|语料来源、审查、去重、增强、拆分与构建代码|[`local/stage2_main_v1/corpus_work`](local/stage2_main_v1/corpus_work)、benchmark 目录中的 provenance/报告|
|8:1:1、6:2:2 冻结语料和各容量词表|[`server_snapshot/stage2_main_v1/preparation_20261116_v2/outputs/eqgpt-research/stage2-preparation-2026-11-16`](server_snapshot/stage2_main_v1/preparation_20261116_v2/outputs/eqgpt-research/stage2-preparation-2026-11-16)|
|阶段 2 上游指标和词表扫描|上一路径中的 `UPSTREAM_TABLES.md`、`UPSTREAM_TABLES.csv`、`*/upstream/`|
|上游调参及容量复核|[`server_snapshot/runs/stage1_tuning_20261116`](server_snapshot/runs/stage1_tuning_20261116)、`stage1_tuning_v96_128_160_20261116`、`stage1_v128_confirmation_20261117`|
|最新上游搜索实验与输出|[`server_snapshot/runs/stage1_latest_full_20261117`](server_snapshot/runs/stage1_latest_full_20261117)|
|EQGPT 超参数搜索与复核|[`server_snapshot/runs/eqgpt_tuning_20261117`](server_snapshot/runs/eqgpt_tuning_20261117)、`eqgpt_confirmation_20261117`|
|阶段 2 预训练、调参与正式 v2|`server_snapshot/runs/stage2_pretraining_*`|
|原始阶段 2 下游的准确历史代码|[`server_snapshot/runs/stage2_main_full_v2_safe_20261116/historical_code/code`](server_snapshot/runs/stage2_main_full_v2_safe_20261116/historical_code/code)|
|原始阶段 2 配置、Top10、日志和恢复点|[`server_snapshot/runs/stage2_main_full_v2_safe_20261116`](server_snapshot/runs/stage2_main_full_v2_safe_20261116)|
|评审、曲线、调参分析|[`local/outputs/eqgpt-research`](local/outputs/eqgpt-research)|
|原始服务器文件与 SHA-256 清单|[`manifests/server_sources.json`](manifests/server_sources.json)|

`preparation_212_v1`、`preparation_20261116_v2` 和不同 `selection.json` 保留了历史筛选规则及候选容量，它们可能包含后来被替代的选择。不要混用早期 tokenizer 指标选优与正式预训练的验证 NLL/byte 选优。实际原始下游矩阵、config 和 checkpoint 选择记录是复现运行的依据。最终原始下游矩阵包含 811/622 × 128/192/320；128 是后续选择的小词表。

## 原始下游未完成实验

|组别|已保存完整 batch 数|恢复点|
|---|---:|---|
|811-v320-seed525|12|epoch000_next000012.bin|
|622-v320-seed525|8|epoch000_next000008.bin|
|811-v128-seed525|22|epoch000_next000022.bin|
|622-v128-seed525|31|epoch000_next000031.bin|

共 **73 个完整 batch**，每个保留候选 Top10、统计和 SFT 记录。192 两组当时尚未启动。中断时内存中未提交的候选不在 batch 文件内；保留的 `progress.json` 是进度证据，不代表可恢复全部未提交候选。

## 大文件和模型权重

全部模型权重（不是仅 best）放在 [archive-2026-11-18 Release](https://github.com/xtr1976536/from-tokenizer-to-pde-discovery-2/releases/tag/archive-2026-11-18)，使用内容寻址附件 `weight-<SHA256>.<suffix>`。原路径映射保存在 `manifests/server_sources.json`。同一内容只上传一次，但清单保留所有原路径。约 108 GiB、419 个去重后的权重附件；Git 仓库不直接保存这些二进制权重。

辅助 PDF、图像数组、原始源码压缩包等打包为 `supporting-binary-artifacts.tar.gz`，其内部 asset 名称与原路径映射在 `manifests/release_artifacts.json`。其他本地压缩包在 `local-source-archives.tar.gz`，路径对应 `manifests/local_sources.json`。

使用 `python tools/restore_weights.py --destination /path/to/project` 可按原服务器项目相对路径还原权重；提供 `--verify-only` 可检查已有文件。磁盘需能容纳全部权重及重复路径；脚本对重复内容优先建立硬链接。

## 数据和复现边界

- 全量 Cylinder 模拟场是外部数据集，不打进 Git；数据版本、split、预处理和几何/压力审计记录随代码保存。相关许可须按原数据来源处理。
- 保留了实验当时的绝对服务器路径和队列状态；在其他机器运行前需要调整配置中的路径。
- 上游正在增长的实验目录按此次导出时刻取文件快照，不能把 `queue_status` 中的 running 当成归档后仍可控制的任务。
- 虚拟环境、Git 元数据、缓存、操作系统旁路文件不归档；公开脚本中的凭据替换为环境变量。原始文件 SHA 与发布 SHA 分开保存，避免把脱敏文件误称逐字节原件。
- 没有添加第三方内容的统一许可证；各上游源码/文献/数据的原许可证和来源继续适用。

完整性核验和发布进度见 `manifests/`。权重上传完成后会加入最终 Release 附件核验清单。
