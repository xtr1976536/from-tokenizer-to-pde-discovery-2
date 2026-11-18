# EqGPT下游追加到AST队列之后

用户批准使用最终调参模型加入AST队列等待。12个最佳模型（212/811 LR1e-4,L2.001,T20；212/622 LR5e-5,L2.001,T20；636/811 LR5e-5,L2=0,T20；636/622 LR1e-4,L2.001,T25）×八案例=96任务，seeds525/526/527。无需预训练。

保持旧EqGPT下游legacy采样：SAT限制、20%均匀随机混合、5cycle、每cycle400成功评分目标、现行15000尝试上限、收不足用实际候选继续、累计Top10及5轮SFT/旧余弦1e-5到1e-7；数值代理缓存/评分/结构判定不变。不将AST的纯模型采样和EqGPT legacy说成完全相同采样实验。AST混合任务继续暂缓。

采用队尾等待进程：先等待同一queue.lock，现有AST纯模型队列释放锁后才准入，无需重启正在运行的任务。等待时不加载GPU模型；同GPU1，最多6组、14GiB/worker、84GiB配额、92GiB实际显存准入。准入后先做参考采样/SFT smoke，再执行96任务；案例失败单独记录并继续其他任务。共享现有结果目录且arm独立eqgpt_reference，完成后输出eqgpt_case_results.csv/eqgpt_summary.json。等待状态eqgpt_waiting_status.json；执行状态eqgpt_downstream_status.json。

仅建立链接复用最终已训练best.pt，逐个校验SHA256、训练配置、模型seed与最佳轮。其余AST队列、代码和完成结果不改。

## 用户批准改用GPU3独立运行

实测GPU3占用9256MiB/97871MiB、利用率100%，非闲置但显存余量最大。停止仅等待中的EqGPT supervisor（尚未加载模型，无在跑案例），改为独立eqgpt_queue.lock和eqgpt_downstream_status.json，不覆盖AST的queue_status.json。GPU3最多4并发、14GiB/进程、56GiB本任务配额、used+15GiB≤92GiB准入。先自动smoke验证，再运行96任务；AST原GPU1任务不中断。模型及搜索参数不变，结果仍按eqgpt_reference/legacy独立保存。
