"""Source-reviewed transport, cross-diffusion, reaction, and memory systems."""
from curation import reviewed_model


def build():
    rows = []
    def add(*args, **kwargs):
        rows.append(reviewed_model(*args, **kwargs))

    add('2104.03389', 'S1.EGx1', 'velocity-coupled-wave-pair',
        [r'u_{tt}-\Delta(u)+bv_t=0',r'v_{tt}-a\Delta(v)-bu_t=0'],
        ['u','v'], ['first displacement field','second displacement field, source y'],
        'coupled_wave', r'\mathbb{R}^{d}$ , $d\geq 2$', 'd>=2', 'd',
        note='Rename dependent source field y to v before selecting Cartesian x/y axes. Governing interior equations only; source fractional boundary feedback is a boundary condition, not a new interior PDE.')

    for anchor,name,eqs in [
        ('S1.E1','haptotaxis-virus-with-tissue-remodelling',
         [r'u_t=D_u\Delta(u)-\xi_u\nabla\cdot(u\nabla(v))+\mu_u u(1-u)-\rho_u uz',
          r'v_t=-(\alpha_u u+\alpha_w w)v+\mu_v v(1-v)',
          r'w_t=D_w\Delta(w)-\xi_w\nabla\cdot(w\nabla(v))-\delta_w w+\rho_w uz',
          r'z_t=D_z\Delta(z)-\delta_z z-\rho_z uz+\beta w']),
        ('S1.E2','haptotaxis-virus-no-infected-cell-taxis',
         [r'u_t=D_u\Delta(u)-\xi_u\nabla\cdot(u\nabla(v))+\mu_u u(1-u)-\rho uz',
          r'v_t=-(\alpha_u u+\alpha_w w)v',
          r'w_t=D_w\Delta(w)-w+uz',r'z_t=D_z\Delta(z)-z-uz+\beta w'])]:
        add('2111.08378',anchor,name,eqs,['u','v','w','z'],
            ['uninfected cancer-cell density','extracellular matrix density','infected cancer-cell density','virus density'],
            'haptotaxis',r'\Omega\subset{\mathbb{R}}^{2}', 'Native bounded 2D domain',kind='native_2d')

    for anchor,name,eqs in [
        ('S1.Ex1','irreversible-first-order-conversion',
         [r'a_t-d_a\Delta(a)=-ka',r'b_t-d_b\Delta(b)=ka']),
        ('S1.Ex2','reversible-first-order-conversion',
         [r'a_t-d_a\Delta(a)=-k_1a+k_2b',r'b_t-d_b\Delta(b)=k_1a-k_2b'])]:
        add('1812.07707',anchor,name,eqs,['a','b'],['first chemical concentration','second chemical concentration'],
            'mass_action_reaction_diffusion',r'an open subset of $\mathbb{R}^{d}$',
            'General spatial d in the governing model definition', 'd')

    for anchor,name,second in [('S1.E1','skt-full-cross-diffusion',r'v_t=\Delta((d_2+a_{21}u+a_{22}v)v)+v(a_2-b_2u-c_2v)'),
                               ('S1.E3','skt-triangular-cross-diffusion',r'v_t=\Delta((d_2+a_{22}v)v)+v(a_2-b_2u-c_2v)')]:
        add('1311.6828',anchor,name,
            [r'u_t=\Delta((d_1+a_{11}u+a_{12}v)u)+u(a_1-b_1u-c_1v)',second],
            ['u','v'],['first species density','second species density'], 'cross_diffusion',
            r'\mathbb{R}^{n}$ with $n\geq 2$', 'n>=2')

    add('2106.07038','S0.Ex1','attraction-repulsion-dual-consumption',
        [r'u_t=\Delta(u)-\chi\nabla\cdot(u\nabla(v))+\xi\nabla\cdot(u\nabla(w))',
         r'v_t=\Delta(v)-uv',r'w_t=\Delta(w)-uw'],
        ['u','v','w'],['cell density','attractant concentration','repellent concentration'], 'chemotaxis',
        r'\mathbb{R}^{n}$ , with $n\geq 2$', 'n>=2',equation_math_index=1)

    add('2106.07038','S1.E2','attraction-single-signal-consumption',
        [r'u_t=\Delta(u)-\chi\nabla\cdot(u\nabla(v))',r'v_t=\Delta(v)-uv'],
        ['u','v'],['cell density','consumed attractant concentration'], 'chemotaxis',
        r'\mathbb{R}^{n}$ , with $n\geq 2$', 'n>=2')

    return rows
