"""Reproduce both primary four-metric tables without accessing test formulas."""
import json,sys
from pathlib import Path
from hashlib import sha256
from curation import ROOT
sys.path.insert(0,str(ROOT/'math_tokenizer_project_release/src'))
from compact_ast_bpe import CompactAlphabet,train_compact,derive_alphabet
from run_upstream import evaluate


def main():
    root=ROOT/'outputs/eqgpt-research/stage2-preparation-2026-11-16';reports={}
    for name in ('811','622'):
        base=root/name;manifest=json.loads((base/'frozen/split-manifest.json').read_text())
        # Only train and validation files are read. Test IDs from the manifest
        # suffice to verify separation; test formula payloads remain unopened.
        splits={key:[json.loads(l) for l in (base/'frozen'/f'{key}.jsonl').read_text().splitlines()] for key in ('train','validation')}
        ids=manifest['ids']
        for a,b in [('train','validation'),('train','test'),('validation','test')]:assert not set(ids[a])&set(ids[b])
        train_groups={r['leakage_group'] for r in splits['train']};validation_groups={r['leakage_group'] for r in splits['validation']}
        assert not train_groups&validation_groups
        texts=[r['normalized']['text'] for r in splits['train']];alphabet=derive_alphabet(texts)
        rows=json.loads((base/'upstream/four-metrics.json').read_text());assert [r['vocab_size'] for r in rows]==list(range(64,500,32))
        hashes={}
        for row in rows:
            size=row['vocab_size'];model=CompactAlphabet.load(base/'upstream'/f'ast-bpe-{size}.json')
            fitted=train_compact('ast_bpe',texts,size,alphabet)
            assert fitted.vocab==model.vocab
            assert len(model.vocab)+3==size
            reproduced=evaluate(model,splits['validation'])
            for key,value in reproduced.items():assert row[key]==value,(name,size,key)
            for text in texts:
                ids=model.encode(text);assert ids==fitted.encode(text) and model.decode(ids)==text
            hashes[size]=sha256(json.dumps(model.internal.merges).encode()).hexdigest()
        reports[name]=dict(status='PASS',count=14,train=manifest['counts']['train'],validation=manifest['counts']['validation'],
            test=manifest['counts']['test'],test_formulas_read=False,independent_refits_equal=True,all_four_metrics_reproduced=True,
            no_threshold=True,no_ranking=True,no_selection=True,merge_sha256=hashes)
    (root/'upstream-audit.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(json.dumps({k:{key:value for key,value in r.items() if key!='merge_sha256'} for k,r in reports.items()}))


if __name__=='__main__':main()
