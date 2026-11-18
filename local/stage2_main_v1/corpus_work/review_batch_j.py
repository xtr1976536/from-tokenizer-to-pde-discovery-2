"""Explicit planar chemical kinetics, not padded versions of 1D examples."""
from curation import reviewed_model


def build():
    rows=[]
    rows.append(reviewed_model('1501.03769','S2.EGx1','modified-oregonator-constant-illumination',
        [r'u_t=\frac{u-u^2+w(q-u)}{\epsilon}+D_u\Delta(u)',
         r'v_t=u-v',
         r'w_t=\frac{\Phi_0+fv-w(u+q)}{\eta}+D_w\Delta(w)'],
        ['u','v','w'],['activator concentration','immobilised catalyst concentration','inhibitor concentration'],
        'oregonator','an elongated two-dimensional\nchannel of width $L$ in the $y$ -direction',
        'The source computes this model on a 2D x/y domain',kind='native_2d',
        supporting_quotes=(r'\Phi=\Phi_{0}',r'\Phi\left(x,y,t\right)',
                           'two-dimensional\nmodified Oregonator model Eqs. ( 1 )-( 3 )'),
        note='Source explicitly identifies the uncontrolled background illumination Phi=Phi_0. The feedback-controlled spatial function is not erased. Alias the source positive constant tilde-epsilon to eta; retain both mobile species and the immobile catalyst.'))
    rows.append(reviewed_model('2001.11730','S4.E7','brusselator-planar-single-layer',
        [r'X_t=A+X^2Y-BX-X+D_X\Delta(X)',r'Y_t=BX-X^2Y+D_Y\Delta(Y)'],
        ['X','Y'],['first reactant concentration','second reactant concentration'],
        'chemical_pattern_formation',r'planar spatial coordinate ${\bm{x}}=(x,y)$',
        'Native planar x/y coordinates in the same model section',kind='native_2d',
        note='Retain the original concentration variables of (7). The shifted U/V form in (8) is an exact change of variables and is NOT separately counted.'))
    rows.append(reviewed_model('2001.11730','S4.E9','brusselator-planar-two-layers',
        [r'u_t=(B-1)u+A^2v+D_1\Delta(u)+\alpha(p-u)+\frac{B}{A}u^2+2Auv+u^2v',
         r'v_t=-Bu-A^2v+D_2\Delta(v)+\beta(w-v)-\frac{B}{A}u^2-2Auv-u^2v',
         r'p_t=(B-1)p+A^2w+D_3\Delta(p)+\alpha(u-p)+\frac{B}{A}p^2+2Apw+p^2w',
         r'w_t=-Bp-A^2w+D_4\Delta(w)+\beta(v-w)-\frac{B}{A}p^2-2Apw-p^2w'],
        ['u','v','p','w'],['layer-1 shifted U','layer-1 shifted V','layer-2 shifted U','layer-2 shifted V'],
        'multilayer_reaction_diffusion',r'planar spatial coordinate ${\bm{x}}=(x,y)$',
        'Both layers share the source planar x/y domain',kind='native_2d',supporting_anchors=('S4.E8',),
        scalar_parameters=(r'\alpha',r'\beta'),
        note='Rename U_1,V_1,U_2,V_2 simultaneously to u,v,p,w. Expand only the source-defined NLT(U,V)=(B/A)U^2+2*A*U*V+U^2*V from (8). This is a four-scalar-field system; neither layer is dropped.'))
    rows.append(reviewed_model('2205.10755','S3.E44','gray-scott-explicit-planar',
        [r'u_t=\mu_1\Delta(u)-uv^2+k_1(1-u)',r'v_t=\mu_2\Delta(v)+uv^2-(k_1+k_2)v'],
        ['u','v'],['first chemical species','second chemical species'],
        'chemical_pattern_formation',r'(x,y,t)\in\Omega\times[0,T]',
        'Source equation (44) explicitly includes both u_xx+u_yy and v_xx+v_yy',kind='native_2d',scalar_parameters=('k_1',),
        note='Use the explicitly 2D equation (44), not the preceding 1D example (36). The displayed spatial sums are exactly the Cartesian 2D Laplacian.'))
    rows.append(reviewed_model('1711.00976','S7.E4','fitzhugh-nagumo-general-spatial-domain',
        [r'u_t=d_1\Delta(u)-u^3+(1+\beta)u^2-\beta u-v+I',
         r'v_t=d_2\Delta(v)+\varepsilon u-\varepsilon\gamma v'],
        ['u','v'],['membrane potential','sodium-gating variable'],
        'neuronal_reaction_diffusion',r'\Omega$ is a bounded domain in $\mathbb{R}^{n}',
        'The explicit example (7.4) belongs to the general spatial-n framework (2.1)',
        model_dimension_link='this model falls under the general framework proposed',
        note='The source explicitly identifies (7.4) as a specialization of the general-n model (2.1). No 1D numerical example is padded with y. The external stimulus I is a stated source constant.'))
    return rows
