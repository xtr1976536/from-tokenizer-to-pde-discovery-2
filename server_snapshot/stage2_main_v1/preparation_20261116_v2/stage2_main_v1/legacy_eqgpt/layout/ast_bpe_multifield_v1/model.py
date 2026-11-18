"""Original stage-one decoder classes, loaded without GRE vocabulary side effects.
Only trusted local function/class definitions are executed, never corpus text.
The production dimensions match stage one; small dimensions are smoke-test only.
"""
import ast,hashlib,json,random
from pathlib import Path
import numpy as np
import torch
from torch import nn,optim
from torch.utils import data as Data
SOURCE=Path(__file__).resolve().parents[1]/'分词器-pde发现/eqgpt_original/code/gpt_model.py'
DEFAULT=dict(d_model=768,d_ff=2048,d_k=64,d_v=64,n_layers=6,n_heads=8)
SMOKE=dict(d_model=48,d_ff=96,d_k=12,d_v=12,n_layers=1,n_heads=4)

def build(vocab_size,positions=512,device='cpu',seed=525,smoke=False):
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    tree=ast.parse(SOURCE.read_text());definitions=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
    config=SMOKE.copy() if smoke else DEFAULT.copy()
    env=dict(torch=torch,nn=nn,optim=optim,np=np,random=random,Data=Data,device=torch.device(device),vocab_size=vocab_size,max_pos=positions,CLIP=1,**config)
    exec(compile(ast.Module(body=definitions,type_ignores=[]),str(SOURCE),'exec'),env)
    model=env['GPT']().to(device)
    model.stage2_config=dict(**config,vocab_size=vocab_size,positions=positions,smoke=smoke,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest())
    return model

def save(model,path,**metadata):
    torch.save(dict(config=model.stage2_config,state=model.state_dict(),metadata=metadata),path)

def load(path,device='cpu'):
    d=torch.load(path,map_location='cpu',weights_only=True);c=d['config'];m=build(c['vocab_size'],c['positions'],device,smoke=c['smoke']);assert m.stage2_config==c
    m.load_state_dict(d['state']);return m,d['metadata']
