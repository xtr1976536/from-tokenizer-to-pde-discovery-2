"""Re-audit existing Stage1 members against original, explicitly steady source PDFs.

No new function choices are generated. Generic x/y first-order equations are
not admitted merely because their variable names look spatial.
"""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sympy as sp
from curation import ROOT,OUT,implementation_fingerprints
from structure_latex import normalize_system
from equivalence import key as equivalent_key
from direct_parser import parse
from dimension_evidence import validate as validate_dimension
from leakage_guard import reasons

RELEASE=ROOT/'math_tokenizer_project_release'
CATALOG=RELEASE/'data/formulas/diverse636_revision/sources636.jsonl'
ALLOWED={'npde3101','npde3102','npde3107','npde3201','npde3301','npde3303','lpde302','lpde303'}


def text_cache(pdf,stem):
    output=OUT/'legacy-pdf-evidence'/(stem+'.txt')
    output.parent.mkdir(exist_ok=True)
    if not output.exists():subprocess.run(['pdftotext','-layout',str(pdf),str(output)],check=True)
    return output,output.read_text()


def function_choices(record):
    result={}
    for key,value in record.get('parameters',{}).items():
        if not isinstance(value,str) or key=='constant_policy':continue
        key=re.sub(r'\s+','',key).lstrip('\\')
        if '(' not in key:key+='(u)'
        result[key]=value
    return result


def instantiate(record):
    text=record['source_template_latex']
    for name,value in sorted(function_choices(record).items(),key=lambda item:-len(item[0])):
        names=[name] if '(' in name else [name+'(u)']
        for call in names:
            text=text.replace('\\'+call,'('+value+')').replace(call,'('+value+')')
    for name,value in record.get('parameters',{}).items():
        if isinstance(value,(int,float)):
            text=re.sub(r'(?<![A-Za-z\\])'+re.escape(name)+r'(?![A-Za-z])','('+str(value)+')',text)
    return text


def profile_expression(node):
    kind=node[0]
    if kind=='v':return sp.Symbol(node[1],real=True)
    if kind=='n':return sp.Rational(str(node[1]))
    if kind=='neg':return -profile_expression(node[1])
    if kind=='add':return sum(profile_expression(c) for c in node[1:])
    if kind=='mul':return sp.prod(profile_expression(c) for c in node[1:])
    if kind=='div':return profile_expression(node[1])/profile_expression(node[2])
    if kind=='pow':return profile_expression(node[1])**profile_expression(node[2])
    if kind=='fn':return {'abs':sp.Abs,'ln':sp.log}.get(node[1],getattr(sp,node[1],None))(profile_expression(node[2]))
    raise ValueError('A declared function profile cannot contain an undeclared operator')


def power_cohort(record):
    values={};shapes=[]
    def shape(expr,path,base=False):
        if expr.is_Number:return ('number',str(expr))
        if expr.is_Pow:
            if not expr.exp.is_Number:raise ValueError('Unspecified power remains in an inherited profile')
            skeleton=shape(expr.base,path+'.base',True)
            values[path+'.power']=float(expr.exp)
            return ('power',skeleton,'?')
        if expr.is_Symbol:
            if base:return ('variable',str(expr))
            values[path+'.power']=1
            return ('power',('variable',str(expr)),'?')
        if expr.func in (sp.Add,sp.Mul):return (str(expr.func),tuple(shape(c,path+'.'+str(i)) for i,c in enumerate(expr.args)))
        skeleton=(str(expr.func),tuple(shape(c,path+'.arg'+str(i)) for i,c in enumerate(expr.args)))
        if base:return skeleton
        values[path+'.power']=1
        return ('power',skeleton,'?')
    for name,value in sorted(function_choices(record).items()):
        ast,parameters=parse(value,('u',))
        if parameters:raise ValueError('Unspecified symbol in inherited function choice')
        shapes.append((name,shape(sp.expand(profile_expression(ast)),name)))
    exponents=re.findall(r'\^(?:\{([^}]+)\}|([A-Za-z]))',record['source_template_latex'])
    exponent_text=' '.join(a or b for a,b in exponents)
    for name,value in record.get('parameters',{}).items():
        if isinstance(value,(int,float)) and re.search(r'(?<![A-Za-z\\])'+re.escape(name)+r'(?![A-Za-z])',exponent_text):values['parameter.'+name]=value
    cohort=record['source_group']+'#fixed-functional-form:'+sha256(repr(shapes).encode()).hexdigest()[:16]
    return cohort,values


def reviewed_pdf_member(record,source_index):
    stem=record['source_group'].split(':')[1]
    pdf=RELEASE/record['source_file']
    pdf_digest=sha256(pdf.read_bytes()).hexdigest()
    if pdf_digest!=record['source_sha256']:raise ValueError('Original source PDF hash differs from legacy provenance')
    text_path,text=text_cache(pdf,stem)
    files=[{'path':str(pdf.relative_to(ROOT)),'sha256':pdf_digest,'role':'original governing formula PDF',
            'text_path':str(text_path.relative_to(ROOT)),'text_sha256':sha256(text_path.read_bytes()).hexdigest()}]
    if stem in ('npde3101','npde3102','npde3201'):
        toc=RELEASE/'data/formulas/diverse_pde_v4/sources/npde-toc3.pdf'
        proof_path,proof=text_cache(toc,'npde-toc3')
        files.append({'path':str(toc.relative_to(ROOT)),'sha256':sha256(toc.read_bytes()).hexdigest(),'role':'original elliptic/stationary chapter index',
                      'text_path':str(proof_path.relative_to(ROOT)),'text_sha256':sha256(proof_path.read_bytes()).hexdigest()})
        statement='Second-Order Elliptic Partial Differential Equations'
        excerpt={'npde3101':'aw + bwn','npde3102':'awn + bw2n','npde3201':'Anisotropic heat/diffusion equation.'}[stem]
    else:
        proof_path,proof=text_path,text
        patterns={'npde3107':r'This is a stationary[^.]+\.', 'npde3303':r'This is a stationary[^.]+\.',
                  'npde3301':r'Stationary[^.]+\.', 'lpde302':r'The two-dimensional Poisson equation has the following form:',
                  'lpde303':r'The two-dimensional Helmholtz equation has the following form:'}
        match=re.search(patterns[stem],proof)
        if match is None:raise ValueError('Explicit stationary/two-dimensional source statement missing')
        statement=match.group()
        position=proof.find('∂')
        if position<0:raise ValueError('Primary governing derivative display is missing')
        excerpt=proof[position:position+100]
    if statement not in proof or excerpt not in proof:raise ValueError('Source dimension/first-equation link is missing')
    original=record['original_latex']
    normal=normalize_system([original],['u'])
    check=normalize_system([instantiate(record)],['u'])
    if equivalent_key(normal['residual_support_ast'],normal['fields'])!=equivalent_key(check['residual_support_ast'],check['fields']):
        raise ValueError('Existing member does not match its declared source template/function substitution')
    target=reasons(normal['residual_support_ast'],normal['fields'])
    if target:raise ValueError('Target or near-target structure')
    cohort,values=power_cohort(record)
    snapshot=OUT/'legacy-source-records'/(record['source_id'].split(':')[-1]+'.json')
    snapshot.parent.mkdir(exist_ok=True)
    snapshot.write_text(json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    row={'id':'reuse-stage1-'+record['source_id'].split(':')[-1],
         'source_group':record['source_group'],'source_model_group':cohort,'split_group':record['source_group'],
         'source_url':record['source_url'],'source_title':'EqWorld / '+stem,
         'source_format':'primary_pdf_legacy_member','primary_source_files':files,
         'legacy_snapshot_path':str(snapshot.relative_to(ROOT)),'legacy_snapshot_sha256':sha256(snapshot.read_bytes()).hexdigest(),
         'legacy_catalog_path':str(CATALOG.relative_to(ROOT)),'legacy_catalog_sha256':sha256(CATALOG.read_bytes()).hexdigest(),
         'legacy_catalog_index':source_index,'source_template_latex':record['source_template_latex'],
         'instantiated_template_latex':instantiate(record),'source_function_choices':function_choices(record),
         'latex_origin':'inherited_declared_source_family_member_not_claimed_literal_published_instance',
         'source_fields':['u'],'scalar_component_roles':['scalar planar stationary field; original source dependent variable w'],
         'reviewed_transcription':[original],'explicit_scalar_parameters':[],'family':record.get('broad_family',record['family']),
         'implementation_sha256':implementation_fingerprints(),
         'normalized':normal,'structure_key':__import__('structure_latex').structure_key(normal['residual_support_ast'],normal['fields']),
         'leakage_review_reasons':[],'review_status':'SOURCE_REVIEWED_PENDING_SECOND_AUDIT',
         'domain_conditions':record.get('domain_conditions','x>0,y>0,u>0 where needed for roots or inverse powers'),
         'transformation_note':'Existing Stage1 LaTeX member reused directly. Source PDF and its stationary/elliptic classification have been re-read; original w is globally renamed to u. Only previously declared function choices are carried forward. Particular exact-solution subcase restrictions are not claimed as governing-model restrictions.',
         'dimension_evidence':{'kind':'native_2d','spatial_dimension':2,
             'source_file':str(proof_path.relative_to(ROOT)),'source_file_sha256':sha256(proof_path.read_bytes()).hexdigest(),
             'verbatim_dimension_statement':statement,'model_context_start':0,'model_context_end':len(proof),
             'equation_evidence':excerpt,'reviewed_context_role':'governing_model',
             'source_dimension_condition':'Explicit stationary/elliptic planar x/y source formula; t is absent, not renamed from either axis'}}
    if values:row['power_specialization']={'values':values,'source_range_verified':True,
        'range_statement':'Existing source-defined family member on its stated domain; at most two existing exponent assignments for the same fixed non-power functional form'}
    validate_dimension(row,ROOT)
    return row


def build():
    records=[json.loads(line) for line in CATALOG.read_text().splitlines()]
    accepted=[];decisions=[];bindings=defaultdict(set)
    for index,record in enumerate(records):
        stem=record.get('source_group','').split(':')[-1]
        if stem not in ALLOWED:continue
        try:
            cohort,values=power_cohort(record)
            binding=tuple(sorted(values.items()))
            if binding not in bindings[cohort] and len(bindings[cohort])>=2:
                decisions.append({'source_id':record['source_id'],'status':'HELD_POWER_CAP','reason':'Two existing exponent assignments for the same fixed functional form already retained'})
                continue
            row=reviewed_pdf_member(record,index)
            bindings[cohort].add(binding)
            accepted.append(row)
            decisions.append({'source_id':record['source_id'],'status':'SOURCE_REVIEWED','id':row['id']})
        except (ValueError,TypeError,KeyError,IndexError) as error:
            decisions.append({'source_id':record['source_id'],'status':'HELD_REVIEW','reason':str(error)})
    (OUT/'legacy-stage1-pdf-reuse-decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+'\n')
    print('Stage1 PDF family members reviewed:',len(accepted),'held:',len(decisions)-len(accepted))
    return accepted
