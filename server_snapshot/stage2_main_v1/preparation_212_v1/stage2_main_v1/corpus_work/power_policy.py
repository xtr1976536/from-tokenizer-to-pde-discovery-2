"""Source-supported exponent specializations: at most TWO total per model."""
from collections import defaultdict


def validate(rows, maximum=2):
    seen = defaultdict(set)
    split_groups = {}
    for row in rows:
        binding = row.get('power_specialization')
        if not binding:
            continue
        if not binding.get('source_range_verified'):
            raise ValueError('Exponent values lack reviewed source-range evidence')
        if not binding.get('range_statement', '').strip():
            raise ValueError('Original exponent range must be recorded')
        group = row['source_model_group']
        if group in split_groups and split_groups[group] != row['split_group']:
            raise ValueError('All specializations must share their original model group')
        split_groups[group] = row['split_group']
        values = binding['values']
        if not values or any(not isinstance(v, (int, float)) for v in values.values()):
            raise ValueError('Need concrete structural exponent values')
        seen[row['source_model_group']].add(tuple(sorted(values.items())))
        if len(seen[row['source_model_group']]) > maximum:
            raise ValueError('More than two total exponent instances from one original model')
    return {'maximum_per_original_model': maximum,
            'instance_counts': {key: len(value) for key, value in sorted(seen.items())}}
