"""Explicit entrypoint: user selects split and vocabulary; no implicit sweep."""
import argparse,json
from pathlib import Path
from .generator import ASTBPEGenerator,DEFAULT_PRETRAIN


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--split',choices=['811','622'],required=True)
    ap.add_argument('--vocab',type=int,choices=list(range(64,500,32)),required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--device',default='cpu')
    ap.add_argument('--epochs',type=int);ap.add_argument('--smoke',action='store_true');ap.add_argument('--resume',action='store_true')
    ap.add_argument('--positions',type=int,default=2048);ap.add_argument('--settings',type=Path)
    ap.add_argument('--seed',type=int,default=525);ap.add_argument('--cuda-visible-devices')
    args=ap.parse_args()
    if args.cuda_visible_devices is not None:
        import os
        os.environ['CUDA_VISIBLE_DEVICES']=args.cuda_visible_devices
    root=Path(__file__).resolve().parents[1]/'outputs/eqgpt-research/stage2-preparation-2026-11-16'/args.split
    train=[json.loads(l)['text'] for l in (root/'frozen/train-augmented.jsonl').read_text().splitlines()]
    validation=[json.loads(l)['normalized']['text'] for l in (root/'frozen/validation.jsonl').read_text().splitlines()]
    cfg=json.loads(args.settings.read_text()) if args.settings else dict(DEFAULT_PRETRAIN)
    if args.epochs:cfg['maximum_epochs']=args.epochs
    if args.smoke:
        train=train[:8];validation=validation[:2];cfg.update(maximum_epochs=min(cfg['maximum_epochs'],2),batch_size=4,token_budget=2048)
    generator=ASTBPEGenerator(root/f'upstream/ast-bpe-{args.vocab}.json',device=args.device,seed=args.seed,positions=args.positions,smoke=args.smoke)
    generator.pretrain(train,validation,args.output,cfg,args.resume)


if __name__=='__main__':main()
