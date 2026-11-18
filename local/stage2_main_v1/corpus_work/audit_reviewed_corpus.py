"""Two distinct audit passes for the growing reviewed batch; no quota inflation."""
from collections import Counter
from hashlib import sha256
import json
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from curation import ROOT, OUT, math_evidence
from dimension_evidence import validate as validate_dimension
from power_policy import validate as validate_power
from structure_latex import normalize_system, structure_key, nodes
from equivalence import key as count_key
from task_gate import validate as validate_task


def main():
    rows = [json.loads(line) for line in (OUT / 'reviewed-unique-structures.jsonl').read_text().splitlines()]
    checks = []
    # Pass 1: independently reload evidence and reproduce structural normalization.
    for row in rows:
        for filename,digest in row['implementation_sha256'].items():
            assert sha256((Path(__file__).parent/filename).read_bytes()).hexdigest() == digest, ('implementation changed; rebuild first',filename)
        validate_dimension(row, ROOT)
        original = normalize_system(row['reviewed_transcription'], row['source_fields'], row['explicit_scalar_parameters'])
        assert original['text'] == row['normalized']['text'], row['id']
        assert structure_key(original['residual_support_ast'], original['fields']) == row['structure_key'], row['id']
        assert count_key(original['residual_support_ast'],original['fields'])==row['count_key'],row['id']
        canonical = normalize_system(original['equations'], original['fields'])
        assert canonical['text'] == original['text'], ('non-idempotent normalization', row['id'])
        if len(original['fields']) == 3 and len(original['equations']) == 3:
            validate_task(original['text'])
        checks.append(row['id'])
    cap_report = validate_power(rows)
    assert len({row['count_key'] for row in rows})==len(rows),'Equivalent differential supports counted twice'
    # Pass 2: reload ORIGINAL HTML/PDF evidence, never just the legacy labels.
    checked_pdfs=set()
    for row in rows:
        if row.get('source_format')=='primary_pdf_transcribed':
            for evidence in row['primary_source_files']:
                path=ROOT/evidence['path'];text_path=ROOT/evidence['text_path']
                assert sha256(path.read_bytes()).hexdigest()==evidence['sha256'],row['id']
                assert sha256(text_path.read_bytes()).hexdigest()==evidence['text_sha256'],row['id']
                regenerated=subprocess.run(['pdftotext','-layout',str(path),'-'],check=True,capture_output=True).stdout.decode()
                assert regenerated==text_path.read_text(),row['id']
            continue
        if row.get('source_format')=='primary_pdf_legacy_member':
            from legacy_pdf_reuse import instantiate,function_choices,power_cohort
            snapshot_path=ROOT/row['legacy_snapshot_path']
            assert sha256(snapshot_path.read_bytes()).hexdigest()==row['legacy_snapshot_sha256'],row['id']
            snapshot=json.loads(snapshot_path.read_text())
            catalog_path=ROOT/row['legacy_catalog_path']
            assert sha256(catalog_path.read_bytes()).hexdigest()==row['legacy_catalog_sha256'],row['id']
            assert json.loads(catalog_path.read_text().splitlines()[row['legacy_catalog_index']])==snapshot,row['id']
            assert row['source_template_latex']==snapshot['source_template_latex'],row['id']
            assert row['source_function_choices']==function_choices(snapshot),row['id']
            expected=normalize_system([instantiate(snapshot)],['u'])
            assert count_key(expected['residual_support_ast'],expected['fields'])==row['count_key'],row['id']
            for evidence in row['primary_source_files']:
                path=ROOT/evidence['path'];text_path=ROOT/evidence['text_path']
                assert sha256(path.read_bytes()).hexdigest()==evidence['sha256'],row['id']
                assert sha256(text_path.read_bytes()).hexdigest()==evidence['text_sha256'],row['id']
                if str(path) not in checked_pdfs:
                    regenerated=subprocess.run(['pdftotext','-layout',str(path),'-'],check=True,capture_output=True).stdout
                    assert regenerated.decode('utf-8')==text_path.read_text(),row['id']
                    checked_pdfs.add(str(path))
            continue
        ident = row['source_cache_id']
        path = OUT / 'sources' / (ident + '.html')
        assert sha256(path.read_bytes()).hexdigest() == row['source_html_sha256'], row['id']
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        node = soup.find(id=row['equation_locator'])
        assert node is not None, row['id']
        assert math_evidence(node) == row['original_mathml_alttext'], row['id']
        for support in row.get('supporting_equation_evidence',[]):
            node = soup.find(id=support['anchor'])
            assert node is not None, row['id']
            assert math_evidence(node) == support['mathml_alttext'], row['id']
        source_text = (OUT/'sources'/(ident+'.txt')).read_text()
        assert all(quote in source_text for quote in row.get('supporting_source_quotes',[])), row['id']
    report = {
        'status': 'GROWING_REVIEWED_BATCH_CHECKS_PASSED_NOT_FINAL_CORPUS',
        'pass_1': 'source-dimension evidence, normalization reproducibility/idempotence, 3-field task gate, exponent caps',
        'pass_2': 'original HTML anchors and formulas; original PDF hashes and independently regenerated text; old catalog snapshots and exact declared-function membership',
        'reviewed_unique_structures': len(rows),
        'original_model_definitions': len({row['source_model_group'] for row in rows}),
        'source_papers': len({row['source_group'] for row in rows if row['source_group'].startswith(('arxiv:','doi:'))}),
        'source_documents': len({row['source_group'] for row in rows}),
        'source_formats': dict(Counter(row.get('source_format','html_math') for row in rows)),
        'field_counts': dict(Counter(len(row['normalized']['fields']) for row in rows)),
        'three_field_fraction': sum(len(row['normalized']['fields']) == 3 for row in rows) / len(rows),
        'family_counts': dict(Counter(row['family'] for row in rows)),
        'power_policy': cap_report,
        'minimum_required': 212, 'target': 1000,
        'minimum_met': len(rows) >= 212, 'target_met': len(rows) >= 1000,
        'frozen_for_training': False,
        'formal_training_started': False,
        'three_field_count_target_met':sum(len(row['normalized']['fields'])==3 for row in rows)>=80,
        'four_field_originals_preserved':all(any(row['id']==ident and row['structure_key']==key for row in rows) for ident,key in json.loads((OUT/'locked-four-field-structures.json').read_text()).items()),
        'input_corpus_sha256': sha256((OUT/'reviewed-unique-structures.jsonl').read_bytes()).hexdigest(),
        'limitations': ['Automated audits do not replace independent mathematical peer review of each transcription.',
                       'Family labels require a final coarse-mechanism diversity audit after collection.',
                       'Only the explicitly reviewed batch is counted; search hits and augmentation are excluded.'],
    }
    audited=[]
    for row in rows:
        row=dict(row)
        row['review_status']='SOURCE_AND_STRUCTURE_AUDITED_BATCH_NOT_FROZEN'
        audited.append(row)
    audit_path=OUT/'audited-structures.jsonl'
    audit_path.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in audited))
    report['audited_snapshot_sha256']=sha256(audit_path.read_bytes()).hexdigest()
    (OUT / 'reviewed-corpus-audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({key: report[key] for key in ('reviewed_unique_structures','original_model_definitions','source_papers','field_counts','minimum_met','target_met')},ensure_ascii=False))


if __name__ == '__main__':
    main()
