import unittest
from power_policy import validate


def row(a, b):
    return {'source_model_group': 'model-1', 'split_group': 'model-1',
            'power_specialization': {'source_range_verified': True,
                                     'range_statement': 'a,b>1', 'values': {'a': a, 'b': b}}}


class PowerPolicyTests(unittest.TestCase):
    def test_two_total_combinations_allowed(self):
        self.assertEqual(validate([row(2, 3), row(3, 4)])['instance_counts']['model-1'], 2)

    def test_per_parameter_cartesian_expansion_rejected(self):
        with self.assertRaises(ValueError):
            validate([row(2, 2), row(2, 3), row(3, 2), row(3, 3)])

    def test_split_and_missing_source_evidence_rejected(self):
        value = row(2, 3)
        value['split_group'] = 'other'
        with self.assertRaises(ValueError):
            validate([row(3, 4), value])
        value = row(2, 3)
        value['power_specialization']['source_range_verified'] = False
        with self.assertRaises(ValueError):
            validate([value])


if __name__ == '__main__':
    unittest.main()
