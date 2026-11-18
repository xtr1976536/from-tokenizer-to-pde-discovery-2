import unittest
from structure_latex import normalize_system
from equivalence import key


def count_key(text):
    row=normalize_system([text],['u'])
    return key(row['residual_support_ast'],row['fields'])


class EquivalenceTests(unittest.TestCase):
    def test_laplacian_is_not_extra_structure(self):
        self.assertEqual(count_key(r'u_t=\Delta(u)+u^3'),count_key(r'u_t=u_{xx}+u_{yy}+u^3'))
    def test_product_rule_is_not_extra_structure(self):
        self.assertEqual(count_key(r'u_t=\partial_x(u u_x)+\partial_y(u u_y)'),
                         count_key(r'u_t=u u_{xx}+u_x^2+u u_{yy}+u_y^2'))
    def test_fitted_columns_do_not_cancel_each_other(self):
        self.assertNotEqual(count_key(r'u_t=\partial_x(\exp(-u))+\exp(-u)u_x'),count_key(r'u_t=0'))
    def test_spatial_dimension_and_power_matter(self):
        self.assertNotEqual(count_key(r'u_t=\Delta(u)+u^2'),count_key(r'u_t=\Delta(u)+u^3'))


if __name__=='__main__':unittest.main()
