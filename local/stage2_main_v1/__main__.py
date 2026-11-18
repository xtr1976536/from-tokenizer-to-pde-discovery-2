"""Default check is read-only; run requires explicit trained adapter factory."""
import argparse
import importlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['check','train','test'])
    p.add_argument('--config',default=str(Path(__file__).with_name('config.json')))
    p.add_argument('--manifest');p.add_argument('--factory',help='module:function returning (generator,numerics)')
    p.add_argument('--output');p.add_argument('--weight',type=float,choices=[1.],default=1.,help='Compatibility argument; Stage1 fit-only reward uses1')
    p.add_argument('--resume',action='store_true')
    a=p.parse_args();config=json.loads(Path(a.config).read_text())
    if a.action=='check':
        print(json.dumps({'status':'PREPARED_NOT_RUNNABLE','audits':config['readiness'],
              'legacy_eqgpt':{'fields':['u','v'],'equations':2,'modified':False},
              'available_factory':'stage2_main_v1.generator:factory',
              'pending':[name for name,ready in config['readiness'].items() if not ready],
              'required_plugins':['selected pretrained checkpoint','Cylinder/backend acceptance'],
              'baseline_source_modified':False},ensure_ascii=False,indent=2));return
    if not all(config['readiness'].values()):p.error('Data, geometry, corpus and backend audits are not complete')
    if not all([a.manifest,a.factory,a.output]) or (a.action=='train' and a.weight is None):
        p.error('Explicit manifest, factory, output and training weight are required')
    from .data import SimulationData
    from .runner import run,evaluate_frozen
    module,name=a.factory.split(':');generator,numerics=getattr(importlib.import_module(module),name)(config)
    data=SimulationData(a.manifest,config)
    if a.action=='train':run(config,data,generator,numerics,a.output,a.weight,a.resume)
    else:evaluate_frozen(config,data,numerics,a.output)

if __name__=='__main__':main()
