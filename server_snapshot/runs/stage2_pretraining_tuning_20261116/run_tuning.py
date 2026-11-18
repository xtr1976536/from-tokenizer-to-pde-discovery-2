from pathlib import Path
import json
from stage2_main_v1.generator import ASTBPEGenerator,DEFAULT_PRETRAIN
root=Path('/data1/users/liugang/src/eq-bpe/project/stage2_main_v1/preparation_20261116_v2/outputs/eqgpt-research/stage2-preparation-2026-11-16/811')
train=[json.loads(l)['text'] for l in (root/'frozen/train-augmented.jsonl').read_text().splitlines()]
val=[json.loads(l)['normalized']['text'] for l in (root/'frozen/validation.jsonl').read_text().splitlines()]
tests=[('lr1e4_wd1e3',1e-4,1e-3),('lr5e5_wd1e3',5e-5,1e-3),('lr1e4_wd1e2',1e-4,1e-2)]
for name,lr,wd in tests:
 cfg=dict(DEFAULT_PRETRAIN,maximum_epochs=80,cosine_epochs=25,learning_rate=lr,minimum_learning_rate=1e-6,patience=15,min_delta=1e-4,minimum_epochs=25,weight_decay=wd,batch_size=128,token_budget=8192,gradient_clip=1.)
 run=Path('/data1/users/liugang/src/eq-bpe/project/runs/stage2_pretraining_tuning_20261116')/name
 if (run/'COMPLETE.json').exists():continue
 g=ASTBPEGenerator(root/'upstream/ast-bpe-192.json',device='cuda',seed=525,positions=2048)
 result=g.pretrain(train,val,run,cfg)
 h=result['history'];best=result['best_epoch']-1
 row=dict(name=name,lr=lr,weight_decay=wd,epochs=len(h),best_epoch=result['best_epoch'],best_val_ce=result['best_loss'],
   val_first=h[0]['validation']['token_cross_entropy'],val_10=h[min(9,len(h)-1)]['validation']['token_cross_entropy'],
   val_25=h[min(24,len(h)-1)]['validation']['token_cross_entropy'],val_last=h[-1]['validation']['token_cross_entropy'],
   train_last=h[-1]['train']['token_cross_entropy'],minimum_epochs=25,patience=15,cosine_epochs=25)
 (run/'tuning-summary.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
