import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from dimension_evidence import validate


class DimensionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        text = 'Model: u_t=Delta u+v, v_t=Delta v. Domain R^n, n>=1. References: two-dimensional.'
        (self.root / 'source.txt').write_text(text)
        self.record = {
            'source_fields': ['u', 'v'],
            'scalar_component_roles': ['first concentration', 'second concentration'],
            'dimension_evidence': {
                'kind': 'general_n_includes_2',
                'source_file': 'source.txt',
                'source_file_sha256': hashlib.sha256(text.encode()).hexdigest(),
                'verbatim_dimension_statement': 'Domain R^n, n>=1.',
                'model_context_start': 0,
                'model_context_end': text.index('References:'),
                'equation_evidence': 'u_t=Delta u+v, v_t=Delta v.',
                'reviewed_context_role': 'governing_model',
                'spatial_dimension': 2,
                'source_dimension_symbol': 'n',
                'source_dimension_condition': 'n>=1',
                'n2_allowed_by_original_definition': True,
            },
        }

    def test_explicit_general_dimension_specialization(self):
        self.assertEqual(validate(self.record, self.root)['spatial_dimension'], 2)

    def test_bibliography_hit_does_not_supply_dimension(self):
        self.record['dimension_evidence']['verbatim_dimension_statement'] = 'two-dimensional'
        with self.assertRaises(ValueError):
            validate(self.record, self.root)

    def test_dimension_excludes_2_or_counts_time(self):
        for field, value in [('n2_allowed_by_original_definition', False), ('spatial_dimension', 1)]:
            record = copy.deepcopy(self.record)
            record['dimension_evidence'][field] = value
            with self.assertRaises(ValueError):
                validate(record, self.root)

    def test_source_revision_and_vector_count(self):
        record = copy.deepcopy(self.record)
        record['scalar_component_roles'].append('unexpanded vector component')
        with self.assertRaises(ValueError):
            validate(record, self.root)
        (self.root / 'source.txt').write_text('changed')
        with self.assertRaises(ValueError):
            validate(self.record, self.root)


if __name__ == '__main__':
    unittest.main()
