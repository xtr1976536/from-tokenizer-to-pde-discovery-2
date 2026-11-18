"""One literal planar elliptic combustion equation, with original PDF evidence."""
from hashlib import sha256
from curation import ROOT,OUT,implementation_fingerprints
from legacy_pdf_reuse import text_cache,RELEASE
from structure_latex import normalize_system,structure_key
from dimension_evidence import validate


def build():
    files=[]
    for name,role in [('npde3103','original combustion governing formula'),('npde-toc3','original elliptic chapter classification')]:
        p=RELEASE/'data/formulas/diverse_pde_v4/sources'/(name+'.pdf')
        q,t=text_cache(p,name)
        files.append(dict(path=str(p.relative_to(ROOT)),sha256=sha256(p.read_bytes()).hexdigest(),role=role,
                          text_path=str(q.relative_to(ROOT)),text_sha256=sha256(q.read_bytes()).hexdigest()))
    proof=ROOT/files[1]['text_path'];text=proof.read_text()
    normal=normalize_system([r'u_{xx}+u_{yy}=A\exp(u)'],['u'])
    row=dict(id='liouville-planar-stationary-combustion',source_group='eqworld:npde3103',
             source_model_group='eqworld:npde3103#governing',split_group='eqworld:npde3103',
             source_url='https://eqworld.ipmnet.ru/en/solutions/npde/npde3103.pdf',
             source_title='EqWorld: second-order elliptic combustion equation',source_format='primary_pdf_transcribed',
             primary_source_files=files,original_source_equation=r'w_{xx}+w_{yy}=a\exp(\beta w)',
             reviewed_transcription=[r'u_{xx}+u_{yy}=A\exp(u)'],source_fields=['u'],
             scalar_component_roles=['scalar planar stationary combustion field'],explicit_scalar_parameters=[],
             family='elliptic_exponential_combustion',normalized=normal,
             structure_key=structure_key(normal['residual_support_ast'],normal['fields']),
             implementation_sha256=implementation_fingerprints(),leakage_review_reasons=[],
             review_status='SOURCE_REVIEWED_PENDING_SECOND_AUDIT',
             transformation_note='Exact nonzero-beta field-unit change u=beta*w, A=a*beta; no coordinate is time and no inner nonlinear coefficient is set arbitrarily. Original equation lies in the source second-order elliptic chapter; the page explicitly identifies combustion theory. No exact solution is counted as a governing PDE.',
             dimension_evidence=dict(kind='native_2d',spatial_dimension=2,source_file=str(proof.relative_to(ROOT)),
                 source_file_sha256=sha256(proof.read_bytes()).hexdigest(),verbatim_dimension_statement='Second-Order Elliptic Partial Differential Equations',
                 model_context_start=0,model_context_end=len(text),equation_evidence='aeβw',
                 reviewed_context_role='governing_model',source_dimension_condition='Explicit x/y elliptic source formula and original chapter classification'))
    validate(row,ROOT)
    return [row]
