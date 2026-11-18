#!/usr/bin/env bash
set -euo pipefail
PROJECT=/data1/users/liugang/src/eq-bpe/project
WORK=$PROJECT/stage2_main_v1/preparation_20261116_v2
OUT=$PROJECT/runs/stage2_pretraining_formal_v2_20261116
PY=$PROJECT/.venv/bin/python
export CUDA_VISIBLE_DEVICES=0
cd $WORK
for SPLIT in 811 622; do
  for VOCAB in 128 160 192 320 416; do
    RUN=$OUT/$SPLIT/vocab_$VOCAB
    mkdir -p $RUN
    PYTHONPATH=$WORK:$WORK/math_tokenizer_project_release/src $PY -m stage2_main_v1.pretrain --split $SPLIT --vocab $VOCAB --seed 525 --device cuda --settings $WORK/outputs/eqgpt-research/stage2-preparation-2026-11-16/pretraining-settings.json --output $RUN > $RUN/train.log 2>&1
  done
done
