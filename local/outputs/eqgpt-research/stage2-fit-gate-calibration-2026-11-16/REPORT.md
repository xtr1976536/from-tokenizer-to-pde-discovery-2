# Latest coarse fit gate and reduced Cylinder acceptance

The fixed threshold is strictly greater than -0.0035 for each equation's batch-mean R2. Calibration used only two training trajectories and reproduced 512 samples: 192 finite fits, 78 rejected (40.625%), 114 retained. Including invalid and unfit candidates, total rejection was 77.734375%. No per-batch quantile policy is applied.

An independent-seed vocab320/811 reduced run passed: 34 inspected training candidates yielded 2 accepted formulas; five SFT epochs changed weights, save/load was identical; seven inspected fresh post-SFT candidates yielded one fit-and-forecast candidate; validation_select and independent validation_stop each used one real Cylinder window. Training used two windows. Observed generation was batched, so 40 and 8 strings were emitted respectively. No test fields or training future targets were read. Frozen pretrained checkpoint remained unchanged.

Stop normalized joint RMSE: 0.037575171898993426; channel normalized RMSE: [0.010451797924790016, 0.024554817795417152, 0.059359089218837716]. Total elapsed time: 136.21950948610902 seconds. This establishes reduced execution, not discovery accuracy or formal 32-window/400-candidate feasibility. Baselines and full six-model runs were not launched.

Production numerical budgets remain 30 seconds internal per forecast window, 30000 residual calls across the whole rollout, max_nfev=30 per implicit time step, residual tolerance 1e-4. Smoke additionally imposes a 45-second candidate hard deadline. The current generic rollout-budget error does not distinguish the time and call caps.
