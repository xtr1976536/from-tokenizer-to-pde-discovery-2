"""Read-only inventory of the old PDE corpus; never treat variants as new sources."""
from pathlib import Path
import json,collections,hashlib
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'stage2_main_v1/legacy_eqgpt/training_corpus'
OUT=ROOT/'outputs/eqgpt-research/stage2-corpus-2026-11-15';OUT.mkdir(parents=True,exist_ok=True)
rows=[json.loads(l) for l in (BASE/'equations.jsonl').read_text().splitlines()]
macro={'reaction_diffusion':'reaction_diffusion_and_taxis','cross_diffusion':'reaction_diffusion_and_taxis','chemotaxis':'reaction_diffusion_and_taxis','haptotaxis':'reaction_diffusion_and_taxis','population_competition':'reaction_diffusion_and_taxis','epidemic':'reaction_diffusion_and_taxis','oscillator_reaction_diffusion':'reaction_diffusion_and_taxis','boussinesq':'fluid_or_boussinesq_requires_source_review','forced_boussinesq':'fluid_or_boussinesq_requires_source_review','dispersive':'dispersive'}
result={'old_parent_systems':len(rows),'field_counts':dict(collections.Counter(str(len(r['fields'])) for r in rows)),
 'label_family_counts':dict(collections.Counter(r['family'] for r in rows)),
 'coarse_mechanism_counts':dict(collections.Counter(macro.get(r['family'],r['family']) for r in rows)),
 'three_field_fraction':sum(len(r['fields'])==3 for r in rows)/len(rows),
 'all_published_source_urls_present':all(r.get('source_url') for r in rows),
 'old_coordinate_metadata_not_new_native_2d_proof':True,
 'no_new_corpus_claimed':True,'old_corpus_sha256':hashlib.sha256((BASE/'equations.jsonl').read_bytes()).hexdigest()}
(OUT/'old-corpus-audit.json').write_text(json.dumps(result,indent=2))
# Candidate quarantine only: title matching alone cannot certify target similarity.
quarantine=[]
for r in rows:
 if r['family'] in {'magnetohydrodynamics','boussinesq','forced_boussinesq','shallow_water'} or any(s in r.get('title','').lower() for s in ['navier','stokes','incompressible','vorticity']):
  quarantine.append({'id':r['id'],'family':r['family'],'title':r['title'],'source':r['source_url'],'action':'quarantine pending source-level and structural leakage review; not admitted to new corpus'})
(OUT/'target-related-quarantine.json').write_text(json.dumps(quarantine,indent=2,ensure_ascii=False))
print(json.dumps(result,indent=2));print('QUARANTINED_FOR_REVIEW',len(quarantine))
