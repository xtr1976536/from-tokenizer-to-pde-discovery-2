# EqGPT补充确认：11组

用户批准76组复核后的建议。四首选各seed526/527=8组；636/622同LR1e-4/L2=.001的T25补seed526/527=2组，与已有T30首选配对；212/622 LR5e-5/L2=.001/T30 seed525 minimum45=1组，检查原30轮停止后的恢复。

全部从头初始化，不恢复旧进度；seed525已有首选直接复用用于汇总，不重复训练。原GRE分词、6层、batch128、clip1、Adam、最高80轮、patience15、delta1e-4、eta_min1e-6不变。L2仅矩阵；主候选minimum30，恢复任务minimum45。只读取冻结train/validation，不用test。

四首选：212/811 LR1e-4 L2=.001 T20；212/622 LR5e-5 L2=.001 T20；636/811 LR5e-5 L2=0 T20；636/622 LR1e-4 L2=.001 T30。

独立目录/runs/eqgpt_confirmation_20261117；GPU3 UUID GPU-ba72db90-47e9-38fd-0e9e-905c3b1798b5，4并发、8GiB分配上限/worker、启动前used+9GiB≤92GiB、总配额32GiB；原有任务不动，AST GPU1队列不动。旧76组保存。只执行预训练确认，不自动开启下游。

全部完成自动审计11份记录、三种子候选摘要、636/622 T25/T30三种子配对及212/622恢复前后结果，输出CSV/JSON/曲线。最终选择仍需复核平台趋势、gap、封顶和轻微回升，不能仅依据最低点；不把单seed旧策略对照夸大为三seed配对。
