"""Build an auditable corpus from explicit, source-reviewed model declarations.

Search hits and parser successes never enter this builder automatically.
"""
from pathlib import Path
from hashlib import sha256
import json
from functools import lru_cache
from bs4 import BeautifulSoup
from structure_latex import normalize_system, structure_key
from dimension_evidence import validate as validate_dimension
from leakage_guard import reasons as leakage_reasons
from power_policy import validate as validate_power_policy
from ast_runtime import expand_laplacian

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/eqgpt-research/stage2-corpus-2026-11-15'


def implementation_fingerprints():
    names=('curation.py','direct_parser.py','structure_latex.py','latex_render.py','equivalence.py','legacy_pdf_reuse.py',
           'leakage_guard.py','dimension_evidence.py','power_policy.py')
    return {name:sha256((Path(__file__).parent/name).read_bytes()).hexdigest() for name in names}


@lru_cache(maxsize=64)
def source_cache(ident):
    html_path = OUT / 'sources' / (ident + '.html')
    text_path = OUT / 'sources' / (ident + '.txt')
    return html_path, text_path, BeautifulSoup(html_path.read_text(), 'html.parser'), text_path.read_text()


def math_evidence(node):
    """Read literal mathematics supplied by the original source provider."""
    arxiv = [math['alttext'] for math in node.select('math[alttext]')]
    if arxiv:
        return arxiv
    return [span.get_text().strip() for span in node.select('.tex-math')]


def occurrences(text,needle):
    result=[];position=0
    while True:
        position=text.find(needle,position)
        if position<0:return result
        result.append(position);position+=1


def reviewed_model(ident, anchor, name, equations, fields, roles, family,
                   dimension_statement, condition, dimension_symbol='n', kind='general_n_includes_2',
                   note='', equation_math_index=0, power=None, scalar_parameters=(), model_dimension_link='',
                   supporting_anchors=(), supporting_quotes=(), source_url=None, source_group=None,
                   original_model_key=None):
    html_path, text_path, soup, text = source_cache(ident)
    node = soup.find(id=anchor)
    if node is None:
        raise ValueError(f'{ident}: source equation anchor {anchor} missing')
    maths = math_evidence(node)
    evidence = maths[equation_math_index]
    support = []
    for support_anchor in supporting_anchors:
        support_node = soup.find(id=support_anchor)
        if support_node is None:
            raise ValueError(f'{ident}: supporting formula {support_anchor} missing')
        support.append({'anchor':support_anchor,
                        'mathml_alttext':math_evidence(support_node)})
    if any(quote not in text for quote in supporting_quotes):
        raise ValueError(f'{ident}: supporting source statement missing')
    # Pair the exact model formula with its dimensional definition in full text.
    # Prefer the body over an abstract duplicate by choosing the later tied pair.
    positions = occurrences(text,evidence)
    statements = occurrences(text,dimension_statement)
    if not positions or not statements:
        raise ValueError(f'{ident}: exact equation or dimension quote missing from source text')
    # Bind repeated formulas to the selected HTML node. A short heat equation
    # may occur in several tables; proximity to an introduction must not pick
    # a different occurrence from the explicitly reviewed row.
    local_maths=node.select('math[alttext]')
    exact_positions=occurrences(text,'$'+evidence+'$')
    if local_maths:
        all_maths=soup.select('math[alttext]')
        matched=[math for math in all_maths if math['alttext']==evidence]
        chosen=local_maths[equation_math_index]
        ordinal=next(i for i,math in enumerate(matched) if math is chosen)
        bound=exact_positions[ordinal]+1 if len(exact_positions)==len(matched) else None
    else:
        matched=[span for span in soup.select('.tex-math') if span.get_text().strip()==evidence]
        chosen=node.select('.tex-math')[equation_math_index]
        ordinal=next(i for i,span in enumerate(matched) if span is chosen)
        bound=positions[ordinal] if len(positions)==len(matched) else None
    if bound is None:
        if len(positions)!=1:raise ValueError(f'{ident}: repeated formula cannot be bound to its selected HTML anchor')
        bound=positions[0]
    eqpos=bound
    dimpos=min(statements,key=lambda position:abs(position-eqpos))
    start = max(0, min(eqpos, dimpos) - 200)
    end = min(len(text), max(eqpos+len(evidence), dimpos+len(dimension_statement)) + 200)
    if model_dimension_link and model_dimension_link not in text[start:end]:
        nearby = [i for i in range(max(0,eqpos-4000),min(len(text),eqpos+len(evidence)+4000))
                  if text.startswith(model_dimension_link,i)]
        if nearby:
            linkpos = min(nearby,key=lambda i:abs(i-eqpos))
            start = min(start,linkpos)
            end = max(end,linkpos+len(model_dimension_link))
    if model_dimension_link and model_dimension_link not in text[start:end]:
        raise ValueError(f'{ident}: explicit model/dimension cross-reference is not in source context')
    if end-start > 16000 and not model_dimension_link:
        raise ValueError(f'{ident}: model/dimension link too remote; review a closer source statement')
    group = source_group or 'arxiv:' + ident
    row = {
        'id': name, 'source_group': group, 'source_cache_id': ident,
        'source_model_group': group + '#' + (original_model_key or anchor),
        'split_group': group,
        'source_url': (source_url or 'https://arxiv.org/html/' + ident) + '#' + anchor,
        'source_title': soup.title.get_text(' ', strip=True),
        'source_html_sha256': sha256(html_path.read_bytes()).hexdigest(),
        'implementation_sha256': implementation_fingerprints(),
        'source_format':'html_math',
        'equation_locator': anchor, 'original_mathml_alttext': maths,
        'supporting_equation_evidence': support,
        'supporting_source_quotes': list(supporting_quotes),
        'source_fields': fields, 'scalar_component_roles': roles,
        'reviewed_transcription': equations, 'family': family,
        'explicit_scalar_parameters': list(scalar_parameters),
        'transformation_note': note or 'Governing rows transcribed; boundary and initial data retained in source evidence, excluded from structural training.',
        'dimension_evidence': {
            'kind': kind, 'spatial_dimension': 2,
            'source_file': str(text_path.relative_to(ROOT)),
            'source_file_sha256': sha256(text_path.read_bytes()).hexdigest(),
            'verbatim_dimension_statement': dimension_statement,
            'source_dimension_symbol': dimension_symbol,
            'source_dimension_condition': condition,
            'n2_allowed_by_original_definition': True,
            'model_context_start': start, 'model_context_end': end,
            'equation_evidence': evidence,
            'equation_context_binding':'selected HTML math-node occurrence',
            'reviewed_context_role': 'governing_model',
            'explicit_model_dimension_link': model_dimension_link,
        },
    }
    if power:
        row['power_specialization'] = power
    validate_dimension(row, ROOT)
    row['normalized'] = normalize_system(equations, fields, scalar_parameters)
    # A gradient is vector-valued and cannot silently become one scalar field.
    for ast in row['normalized']['residual_support_ast']:
        expand_laplacian(ast, ('x', 'y'))
    row['structure_key'] = structure_key(row['normalized']['residual_support_ast'], row['normalized']['fields'])
    row['leakage_review_reasons'] = leakage_reasons(row['normalized']['residual_support_ast'], row['normalized']['fields'])
    if row['leakage_review_reasons']:
        raise ValueError(f'{name}: target-related structure: {row["leakage_review_reasons"]}')
    row['review_status'] = 'SOURCE_REVIEWED_PENDING_SECOND_AUDIT'
    return row


def save(rows):
    from equivalence import key as count_key
    validate_power_policy(rows)
    unique, duplicates = {}, []
    for row in rows:
        key = count_key(row['normalized']['residual_support_ast'],row['normalized']['fields'])
        row['count_key']=key
        if key in unique:
            duplicates.append({'id': row['id'], 'same_structure_as': unique[key]['id'],
                               'source_url': row['source_url']})
        else:
            unique[key] = row
    lock=OUT/'locked-four-field-structures.json'
    if lock.exists():
        expected=json.loads(lock.read_text())
        actual={row['id']:row['structure_key'] for row in unique.values() if len(row['normalized']['fields'])==4}
        if any(actual.get(ident)!=key for ident,key in expected.items()):
            raise ValueError('The ten existing four-field structures must be preserved; new sourced systems may be added')
    (OUT / 'reviewed-source-models.jsonl').write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    (OUT / 'reviewed-unique-structures.jsonl').write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in unique.values()))
    (OUT / 'reviewed-duplicate-structures.json').write_text(json.dumps(duplicates, indent=2, ensure_ascii=False) + '\n')
    print(f'Reviewed declarations: {len(rows)}; unique structures: {len(unique)}; duplicates: {len(duplicates)}')
