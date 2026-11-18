"""Two exponent instances per explicit cyclic/HOI three-species model."""
from curation import reviewed_model


def build():
    rows=[]
    for q,l,r in [(2,2,2),(3,2,2)]:
        rows.append(reviewed_model('2510.27555','S3.E1',f'cyclic-power-reaction-{q}-{l}-{r}',
            [fr'u_t-d_1\Delta(u)=v^{l}-u^{q}',
             fr'v_t-d_2\Delta(v)=w^{r}-Bv^{l}',
             fr'w_t-d_3\Delta(w)=Au^{q}-Cw^{r}'],
            ['u','v','w'],['first nonnegative species','second nonnegative species','third nonnegative species'],
            'cyclic_reaction_diffusion',r'Let $N\in\mathbb{N}$ , and $\Omega\subset\mathbb{R}^{N}',
            'Arbitrary positive N; Example 1 is a direct application of the same Theorem 1', 'N',
            model_dimension_link='As all the assumptions of Theorem 1 are fulfilled.',
            supporting_quotes=(r'l,q,r\geq 1',),
            note='Source Example 1 defines l,q,r>=1 and positive A,B,C with A<min(B,C). Keep these original coefficient constraints as provenance. Choose exactly TWO total exponent triples, not all Cartesian combinations. General spatial N is inherited through the explicit application of Theorem 1.',
            power={'values':{'q':q,'l':l,'r':r},'range_statement':'l,q,r>=1','source_range_verified':True}))
    for g1,g2,g3 in [(1,1,1),(2,1,1)]:
        rows.append(reviewed_model('2510.27555','S3.E11',f'three-species-hoi-lotka-volterra-{g1}-{g2}-{g3}',
            [fr'u_t-d_1\Delta(u)=\tau_1u+u^{g1}(a_{{11}}u^{g1}+a_{{12}}v^{g2}+a_{{13}}w^{g3})',
             fr'v_t-d_2\Delta(v)=\tau_2v+v^{g2}(a_{{21}}u^{g1}+a_{{22}}v^{g2}+a_{{23}}w^{g3})',
             fr'w_t-d_3\Delta(w)=\tau_3w+w^{g3}(a_{{31}}u^{g1}+a_{{32}}v^{g2}+a_{{33}}w^{g3})'],
            ['u','v','w'],['first interacting species','second interacting species','third interacting species'],
            'lotka_volterra_higher_order', 'in arbitrary spatial dimensions',
            'Example 3 explicitly states arbitrary spatial dimensions; select N=2', 'N',
            supporting_quotes=(r'\gamma_{i}\geq 1',),
            note='Use the explicit higher-order-interaction model (3.11), with the source sub-skew-symmetric coefficient-matrix restrictions retained as provenance. Both exponent triples satisfy gamma_i>=1. This does not assign arbitrary functions in Example 2.',
            power={'values':{'gamma_1':g1,'gamma_2':g2,'gamma_3':g3},'range_statement':'gamma_i>=1','source_range_verified':True}))
    return rows
