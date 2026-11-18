"""Check actual source boundaries and real PyTorch scheduler endpoint."""
import ast,json,math
from pathlib import Path
import torch
root=Path(__file__).resolve().parent
source=(root/'pretrain_tune.py').read_text();tree=ast.parse(source)
loop=next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='epoch')
entry=loop.body[0];assert isinstance(entry,ast.If)
condition=compile(ast.Expression(entry.test),'<actual early-stop condition>','eval')
from types import SimpleNamespace
a=SimpleNamespace(minimum_epochs=30,patience=15)
assert not eval(condition,dict(history=[None]*29,bad_epochs=15,a=a))
assert eval(condition,dict(history=[None]*30,bad_epochs=15,a=a))
assert not eval(condition,dict(history=[None]*30,bad_epochs=14,a=a))
step=next(n for n in ast.walk(loop) if isinstance(n,ast.If) and any(isinstance(k,ast.Expr) and isinstance(k.value,ast.Call) and isinstance(k.value.func,ast.Attribute) and k.value.func.attr=='step' for k in n.body))
step_test=compile(ast.Expression(step.test),'<actual schedule condition>','eval')
for lr in [1e-4,5e-5]:
 a.cosine=20;p=torch.nn.Parameter(torch.tensor(0.));opt=torch.optim.Adam([p],lr=lr);scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(opt,T_max=20,eta_min=1e-6);used=[]
 for epoch in range(1,36):
  used.append(opt.param_groups[0]['lr']);opt.step()
  if eval(step_test,dict(epoch=epoch,a=a)):scheduler.step()
 assert math.isclose(used[0],lr) and used[19]>1e-6
 assert all(math.isclose(v,1e-6,abs_tol=1e-16) for v in used[20:])
assert 'epochs=len(history)' in source
print(json.dumps(dict(status='PASS',checks=['minimum training boundary 29/30','patience boundary14/15','actual PyTorch T20 endpoint for both LRs','eta_min held through epoch35','completion count uses history']),indent=2))
