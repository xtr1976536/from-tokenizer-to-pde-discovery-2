"""Collect primary-source equation evidence, never auto-admit search hits."""
import json,hashlib,time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/eqgpt-research/stage2-corpus-2026-11-15';SOURCES=OUT/'sources';SOURCES.mkdir(exist_ok=True)
IDS=['2301.00168','2608.09491','2510.27555','1503.00283','1412.2637','2309.02786','2208.06558','2204.09632','1208.3848','2611.03134']
def main():
 evidence=[];registry=[]
 for ident in IDS:
  path=SOURCES/(ident+'.html');url='https://arxiv.org/html/'+ident
  if not path.exists():
   try:
    r=requests.get(url,timeout=40)
    if r.status_code!=200:registry.append({'id':ident,'status':r.status_code,'url':url});time.sleep(3);continue
    path.write_text(r.text)
   except requests.RequestException as exc:registry.append({'id':ident,'status':type(exc).__name__,'url':url});continue
   time.sleep(3)
  soup=BeautifulSoup(path.read_text(),'html.parser');title=soup.title.get_text(' ',strip=True) if soup.title else ident
  text=soup.get_text(' ',strip=True)
  for index,node in enumerate(soup.select('.ltx_equation,.ltx_equationgroup')):
   maths=node.select('math[alttext]');latex='\n'.join(m.get('alttext','') for m in maths)
   if not latex or not any(s in latex for s in ['\\partial','\\Delta','\\nabla']):continue
   parent=node.parent;context=parent.get_text(' ',strip=True)[:1800]
   evidence.append({'source_group':'arxiv:'+ident,'source_url':url,'title':title,'source_file':str(path.relative_to(ROOT)),
     'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'equation_anchor':node.get('id'),'equation_index':index,'raw_mathml_alttext':latex,
     'context':context,'status':'primary evidence candidate; dimensionality/completeness/normalization/leakage not yet adjudicated'})
  registry.append({'id':ident,'status':'DOWNLOADED','url':url,'title':title,'bytes':path.stat().st_size})
  print(ident,'EVIDENCE',sum(r['source_group']=='arxiv:'+ident for r in evidence),flush=True)
 (OUT/'new-source-registry.json').write_text(json.dumps(registry,indent=2,ensure_ascii=False))
 (OUT/'new-primary-equation-evidence.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in evidence))
if __name__=='__main__':main()
