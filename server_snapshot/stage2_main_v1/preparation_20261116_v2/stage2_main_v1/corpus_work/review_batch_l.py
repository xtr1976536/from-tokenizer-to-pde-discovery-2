"""Planar spot/chimera systems and two source-defined memristor laws."""
from curation import reviewed_model


def build():
    rows=[]
    rows.append(reviewed_model('2204.02740','S1.E1','three-component-spots-finite-relaxation',
        [r'u_t=D_u\Delta(u)+k_1u-u^3-k_3v-k_4w+\kappa',
         r'\tau v_t=D_v\Delta(v)+u-v',r'\theta w_t=D_w\Delta(w)+u-w'],
        ['u','v','w'],['activator','first inhibitor','second inhibitor'],
        'three_component_localized_patterns',r'\mathbf{r}\in\mathbb{R}^{2}',
        'Native planar R^2 defining equation',kind='native_2d'))
    rows.append(reviewed_model('2204.02740','S1.E2','three-component-spots-instantaneous-inhibitor',
        [r'u_t=D_u\Delta(u)+k_1u-u^3-k_3v-k_4w+\kappa',
         r'\tau v_t=u-v',r'0=D_w\Delta(w)+u-w'],
        ['u','v','w'],['activator','local dynamic inhibitor','instantaneous inhibitor G^{-1}u'],
        'three_component_localized_patterns',r'\mathbf{r}\in\mathbb{R}^{2}',
        'Source reduced planar model and its defining elliptic Green operator',kind='native_2d',
        supporting_anchors=('S1.E3',),
        note='Source explicitly writes the reduced model (2) with G^{-1}u and defines G=-D_w*Delta+1 in (3). Reintroduce w=G^{-1}u using the exact elliptic equation G*w=u, preserving the original inverse/decay prescription. This is not a new arbitrary closure.'))
    rows.append(reviewed_model('2012.00983','S2.EGx1','three-component-chimera-single-mobile-inhibitor',
        [r'u_t=\phi(au-\alpha u^3-bv-cw)',r'v_t=\phi\epsilon_1(u-v)',
         r'w_t=\phi\epsilon_2(u-w)+D_w\Delta(w)'],
        ['u','v','w'],['activator','local recovery variable','diffusing inhibitor'],
        'oscillatory_reaction_diffusion','two-dimensional spatially continuous RD system',
        'Author explicitly describes the source model as spatially continuous in 2D',kind='native_2d',
        supporting_quotes=(r'D_{u}=D_{v}=0',),
        note='Use the author explicitly studied single-component-diffusion regime D_u=D_v=0,D_w>0. The omission of these diffusion terms is a stated physical regime, not an artificial coefficient sweep.'))
    for law in ('quadratic','tanh'):
        mem = r'(c+\gamma\rho+\delta\rho^2)' if law=='quadratic' else r'\tanh(\rho)'
        rows.append(reviewed_model('2208.06012','S1.EGx1','memristive-hindmarsh-rose-'+law,
            [r'u_t=\eta\Delta(u)+au^2-bu^3+v-w+J_e-k_1'+mem+'u',
             r'v_t=\alpha-\beta u^2-v',r'w_t=q(u-a_0)-rw',r'\rho_t=u-k_2\rho'],
            ['u','v','w',r'\rho'],['membrane potential','fast ion transport/spiking variable','slow ion transport/bursting variable','memductance'],
            'memristive_neurodynamics',r'\Omega\subset\mathbb{R}^{n}$ ( $n\leq 3$ )',
            'Source positive spatial dimension n<=3 includes 2',scalar_parameters=('q','k_1'),
            supporting_anchors=('S1.E5',),
            supporting_quotes=(() if law=='quadratic' else (r'\varphi(\rho)=\tanh(\rho)',)),
            note='Source supplies the quadratic memristor law (1.5) and explicitly states that the alternative tanh(rho) law is covered. Substitute only those two stated laws. Alias the constant reference potential u_e to a_0 before parsing to distinguish it from a derivative subscript. Keep all four scalar state equations.'))
    return rows
