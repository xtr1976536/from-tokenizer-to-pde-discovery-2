"""Validate reviewed source evidence, without inferring dimension from keywords.

Reviewers bind the dimensional statement to the actual model, not to a theorem
or bibliography entry. A cached full-text hash makes that review reproducible.
"""
from hashlib import sha256
from pathlib import Path


def validate(record, root):
    evidence = record['dimension_evidence']
    kind = evidence['kind']
    if kind not in ('native_2d', 'general_n_includes_2'):
        raise ValueError('Only source-supported spatial 2D is admitted')
    source = (Path(root) / evidence['source_file']).resolve()
    if not source.is_relative_to(Path(root).resolve()):
        raise ValueError('Evidence file must be inside the source cache')
    raw = source.read_bytes()
    if sha256(raw).hexdigest() != evidence['source_file_sha256']:
        raise ValueError('Source evidence hash changed')
    text = raw.decode('utf-8')
    statement = evidence['verbatim_dimension_statement']
    if not statement.strip() or statement not in text:
        raise ValueError('Dimension statement must occur verbatim in cached source')
    start = evidence['model_context_start']
    end = evidence['model_context_end']
    if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(text):
        raise ValueError('Invalid reviewed model-context span')
    context = text[start:end]
    if statement not in context:
        raise ValueError('Dimension statement is outside the reviewed model context')
    if evidence['equation_evidence'] not in context or not evidence['equation_evidence'].strip():
        raise ValueError('Equation and dimension must be linked in the reviewed context')
    if evidence['reviewed_context_role'] != 'governing_model':
        raise ValueError('Bibliography, related work and theorem hits are not model evidence')
    if evidence['spatial_dimension'] != 2:
        raise ValueError('Corpus target has two spatial dimensions, excluding time')
    if kind == 'general_n_includes_2':
        if evidence['source_dimension_symbol'] not in ('n', 'N', 'd', 'D'):
            raise ValueError('Need the original spatial-dimension symbol')
        if not evidence['source_dimension_condition'].strip():
            raise ValueError('Need the original admissible dimension condition')
        if evidence['n2_allowed_by_original_definition'] is not True:
            raise ValueError('Source model must explicitly admit the 2D specialization')
    components = record['scalar_component_roles']
    if len(components) != len(record['source_fields']) or not 1 <= len(components) <= 4:
        raise ValueError('Count scalar components after vector/complex decomposition')
    if any(not role.strip() for role in components):
        raise ValueError('Every scalar component needs a source role')
    return {'spatial_dimension': 2, 'kind': kind, 'source_sha256': evidence['source_file_sha256']}
