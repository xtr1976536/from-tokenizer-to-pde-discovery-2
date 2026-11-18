"""Independent final integrity checks across corpus, splits, augmentation and vocab artifacts."""
import json,sys,re
from pathlib import Path
from hashlib import sha256
from collections import Counter,defaultdict
from curation import ROOT,OUT
from structure_latex import normalize_system
sys.path.insert(0,str(ROOT/'math_tokenizer_project_release/src'))
from compact_ast_bpe import CompactAlphabet,train_compact,derive_alphabet


def main():
    frozen=OUT/'frozen';up=OUT/'upstream'
    rows=[json.loads(l) for l in (frozen/'base-structures.jsonl').read_text().splitlines()]
    manifest=json.loads((frozen/'split-manifest.json').read_text())
    assert sha256((frozen/'base-structures.jsonl').read_bytes()).hexdigest()==manifest['base_sha256']
    assert len(rows)>=212 and sum(len(r['source_fields'])==3 for r in rows)>=80
    assert len({r['count_key'] for r in rows})==len(rows)
    sets={name:{r['id'] for r in rows if r['split']==name} for name in ('train','validation','test')}
    groups={name:{r['leakage_group'] for r in rows if r['split']==name} for name in sets}
    for a,b in [('train','validation'),('train','test'),('validation','test')]:
        assert not sets[a]&sets[b] and not groups[a]&groups[b]
    powers=defaultdict(set)
    for r in rows:
        if r.get('power_specialization'):powers[r['source_model_group']].add(r['split'])
    assert all(len(s)==1 for s in powers.values())
    aug=[json.loads(l) for l in (frozen/'train-augmented.jsonl').read_text().splitlines()]
    counts=Counter(a['parent_id'] for a in aug)
    assert set(counts)==sets['train'] and max(counts.values())<=32
    parents={r['id']:r for r in rows}
    for a in aug:
        p=parents[a['parent_id']]
        assert a['split']=='train' and p['split']=='train'
        assert normalize_system(a['text'].split(chr(92)*2),p['normalized']['fields'])['text']==p['normalized']['text']
    selection=json.loads((up/'selection.json').read_text())
    assert len(selection['vocab_sizes'])==len(set(selection['vocab_sizes']))==3
    validation=json.loads((up/'validation-sweep.json').read_text())
    expected=sorted([r for r in validation if r['eligible']],key=lambda r:(-r['selection_score'],r['vocab_size']))[:3]
    assert selection['vocab_sizes']==[r['vocab_size'] for r in expected]
    texts=[r['normalized']['text'] for r in rows if r['split']=='train']
    alphabet=derive_alphabet(texts)
    checked=[];sequence_digests={};previous_path=OUT/'final-preparation-checks.json'
    expected_digests=json.loads(previous_path.read_text()).get('token_sequence_sha256',{}) if previous_path.exists() else {}
    for size in selection['vocab_sizes']:
        model=CompactAlphabet.load(up/f'ast-bpe-{size}.json')
        assert len(model.vocab)+3==size and set(alphabet)==model.alphabet
        # Fit this capacity independently to verify ranked-prefix reuse.
        independent=train_compact('ast_bpe',texts,size,alphabet)
        assert model.vocab==independent.vocab
        sequence_hash=sha256()
        for r in rows:
            text=r['normalized']['text'];ids=model.encode(text)
            assert ids==independent.encode(text)
            assert model.decode(ids)==text
            sequence_hash.update((json.dumps(ids,separators=(',',':'))+'\n').encode())
        for a in aug:
            ids=model.encode(a['text']);assert model.decode(ids)==a['text']
            sequence_hash.update((json.dumps(ids,separators=(',',':'))+'\n').encode())
        sequence_digests[str(size)]=sequence_hash.hexdigest()
        if str(size) in expected_digests:assert sequence_hash.hexdigest()==expected_digests[str(size)],('cross-platform token mismatch',size)
        checked.append(size)
    pdf_check=json.loads((OUT/'formula-catalog/qa/report.json').read_text())
    assert pdf_check['status']=='PASS' and pdf_check['source_links']==len(rows)
    digest=sha256((OUT/'reviewed-unique-structures.jsonl').read_bytes()).hexdigest()
    for name in ['reviewed-corpus-audit.json','component-expansion-audit.json','new-component-expansion-audit.json','mathematical-review.json']:
        assert json.loads((OUT/name).read_text())['input_corpus_sha256']==digest
    report=dict(status='PASS',base_structures=len(rows),field_counts=dict(Counter(len(r['source_fields']) for r in rows)),
        split_counts={k:len(v) for k,v in sets.items()},groups_disjoint=True,power_instances_disjoint=True,
        augmented_train_samples=len(aug),all_augmented_samples_reparsed=True,
        selected_vocab_sizes=checked,independent_capacity_refits_match=True,token_sequence_sha256=sequence_digests,
        exact_roundtrip_on_all_base_and_augmented_samples=True,
        formula_pdf_pages=pdf_check['pages'],formula_pdf_source_links=pdf_check['source_links'],
        reviewed_input_sha256=digest,frozen_base_sha256=manifest['base_sha256'],
        mathematical_review_type='agent source-by-source plus47 independent signed symbolic systems; not external human peer review',
        formal_eqgpt_pretraining_started=False,main_experiment_started=False,server_synced=False)
    (OUT/'final-preparation-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
