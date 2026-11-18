"""Additional source-written structural variants; no coefficient sweeps."""
from curation import reviewed_model


def build():
    rows = []
    def add(*args, **kwargs):
        rows.append(reviewed_model(*args, **kwargs))

    add('1811.09343','S1.EGx4','two-species-consumption-with-competition',
        [r'u_t=\Delta(u)-\chi_1\nabla\cdot(u\nabla(w))+\mu_1u(1-u-a_1v)',
         r'v_t=\Delta(v)-\chi_2\nabla\cdot(v\nabla(w))+\mu_2v(1-a_2u-v)',
         r'w_t=\Delta(w)-(\alpha u+\beta v)w'],
        ['u','v','w'],['first competing population','second competing population','consumed chemical'],
        'chemotaxis',r'\Omega\subset\mathbb{R}^{n}$ $(n\geq 2)$','n>=2')

    add('2510.14728','S1.EGx1','four-component-predator-prey-alarm-signal',
        [r'u_t=d_1\Delta(u)-\chi_1\nabla\cdot(u\nabla(vw))+\mu_1u(1-u+a_1v+a_2w)',
         r'v_t=d_2\Delta(v)-\chi_2\nabla\cdot(v\nabla(z))+\mu_2v(1-v-a_3u+a_4w)',
         r'w_t=d_3\Delta(w)+\xi\nabla\cdot(w\nabla(z))+\mu_3w(1-w-a_5u-a_6v)',
         r'z_t=d_4\Delta(z)+\alpha v+\beta w-\gamma z'],
        ['u','v','w','z'],['first population density','second population density','third population density','alarm signal'],
        'predator_prey_taxis',r'\Omega\subset\mathbb{R}^{n}(n\geq 1)',
        'n>=1; Theorem 1.1 explicitly addresses the same system (1), with 2D numerical examples')

    add('2510.14728','S1.EGx6','three-level-food-chain-ratio-dependent',
        [r'u_t=d_1\Delta(u)+\mu_1u(1-u)-b_1uv-b_3\frac{uw}{u+w}',
         r'v_t=d_2\Delta(v)-\xi\nabla\cdot(v\nabla(u))+\mu_2v(1-v)+uv-b_2vw',
         r'w_t=d_3\Delta(w)-\chi\nabla\cdot(w\nabla(uv))+\mu_3w(1-w)+vw+c_3\frac{uw}{u+w}'],
        ['u','v','w'],['prey density','primary predator density','secondary predator density'],
        'predator_prey_taxis','Neumann heat semigroup technique in two spatial dimensions',
        'Explicit 2D description adjoining this complete displayed model',kind='native_2d',
        note='Source reproduces the complete Jin et al. model with its explicit 2D context; ratio-dependent interaction is retained, not replaced by a polynomial.')

    add('1711.00976','S7.E3','lengyel-epstein-pattern-system',
        [r'u_t=\Delta(u)+a-u-\frac{4uv}{1+u^2}',
         r'v_t=\sigma c\Delta(v)+\sigma b(u-\frac{uv}{1+u^2})'],
        ['u','v'],['activator concentration','inhibitor concentration'],
        'chemical_pattern_formation',r'\Omega$ is a bounded domain in $\mathbb{R}^{n}',
        'General spatial n in system (2.1); (7.3) is an explicit parameter/function specialization',
        scalar_parameters=('b',),
        model_dimension_link='Substituting these parameters in system ( 2.1 )',
        note='Use the explicitly written Lengyel-Epstein system (7.3), not an invented f/g. The source explicitly obtains it by substitution in the general-n governing model (2.1); the source 1D simulation is not used as the dimensional proof.')

    return rows
