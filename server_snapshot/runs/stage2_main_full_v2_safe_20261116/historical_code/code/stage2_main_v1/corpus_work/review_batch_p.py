"""Reuse two-field legacy models after source-level spatial-role review."""
from curation import reviewed_model


def build():
    rows=[]
    def add(*args,**kwargs):rows.append(reviewed_model(*args,**kwargs))
    add('2109.07146','S1.E1','legacy-skt-repulsive-cross-diffusion-no-reaction',
        [r'u_t=\Delta(d_1u+a_{12}uv)',r'v_t=\Delta(d_2v+a_{21}uv)'],
        ['u','v'],['first population density','second population density'],'cross_diffusion',
        r'space variable $x\in\mathbb{T}^{d}$','General spatial dimension d on a periodic torus; choose d=2','d')
    add('2403.00391','S1.E1','legacy-polynomial-cross-self-diffusion-no-reaction',
        [r'u_t=\Delta((d_1+a_1u+b_1v)u)',r'v_t=\Delta((d_2+a_2u+b_2v)v)'],
        ['u','v'],['first population density','second population density'],'cross_diffusion',
        r'the torus $\mathbf{T}^{d}$','Original governing framework is on a general spatial torus T^d; select d=2','d',
        supporting_quotes=('polynomials of two variables with real nonnegative coefficients',),
        note='Reuse the existing old Stage2 linear p(u,v),q(u,v) choices. These are explicit polynomials in the original permitted class and vanish at the origin; do not fabricate new choices. Both time-evolution rows are kept. Generic source class membership is distinguished from a literally written member.')
    add('1901.04278','S1.E2','legacy-irreversible-annihilation-two-species',
        [r'u_t=d_1\Delta(u)-kuv',r'v_t=d_2\Delta(v)-kuv'],
        ['u','v'],['first reactant','second reactant'],'mass_action_reaction_diffusion',
        r'\Omega\subset\mathbb{R}^{d}\ (d\in\mathbb{N})','Any positive spatial d, select d=2','d')
    add('1601.05992','S2.Ex15','legacy-autocatalytic-conversion-two-species',
        [r'a_t-d_a\Delta(a)=-a^2+ab',r'b_t-d_b\Delta(b)=a^2-ab'],
        ['a','b'],['first chemical concentration','second chemical concentration'],'mass_action_reaction_diffusion',
        r'\Omega\subset\mathbb{R}^{n}$ is a bounded domain','General spatial n; Example 2 uses the same domain defined at (1.1)',
        model_dimension_link=r'a_{t}-d_{a}\Delta a=-a^{2}+ab')
    add('2105.08272','S1.E3','legacy-two-species-logistic-competition',
        [r'u_t=d_1\Delta(u)+b_1u(1-u-a_1v)',r'v_t=d_2\Delta(v)+b_2v(1-v-a_2u)'],
        ['u','v'],['first competing population','second competing population'],'population_competition',
        r'\Omega\subset\mathbb{R}^{n}$ with smooth boundary, where $n\geq 1$', 'n>=1')
    add('2504.04166','S1.E1','legacy-two-species-symbiotic-cross-diffusion',
        [r'u_t=d_1\Delta(u)+\alpha\nabla\cdot(v^2\nabla(\frac{u}{v}))+u(a_1-b_1u+c_1v)',
         r'v_t=d_2\Delta(v)+\beta\nabla\cdot(u^2\nabla(\frac{v}{u}))+v(a_2+b_2u-c_2v)'],
        ['u','v'],['first symbiotic population','second symbiotic population'],'cross_diffusion',
        r'\Omega\,(\subset\mathbb{R}^{N})','General positive spatial N; select N=2','N',
        note='Retain exact nonlinear ratio fluxes and their positive-density domain. Product-rule expansion is used only for deduplication; it is not counted again as another model.')
    for anchor,model,react1,react2 in [
        ('S0.EGx2','gierer-meinhardt',r'\frac{u^2}{v}-u+\sigma',r'\mu(u^2-v)'),
        ('S0.EGx3','lengyel-epstein',r'\sigma b(v-\frac{uv}{1+v^2})',r'a-v-\frac{4uv}{1+v^2}')]:
        add('0812.4623','S0.EGx1','legacy-electric-field-'+model,
            [r'u_t=D\Delta(u)+z_2EDu_x+'+react1,r'v_t=\Delta(v)+z_1Ev_x+'+react2],
            ['u','v'],['first ionic concentration, source A','second ionic concentration, source B'],
            'electrodiffusive_chemical_patterns',r'\exp{(ik_{2}y)}',
            'Source evolves two transverse x/y coordinates with independent spatial Fourier y dependence and electric drift along x',kind='native_2d',
            supporting_anchors=(anchor,'S0.E9'),scalar_parameters=('b',r'\mu'),
            note='Use the source explicitly defined '+model+' reaction kinetics. A,B are simultaneously renamed u,v; the electric drift coefficients z_2*E*D and z_1*E remain constants and are not spatial axes. Full original PDE plus y-mode definition establishes 2D; no one-dimensional profile equation is promoted.')
    for anchor,name,source in [
        ('S1.EGx1','without-logistic',False),('S1.EGx4','with-logistic',True)]:
        first=r'u_t=\Delta(u)-\chi\nabla\cdot(\frac{u}{v}\nabla(v))'
        if source:first+=r'+ru-\mu u^2'
        add('2003.03016',anchor,'legacy-singular-sensitivity-'+name,
            [first,r'v_t=\Delta(v)-v+u'],['u','v'],['cell density','strictly positive signal'],'chemotaxis',
            r'\Omega\subset\mathbb{R}^{n}$','Source discusses the fully parabolic precursor for n>=2',
            supporting_quotes=(r'n\geq 2',),
            note='Reuse existing Stage2 literal logarithmic/singular-sensitivity structure. For the generalized logistic row retain only the existing k=2 member; no new power instance is generated. The source distinguishes parabolic and elliptic signal branches.')
    return rows
