"""Cache primary arXiv domain evidence; domain hits are not automatic admission."""
from pathlib import Path
import json,re,hashlib,time
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/eqgpt-research/stage2-corpus-2026-11-15';FOLDER=OUT/'sources';FOLDER.mkdir(exist_ok=True)
def main():
 old=[json.loads(l) for l in (ROOT/'stage2_main_v1/legacy_eqgpt/training_corpus/equations.jsonl').read_text().splitlines()]
 pool=[json.loads(l) for l in (ROOT/'ast_bpe_multifield_v2/data/corpus/review_slate/candidates.jsonl').read_text().splitlines()]
 selected={r['source_group'].split(':',1)[1]:r['title'] for r in old}
 counts={}
 for r in pool:
  family=r.get('family_query','other')
  if family in ['navier_stokes_coupled','fluid_phase']:continue
  if counts.get(family,0)>=6:continue
  if r.get('field_count',0)>4:continue
  ident=r['source_group'].split(':',1)[1]
  if ident not in selected:selected[ident]=r['title'];counts[family]=counts.get(family,0)+1
 registry=[]
 for i,(ident,title) in enumerate(selected.items()):
  safe=ident.replace('/','_');path=FOLDER/(safe+'.html');url='https://arxiv.org/html/'+ident
  if not path.exists():
   try:
    response=requests.get(url,timeout=35)
    if response.status_code!=200:
     registry.append({'id':ident,'title':title,'url':url,'status':response.status_code});time.sleep(3);continue
    path.write_text(response.text)
   except requests.RequestException as e:
    registry.append({'id':ident,'title':title,'url':url,'status':type(e).__name__});continue
   time.sleep(3)
  soup=BeautifulSoup(path.read_text(),'html.parser')
  for math in soup.find_all('math'):
   if math.get('alttext'):math.replace_with(' $'+math['alttext']+'$ ')
  text=soup.get_text(' ',strip=True);(FOLDER/(safe+'.txt')).write_text(text)
  patterns=[r'two[- ]dimensional',r'\\mathbb\s*\{?R\}?\s*\^\s*\{?2',r'\\mathbb\s*\{?R\}?\s*\^\s*\{?[nNdD]',r'\\Omega[^.]{0,160}(?:subset|domain)']
  hits=[]
  for pattern in patterns:
   for m in list(re.finditer(pattern,text,re.I))[:20]:hits.append(text[max(0,m.start()-180):m.end()+300])
  registry.append({'id':ident,'title':title,'url':url,'status':'FETCHED','html_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'text_path':str((FOLDER/(safe+'.txt')).relative_to(ROOT)),'domain_evidence_candidates':hits,'admitted':False})
  (OUT/'source-domain-registry.json').write_text(json.dumps(registry,indent=2,ensure_ascii=False))
  print('SOURCE',i+1,'/',len(selected),ident,'DOMAIN_HITS',len(hits),flush=True)
 (OUT/'source-domain-registry.json').write_text(json.dumps(registry,indent=2,ensure_ascii=False))
 print('SOURCE_DOMAIN_COLLECTION_COMPLETE',len(registry),flush=True)
if __name__=='__main__':main()
