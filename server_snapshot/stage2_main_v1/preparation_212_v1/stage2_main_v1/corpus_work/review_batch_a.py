"""Explicit primary-source declarations, reviewed against cached full texts.

Every entry records the original complete display, field roles, spatial evidence,
and any component decomposition. This is a growing review batch, not a quota.
"""
from curation import reviewed_model, save


def build():
    rows = []
    def add(*args, **kwargs):
        rows.append(reviewed_model(*args, **kwargs))

    add('2508.01436', 'S1.EGx2', 'indirect-signalling-ppp',
        [r'\partial_t(n)=\Delta(n)-\nabla\cdot(n\nabla(c))',
         r'\varepsilon\partial_t(c)=\Delta(c)-c+w',
         r'\varepsilon\partial_t(w)=\tau\Delta(w)-w+n'],
        ['n','c','w'], ['cell density','primary chemical concentration','indirect signal concentration'],
        'chemotaxis', r'\Omega\subset\mathbb{R}^{N}$ , $1\leq N\leq 4', '1<=N<=4', 'N')

    for anchor, name, eqs in [
        ('S1.E1', 'reversible-reaction-full-diffusion',
         [r'a_t-d_a\Delta(a)=c-ab',r'b_t-d_b\Delta(b)=c-ab',r'c_t-d_c\Delta(c)=ab-c']),
        ('S1.E2', 'reversible-reaction-immobile-second',
         [r'a_t-d_a\Delta(a)=c-ab',r'b_t=c-ab',r'c_t-d_c\Delta(c)=ab-c']),
        ('S1.E3', 'reversible-reaction-immobile-product',
         [r'a_t-d_a\Delta(a)=c-ab',r'b_t-d_b\Delta(b)=c-ab',r'c_t=ab-c'])]:
        add('2406.18339', anchor, name, eqs, ['a','b','c'],
            ['first reactant concentration','second reactant concentration','product concentration'],
            'mass_action_reaction_diffusion', r'\Omega\subset\mathbb{R}^{N}',
            'General spatial N in model definition; N=2 is included', 'N')

    add('1811.09343', 'S1.EGx2', 'two-species-signal-consumption',
        [r'u_t=\Delta(u)-\chi_1\nabla\cdot(u\nabla(w))',
         r'v_t=\Delta(v)-\chi_2\nabla\cdot(v\nabla(w))',
         r'w_t=\Delta(w)-(\alpha u+\beta v)w'],
        ['u','v','w'], ['first species density','second species density','consumed chemical concentration'],
        'chemotaxis', r'\Omega\subset\mathbb{R}^{n}$ ( $n\geq 2$ )', 'n>=2')

    add('2604.26905', 'S1.EGx1', 'alopecia-classical-sensitivity',
        [r'u_t=\Delta(u)-\chi_1\nabla\cdot(u\nabla(w))+w-\mu_1 u^2',
         r'v_t=\Delta(v)-\chi_2\nabla\cdot(v\nabla(w))+w+ruv-\mu_2 v^2',
         r'w_t=\Delta(w)+u+v-w'],
        ['u','v','w'], ['CD4 T-cell density','CD8 T-cell density','IFN-gamma concentration'],
        'chemotaxis', r'\Omega\subset\mathbb{R}^{n}$ $(n\geq 1)$', 'n>=1')

    add('1503.00283', 'S1.E1', 'rotating-shallow-water',
        [r'u_t+uu_x+vu_y+g\phi_x-fv=0',
         r'v_t+uv_x+vv_y+g\phi_y+fu=0',
         r'\phi_t+u\phi_x+v\phi_y+\phi(u_x+v_y)=0'],
        ['u','v',r'\phi'], ['horizontal x velocity','horizontal y velocity','water height'],
        'shallow_water', r'(x,y)\in\Omega:=(0,L_{1})\times(0,L_{2})', 'Cartesian rectangle in x,y',
        kind='native_2d')

    add('1201.0498', 'S2.EGx1', 'nonrotating-shallow-water',
        [r'u_t+uu_x+vu_y+h_x=0',r'v_t+uv_x+vv_y+h_y=0',r'h_t+uh_x+vh_y+h(u_x+v_y)=0'],
        ['u','v','h'], ['horizontal x velocity','horizontal y velocity','water height'],
        'shallow_water', r'u_{t}+uu_{x}+vu_{y}+h_{x}=0',
        'Both independent x/y axes explicitly appear in complete defining system', kind='native_2d')

    add('1209.3194', 'S1.E1', 'linearized-rotating-shallow-water',
        [r'u_t+a_0 u_x+b_0 u_y+g\phi_x-fv=0',
         r'v_t+a_0 v_x+b_0 v_y+g\phi_y+fu=0',
         r'\phi_t+a_0\phi_x+b_0\phi_y+c_0(u_x+v_y)=0'],
        ['u','v',r'\phi'], ['x velocity perturbation','y velocity perturbation','height perturbation'],
        'shallow_water', r'(x,y)\in\Omega:=(0,L_{1})\times(0,L_{2})',
        'Cartesian rectangle in x,y', kind='native_2d',
        scalar_parameters=('a_0','b_0','c_0'),
        note='Source explicitly identifies u_0,v_0,phi_0 as positive constants. Alias them to a_0,b_0,c_0 before removing outer scalar coefficients; they are not derivatives or extra fields.')

    add('1508.03407', 'S2.EGx1', 'three-component-chimera-partial-diffusion',
        [r'X_t=\phi(aX-\alpha X^3-bY-cZ)+D_X\Delta(X)',
         r'Y_t=\phi\epsilon_1(X-Y)',
         r'\tau Z_t=\phi\epsilon_2(X-Z)+D_Z\Delta(Z)'],
        ['X','Y','Z'], ['activator concentration','local inhibitor concentration','diffusing inhibitor concentration'],
        'oscillatory_reaction_diffusion', 'a three-component RD system in two spatial dimensions',
        'Native two spatial dimensions', kind='native_2d')

    add('1812.04440', 'S1.E1', 'farmer-hunter-gatherer-spreading',
        [r'F_t=\Delta(F)+aF(1-F-C)',
         r'C_t=\Delta(C)+C(1-F-C)+sH(F+C)',
         r'H_t=d\Delta(H)+bH(1-H-g(F+C))'],
        ['F','C','H'], ['initial farmers density','converted farmers density','hunter-gatherer density'],
        'population_competition', r'general space dimension $N\geq 1$', 'N>=1', 'N',
        scalar_parameters=('g',))

    add('2312.08147', 'S0.EGx1', 'rival-gangs-saturating-graffiti',
        [r'u_t=D_u\Delta(u)+\chi_u\nabla\cdot(u\nabla(w))',
         r'v_t=D_v\Delta(v)+\chi_v\nabla\cdot(v\nabla(z))',
         r'w_t=-w+\frac{v}{1+v}',r'z_t=-z+\frac{u}{1+u}'],
        ['u','v','w','z'], ['first gang density','second gang density','first graffiti field','second graffiti field'],
        'cross_diffusion', r'\Omega\subset\mathbb{R}^{n},n\in\{1,2,3\}',
        'n in {1,2,3}; theorem explicitly covers the same governing model')

    # Split psi=u+i*v, phi=p in the source KGS system. No new field is appended.
    add('1910.06612', 'S1.EGx1', 'cubic-quadratic-klein-gordon-schrodinger',
        [r'-v_t+\Delta(u)=p^2u-pu',r'u_t+\Delta(v)=p^2v-pv',
         r'p_{tt}-\Delta(p)+p=-2(u^2+v^2)p+u^2+v^2'],
        ['u','v','p'], ['real part of source psi','imaginary part of source psi','real source phi'],
        'klein_gordon_schrodinger', 'in space dimensions $n=2$ and $n=3$', 'n=2 or n=3',
        note='Exact real/imaginary split psi=u+i*v, phi=p; Box=partial_tt-Delta. Source scalar-component count is three.')

    add('0807.3400', 'S1.E1', 'zakharov-schrodinger-wave',
        [r'-v_t+\Delta(u)=pu',r'u_t+\Delta(v)=pv',r'p_{tt}-\Delta(p)=\Delta(u^2+v^2)'],
        ['u','v','p'], ['real part of source complex u','imaginary part of source complex u','real ion density n'],
        'zakharov', r'where $\triangle$ is the Laplacian in $\mathbb{R}^{2}$',
        'Native R^2', kind='native_2d',
        note='Exact real/imaginary split of the complex envelope; ion wave equation retains second time derivative. No artificial fourth variable.')

    for p in (3,5):
        add('1610.09883', 'S1.E1', f'semilinear-coupled-power-{p}-3',
            [fr'u_t=\Delta(u)+v^{p}',r'v_t=\mu\Delta(v)+u^3'],
            ['u','v'], ['first real parabolic field','second real parabolic field'],
            'semilinear_parabolic', r'for all $p,q>1$ and $N\geq 1$', 'N>=1', 'N',
            note='Source p=3 or 5, q=3. Odd integer powers give |v|^(p-1)v=v^p exactly on the entire real line.',
            power={'values':{'p':p,'q':3},'source_range_verified':True,'range_statement':'p,q>1'})

    add('2607.25177', 'S2.E2', 'phase-field-crystal-mixed',
        [r'\phi_t=\Delta(\mu)',r'\mu=\phi^3+(1-r)\phi+2\Delta(\phi)+\Delta^2(\phi)'],
        [r'\phi',r'\mu'], ['density field','chemical potential'], 'phase_field_crystal',
        'both the Cahn–Hilliard\nand PFC equations in two spatial dimensions',
        'Paper explicitly uses the defining PFC model in two spatial dimensions', kind='native_2d')

    return rows


if __name__ == '__main__':
    save(build())
