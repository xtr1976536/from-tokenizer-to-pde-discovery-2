"""Further source-reviewed component systems and classical 2D operators."""
from curation import reviewed_model


def build():
    rows = []
    def add(*args, **kwargs):
        rows.append(reviewed_model(*args, **kwargs))

    add('2206.08602', 'S1.EGx2', 'classical-thermoelasticity-fourier',
        [r'u_{tt}-a^2\Delta(u)-(b^2-a^2)(u_{xx}+v_{xy})+\gamma_1 p_x=0',
         r'v_{tt}-a^2\Delta(v)-(b^2-a^2)(u_{xy}+v_{yy})+\gamma_1 p_y=0',
         r'p_t-\kappa\Delta(p)+\gamma_2(u_{xt}+v_{yt})=0'],
        ['u','v','p'], ['x displacement component','y displacement component','temperature difference'],
        'thermoelasticity', 'in the physical dimensions $n=1,2,3$', 'n in {1,2,3}',
        note='Exact Cartesian component expansion of vector displacement (u,v) and scalar temperature p. div u=u_x+v_y.')

    add('2408.17271', 'S2.EGx2', 'two-dimensional-viscous-burgers',
        [r'u_t+\alpha(uu_x+vu_y)-\nu\Delta(u)=0',
         r'v_t+\alpha(uv_x+vv_y)-\nu\Delta(v)=0'],
        ['u','v'], ['x velocity component','y velocity component'],
        'burgers', r'u(x,y,0)', 'Source explicitly defines the two Cartesian components on the x/y unit square',
        kind='native_2d',
        note='Exact component expansion of source vector Burgers PDE. Source initial/boundary data explicitly use x,y in [0,1]^2; no pressure or incompressibility equation is added.')

    add('2102.05093', 'S1.E1', 'kuramoto-sivashinsky-height',
        [r'\psi_t=-\Delta^2(\psi)-\Delta(\psi)-\psi_x^2-\psi_y^2'],
        [r'\psi'], ['flame-front height'], 'kuramoto_sivashinsky',
        r'rectangular domain $[0,L_{1}]\times[0,L_{2}]$',
        'Two-dimensional rectangular periodic domain', kind='native_2d',
        note='Expand the scalar norm |grad psi|^2 exactly as psi_x^2+psi_y^2; retain fourth-order diffusion.')

    add('2604.09530', 'S1.E1', 'swift-hohenberg-cubic',
        [r'u_t=-u-2\Delta(u)-\Delta^2(u)+\mu u-u^3'],
        ['u'], ['real pattern amplitude'], 'swift_hohenberg',
        r'space $\mathbf{x}\in\mathbb{R}^{2}$', 'Native R^2', kind='native_2d',
        note='Use the explicit classical nonlinearity N(u)=-u^3 given immediately after (1.1); expand (1+Delta)^2 linearly, without inventing a new nonlinearity.')
    add('2604.09530', 'A2.E1', 'swift-hohenberg-gradient-quadratic-cubic',
        [r'u_t=-u-2\Delta(u)-\Delta^2(u)+\mu u-\beta(u_x^2+u_y^2)-u^3'],
        ['u'], ['real pattern amplitude'], 'swift_hohenberg',
        r'\Omega=[-4\pi,36\pi]\times[-3\sqrt{3}\pi,3\sqrt{3}\pi]',
        'Explicit 2D rectangle in Appendix B', kind='native_2d',
        note='Explicit Appendix B PDE, not a fabricated parameter sweep. Expand the gradient norm and linear operator exactly.')

    for exponent in (3,5):
        nonlinear = '(u^2+v^2)' if exponent == 3 else '(u^2+v^2)^2'
        add('2201.10195', 'S1.EGx1', f'generalized-davey-stewartson-power-{exponent}',
            [fr'-v_t+\Delta(u)+{nonlinear}u+pu=0',
             fr'u_t+\Delta(v)+{nonlinear}v+pv=0',
             r'\Delta(p)=\partial_{xx}(u^2+v^2)'],
            ['u','v','p'], ['real complex-envelope component','imaginary complex-envelope component','real nonlocal potential'],
            'davey_stewartson', r'(t,\;x)\in\mathbb{R}\times\mathbb{R}^{2}',
            'Native R^2', kind='native_2d',
            note='Exact real/imaginary split varphi=u+i*v; potential p=E_1(|varphi|^2). Fourier symbol xi_1^2/|xi|^2 yields Delta p=partial_xx(u^2+v^2). Preserve the source Fourier/decay prescription as a side condition to fix the harmonic ambiguity.',
            power={'values':{'p':exponent},'source_range_verified':True,'range_statement':'1<p<infinity'})

    # Source magnetization u in S^2 has THREE scalar components, not one.
    fields = ['u','v','p']
    roles = ['x spin component','y spin component','z spin component']
    spin = r'\mathcal{M}=\mathbb{R}^{2}'
    # m x Delta m, with a second exact cross-product expansion for damping.
    cross = [r'v\Delta(p)-p\Delta(v)', r'p\Delta(u)-u\Delta(p)', r'u\Delta(v)-v\Delta(u)']
    double = [fr'v({cross[2]})-p({cross[1]})',
              fr'p({cross[0]})-u({cross[2]})',
              fr'u({cross[1]})-v({cross[0]})']
    add('2301.00168', 'S1.E1', 'landau-lifshitz-precession-damping',
        [fr'{field}_t=\alpha({c})-\beta({d})' for field,c,d in zip(fields,cross,double)],
        fields, roles, 'spin_dynamics', spin, 'Source discusses the same flow for M=R^2',
        kind='native_2d',
        note='Exact three-component cross-product expansion; original unit-spin condition u^2+v^2+p^2=1 remains a source side condition. Coefficients alpha/beta alias source fraktur a_1/a_2.')
    norm = '(u_x^2+u_y^2+v_x^2+v_y^2+p_x^2+p_y^2)'
    add('2301.00168', 'S1.E2', 'harmonic-map-heat-flow-sphere',
        [fr'{field}_t=\Delta({field})+{norm}{field}' for field in fields],
        fields, roles, 'spin_dynamics', spin, 'Same model discussion explicitly includes M=R^2',
        kind='native_2d',
        note='Explicit source harmonic heat-flow equation (1.2), component expansion of |grad m|^2*m. Retain unit-spin side condition from target S^2.')

    return rows
