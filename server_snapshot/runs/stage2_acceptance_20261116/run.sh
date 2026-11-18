#!/bin/bash
set -euo pipefail
cd /data1/users/liugang/src/eq-bpe/project/stage2_main_v1/preparation_20261116_v2
export CUDA_VISIBLE_DEVICES=1 PYTHONPATH=/data1/users/liugang/src/eq-bpe/project/stage2_main_v1/preparation_20261116_v2:/data1/users/liugang/src/eq-bpe/project/stage2_main_v1/preparation_20261116_v2/math_tokenizer_project_release/src
for PHASE in evaluate generate; do
/data1/users/liugang/src/eq-bpe/project/.venv/bin/python -u -m stage2_main_v1.acceptance --phase $PHASE --models /data1/users/liugang/src/eq-bpe/project/runs/stage2_pretraining_formal_v2_20261116 --output /data1/users/liugang/src/eq-bpe/project/runs/stage2_acceptance_20261116
done
