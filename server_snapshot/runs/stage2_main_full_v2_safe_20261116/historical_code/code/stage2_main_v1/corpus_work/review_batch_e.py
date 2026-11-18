"""Source-supported three-field wave, density, and reservoir closures."""
from curation import reviewed_model


def build():
    rows = []
    def add(*args, **kwargs):
        rows.append(reviewed_model(*args, **kwargs))

    add('0912.1388','S1.Ex1','planar-schrodinger-poisson',
        [r'-v_t+\frac{1}{2}\Delta(u)=\lambda pu',
         r'u_t+\frac{1}{2}\Delta(v)=\lambda pv',
         r'-\Delta(p)=u^2+v^2'],
        ['u','v','p'],['real wavefunction component','imaginary wavefunction component','real Poisson potential'],
        'schrodinger_poisson',r'(t,x)\in\mathbb{R}^{1+2}',
        'Source explicitly separates one time and two spatial dimensions',kind='native_2d',
        note='Exact complex-to-real split of source u and scalar potential P. Source growth/gauge prescription grad P bounded and tending to zero at infinity, P(0)=0, is retained as a side condition. The semiclassical rescaling is not counted as another structure.')

    # Two gamma values total. gamma=2 is deliberately not counted separately:
    # its primitive equations reproduce the nonrotating shallow-water structure.
    for exponent in (3,4):
        add('2407.06455','S1.E1',f'compressible-euler-density-gamma-{exponent}',
            [r'r_t+ur_x+vr_y+r(u_x+v_y)=0',
             fr'u_t+uu_x+vu_y+r^{exponent-2}r_x=0',
             fr'v_t+uv_x+vv_y+r^{exponent-2}r_y=0'],
            ['r','u','v'],['strictly positive density, source rho','x velocity component','y velocity component'],
            'compressible_euler',r'for $d=2$', 'd=2 specialization explicitly discussed following governing model (1.1)',
            dimension_symbol='d',kind='native_2d',
            note='Set source gamma=3 or 4 (source allows gamma>1). Rename rho to r and use continuity to convert conserved momentum to primitive velocity equations, dividing only by the source strictly positive density. This compressible density evolution is structurally different from target incompressible zero-divergence closure. Conservative and primitive forms are not separately counted.',
            power={'values':{'gamma':exponent},'source_range_verified':True,'range_statement':'gamma>1'})

    add('2611.04060','S3.E4','polariton-uniform-incoherent-reservoir',
        [r'-v_t=-\frac{1}{2}\Delta(u)+g(u^2+v^2)u+g_Rpu-\frac{1}{2}(Rp-\gamma_c)v',
         r'u_t=-\frac{1}{2}\Delta(v)+g(u^2+v^2)v+g_Rpv+\frac{1}{2}(Rp-\gamma_c)u',
         r'p_t=P_0-(\gamma_R+R(u^2+v^2))p'],
        ['u','v','p'],['real condensate component','imaginary condensate component','incoherent reservoir density'],
        'driven_dissipative_condensate','The fluid is quasi-two-dimensional:',
        'Author derives a 2D evolution model by freezing the axial profile; this is source-supported 2D, not 1D padding',
        kind='native_2d',scalar_parameters=('g','R'),
        note='Exact real/imaginary split of source (4). Use source explicit None trap V=0 and explicit none/uniform pump profile f=1 from (10); P_0 aliases the constant uniform pump. Optional noise and disorder are absent in displayed deterministic equation (4). No arbitrary unspecified potential is replaced.')

    return rows
