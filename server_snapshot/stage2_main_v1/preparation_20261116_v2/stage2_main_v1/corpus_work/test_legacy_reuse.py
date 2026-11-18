import unittest
from legacy_pdf_reuse import power_cohort


def member(key,value):
    return {'source_group':'eqworld:npde3107','source_template_latex':'u_{xx}+u_{yy}=f(u)',
            'parameters':{key:value}}


class LegacyReuseTests(unittest.TestCase):
    def test_metadata_call_spelling_cannot_bypass_power_cap(self):
        a,va=power_cohort(member('f','u^2'))
        b,vb=power_cohort(member('f(u)','u^3'))
        c,vc=power_cohort(member('f(u)',r'\sqrt(u)'))
        self.assertEqual(a,b);self.assertEqual(a,c)
        self.assertNotEqual(va,vb);self.assertNotEqual(vb,vc)
    def test_other_function_types_are_distinct(self):
        self.assertNotEqual(power_cohort(member('f',r'\sin(u)'))[0],power_cohort(member('f',r'\sinh(u)'))[0])


if __name__=='__main__':unittest.main()
