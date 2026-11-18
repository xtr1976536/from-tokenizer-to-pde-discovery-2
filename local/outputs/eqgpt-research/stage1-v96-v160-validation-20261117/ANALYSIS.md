# Vocabulary96/160 validation results

Paired improvements compare seed525 selected and previous strategy on identical vocabulary and split. Three-seed SD is descriptive, not a significance test. Cross-vocabulary comparisons use NLL per rendered byte (NPB), not token CE. Flags are triage only; train-validation gaps require inspection.

|Scale|Split|Vocab|CE mean +/- SD|NPB mean +/- SD|Paired improvement|Max rebound|Capped|
|---|---|---:|---:|---:|---:|---:|---:|
|212|811|96|1.042392 +/- 0.004851|0.489680 +/- 0.002279|10.395%|0.758%|0|
|212|811|160|1.608829 +/- 0.007061|0.475366 +/- 0.002086|5.804%|0.291%|0|
|212|622|96|1.310116 +/- 0.003967|0.507493 +/- 0.001537|2.492%|0.047%|0|
|212|622|160|1.874820 +/- 0.006561|0.521228 +/- 0.001824|1.885%|0.046%|0|
|636|811|96|0.826766 +/- 0.003954|0.341606 +/- 0.001634|4.805%|0.049%|0|
|636|811|160|1.335103 +/- 0.002523|0.336981 +/- 0.000637|3.658%|0.066%|0|
|636|622|96|0.876647 +/- 0.002716|0.357911 +/- 0.001109|6.835%|0.029%|0|
|636|622|160|1.341418 +/- 0.001255|0.350172 +/- 0.000328|4.597%|0.079%|0|

Inspect flagged histories and cap trends before declaring training adequate or accepting shared parameters. Do not automatically launch additional tuning or downstream PDE search.