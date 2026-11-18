"""Create the final preparation record only after all required receipts pass."""
from pathlib import Path
import json,datetime
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
def load(name):return json.loads((BASE/name).read_text())
def main():
 names=['check-round1.json','check-round2.json','final-check1.json','final-check2.json','legacy-check.json','metadata-integrity.json','trajectory-content-audit.json']
 for name in names:assert load(name)['status']=='PASS',name
 server=load('server-retire-receipt.json');local=load('retire-local-receipt.json')
 assert server['status']==local['status']=='PASS'
 data=load('data-manifest.json');geo=load('geometry.json');corpus=load('corpus-audit.json');storage=load('server-storage.json')
 norm=data['normalization'];raw=load('remote-files.json');raw_bytes=sum(r['size'] for r in raw if r['path'].endswith('.arrow'))
 summary={'status':'COMPLETE','scope':'Stage2 first main experiment preparation only',
  'completed_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds'),
  'raw_shards':92,'raw_GiB':raw_bytes/2**30,'processed_trajectories':92,
  'raw_shape':[3990,128,256],'context_shape':[64,128],'cropped_shape':[62,126],
  'dt_seconds':.005,'effective_points':7660,'trajectory_roles':data['role_trajectory_counts'],
  'window_roles':data['role_window_counts'],'baseline_training_trajectories':68,
  'normalization':norm,'server_retired_files':server['deleted_source_config_files'],
  'local_retired_files':local['deleted_source_config_files'],'data_checks':2,'comprehensive_post_cleanup_checks':2,
  'baseline_source_unchanged':True,'eqgpt_modification_started':False,'training_started':False,
  'available_disk_GiB':storage['available_bytes']/2**30}
 (BASE/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
 role_names={'train_fit':'方程拟合／在线batch','reward_holdout':'内部预测reward','validation_select':'候选结构选择','validation_stop':'早停／checkpoint','test':'最终测试'}
 table='\n'.join(f"| {role_names[r]} | {data['role_trajectory_counts'][r]} | {len(data['roles'][r])} | {'10' if r=='train_fit' else '40'} |" for r in role_names)
 mean='、'.join(f'{x:.9g}' for x in norm['mean']);scale='、'.join(f'{x:.9g}' for x in norm['scale'])
 text=f'''# 阶段2第一个主实验：Cylinder仿真数据与旧EQGPT基座准备完成

完成时间：{summary['completed_at']}。本次仅准备数据、固定旧模型与语料并清理旧代码，**未启动EQGPT改造、候选搜索、SFT或baseline训练**。

## 数据位置与完整性

服务器项目根目录：`/data1/users/liugang/src/eq-bpe/project`。

- 原始文件：`data/realpdebench/cylinder/hf_dataset/numerical/`。
- 处理版：`data/cylinder_numerical_stage2_v1/`，训练入口为其`manifest.json`。
- 固定版本：`{data['revision']}`；共92个Arrow分片，原始大小{raw_bytes/2**30:.5f} GiB。
- 92个分片均通过官方LFS SHA-256校验；10个索引、字段、版本及状态元数据文件通过固定版本Git对象校验。
- 原始数据和权重仅保存在服务器。本地仅同步代码、语料文本、元数据、检查报告及小型几何预览。

## 实际字段、时间与裁剪

实际Arrow字段为对齐的u/v/p，float32，形状3990×128×256；坐标和时间为float64。先按官方空间步长2取样为64×128，再裁去矩形外框1格，物理保存为3990×62×126的mmap `.npy`。

**实际时间数组间隔为0.005秒**，范围0.05至19.995秒；模型积分必须使用这些时间值，不能把概况页原始采样间隔0.0025秒代入处理后的时间轴。

圆柱中心由训练参考轨迹`{geo['training_reference_trajectory']}`前20帧的静态零速度支撑区域确定，坐标为({geo['center_x_m']:.12g}, {geo['center_y_m']:.12g})米。半径固定0.015米，另排除一格8邻域界面带。每帧统一有效点数为7660。掩码已作可视检查，并在全量数据检查中独立重算。

裁掉的空间外框单独保存为同帧halo，所有方法均可重建同一可见20帧64×128输入上下文。监督、损失和最终误差统一采用62×126有效掩码。数据入口不向拟合／预测函数提供未来halo。

处理不增加时间滤波、平滑、插值、噪声、压力随机屏蔽或压力规范变换，p保留发布值。审计对象是官方发布的数值数组；不将此次检查扩大宣称为重建了发布前不可见的全部处理过程。

## 原始泄漏与新划分

官方索引训练／验证、训练／测试、验证／测试之间，共享完整40帧窗口中的帧数分别为2100、1940、7920（计数单位为唯一轨迹ID+帧ID）。原索引原样保留作为证据，不直接用于本实验。

新划分以整条轨迹隔离，按参数范围分层，种子525：

| 用途 | 轨迹数 | 40帧窗口数 | 起点步长 |
|---|---:|---:|---:|
{table}

五类角色之间共享轨迹数、共享帧数均为0，全部窗口含完整20帧输入与20帧未来。全轨迹u/v/p联合内容哈希没有发现不同ID下的完全重复数据。此为本实验重新冻结的划分，不宣称等同于官方benchmark划分。

内部reward留出集会反馈到EQGPT训练，因此**baseline训练获得train_fit与reward_holdout的同一训练池**：68条轨迹、24552个窗口；其checkpoint使用validation_stop，最终使用同一test。baseline原始代码和训练专属超参数不在本轮修改。

所有方法共用同一归一化统计，只由train_fit可见历史的去重帧和有效区域计算。计数{norm['point_count']:,}个时空点（每点3通道）；u/v/p均值依次为{mean}，标准差依次为{scale}。独立第二轮使用另一种累计算法重算并核对通过。

## 唯一保留的旧EQGPT版本与语料

位置：`stage2_main_v1/legacy_eqgpt/`。主生成源码为`layout/ast_bpe_multifield_v4/generator_search_optimized.py`，旧两方程数量采样器与必要共享解析／数学运行库一起保留。架构、源码和权重保持原样，旧任务接口仍为u/v双变量、两方程。

旧模型为768维、6层8头、词表300、位置上限72；与v5 PDE语料／词表／编码文件逐项哈希匹配。模型检查包括CPU读取、前向、完整编码往返和共享依赖导入，未训练。后来出现的混合ODE语料模型未被错误选作本次PDE基座。

活动语料为200个父公式、136个来源组，父公式训练177／验证23；增强编码训练1096／验证168，共1264条，来源组不跨集合。公式清单与划分均采用匹配编码文件的v5元数据。语料含160个两变量、32个三变量、8个四变量系统，空间轴均为x/y；尚未为u/v/p新任务改写。

原模型检查点保存在服务器的`legacy_eqgpt/checkpoint/model.pt`。本地不另下载权重或Linux专用编译缓存。源文件、tokenizer本地编译依赖和实际历史预训练来源均记录于`REFERENCE.json`。

## 旧代码清理与保护

服务器删除{server['deleted_source_config_files']}个旧实验源码／配置／缓存文件，本地删除{local['deleted_source_config_files']}个。操作只覆盖核实的旧阶段2目录、历史阶段2运行目录和指定探针／监控入口。删除前执行两次文件与保护对象核对，删除后复核。

baseline源码、baseline配置、所选旧EQGPT与语料以及其他研究内容保留。旧目录只留下必要共享模块的兼容软链接，指向`legacy_eqgpt/layout`中的唯一物理代码副本；不保留旧实验入口与分支的重复源码。清理后重新扫描，待删除的非选定旧源码为0。

## 两轮检查

- 数据第一轮：92个官方LFS哈希、全量u/v/p裁剪值和halo逐块对照、坐标时间对齐、掩码独立重算及文件哈希，PASS。
- 数据第二轮：独立核查轨迹／完整40帧隔离、字段有限性、训练统计重算、原始索引未变，PASS。
- 清理后综合第一轮：实际完整mmap读取、输入上下文与掩码、测试访问屏障、受保护内容哈希，PASS。
- 清理后综合第二轮：旧代码残留复扫、旧模型／语料一致性、7项主流程与3项数据准备测试、受保护内容哈希，PASS。

所有回执与检查文件保存在本目录；服务器对应目录为`maintenance/stage2-data-20261115/`。

当前剩余磁盘空间约{storage['available_bytes']/2**30:.1f} GiB（共享/data1，在检查时测得）。数据准备已就绪；新三变量EQGPT及三方程数值后端仍未改造，继续执行须等待用户下一步确认。
'''
 (BASE/'REPORT.md').write_text(text)
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
