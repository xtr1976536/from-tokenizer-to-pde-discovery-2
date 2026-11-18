"""Previously collected Stage1 formulas rechecked against their actual space/time roles."""
import json
from curation import reviewed_model, OUT


def build():
    rows=[]
    held=[]
    def add(*args,**kwargs):
        try:rows.append(reviewed_model(*args,**kwargs))
        except (ValueError,KeyError,IndexError,TypeError) as error:
            held.append({'id':args[2],'source':args[0],'status':'HOLD_SOURCE_RECHECK','reason':str(error)})
    # These are the two specific legacy members, not all eight classified powers.
    for power,anchor in [(5,'S6.EGx37'),(3,'S7.EGx52')]:
        add('2407.10356',anchor,'reuse-stage1-kolmogorov-degree-'+str(power),
            [fr'u_t+xu_y=x^{power}u_{{xx}}'],['u'],['real scalar field on the source two-coordinate spatial/state domain'],
            'kolmogorov_degenerate_diffusion','(1+2)-dimensional Kolmogorov backward equations',
            'The source explicitly separates one evolution coordinate t and two non-time coordinates x,y',kind='native_2d',
            model_dimension_link='Following Remark 1',original_model_key='S1.EGx1-F-beta',
            power={'values':{'beta':power},'source_range_verified':True,'range_statement':'Original source explicitly writes the inherited beta=5 and beta=3 members'},
            note='Retain exactly the two specific existing Stage1 members. The source calls t,x,y the (1+2)-dimensional Kolmogorov variables; x and y are not silently renamed from time. Spatial/state-space interpretation is retained as source metadata.')
    add('2004.10434','S6.E122','reuse-stage1-nonlinear-anisotropic-rdc',
        [r'u_t=\partial_x(u u_x)+\partial_y(u u_y)+8u u_x+8u^2'],['u'],['real scalar reaction-diffusion-convection field'],
        'nonlinear_reaction_diffusion_convection','time and two space variables',
        'The actual source explicitly studies time plus two space variables',kind='native_2d',
        model_dimension_link='equations of the form ( 1 ) in the case of two space variables')
    add('2605.00235','S1.E5','reuse-stage1-potential-modified-kp',
        [r'v_{xxxx}-4v_{xt}+3v_{yy}+6v_{xx}v_y-6v_x^2v_{xx}=0'],['v'],['real scalar mKP potential'],
        'modified_kadomtsev_petviashvili',r'v_{xxxx}-4v_{xt}+3v_{yy}',
        'Complete source mKP equation explicitly retains independent x/y derivatives and evolution t',kind='native_2d',
        supporting_anchors=('S1.E2',),
        note='Recheck the original mKP hierarchy equation and its KP predecessor. Only the governing nonlinear PDE is retained, not tau-function identities or spectral-parameter equations.')
    add('1505.06453','S1.Ex2','reuse-stage1-dispersionless-kp',
        [r'\partial_x(u_t+u u_x)=-\frac{c}{2}u_{yy}'],['u'],['real scalar dispersionless wave amplitude'],
        'dispersionless_kadomtsev_petviashvili',r'\mathbb{R}^{2}',
        'The source explicitly treats x/y plane integrals and u(x,y,t)',kind='native_2d')
    add('2010.08536','S1.EGx4','reuse-stage1-burgers-anisotropic-advection',
        [r'u_t+u u_x-u_{xx}-u_{yy}=0'],['u'],['real scalar two-dimensional Burgers field'],
        'burgers',r'two-dimensional quasilinear evolution equations',
        'Original complete equation has u_t and both Cartesian diffusion axes',kind='native_2d',
        note='Use the actual source explicit Burgers equation, not another unrelated archived arXiv ID. The source symmetry analysis treats t as the evolution coordinate.')
    for power in (2,3):
        add('1107.3543','S1.Ex1','reuse-stage1-porous-bistable-power-'+str(power),
            [fr'u_t=\varepsilon\Delta(u^{power})+\frac{{1}}{{\varepsilon}}u(u-\frac{{1}}{{4}})(1-u)'],
            ['u'],['nonnegative scalar phase/population field'],'porous_medium_bistable',
            r'\mathbb{R}^{N}$ ( $N\geq 2$ )','N>=2 and m>1; select N=2','N',
            supporting_quotes=('has exactly',),
            note='Reuse only existing m=2 and m=3 members and the previously declared bistable polynomial u(u-1/4)(1-u), on u>=0. The source explicitly allows general spatial N>=2; no one-dimensional spatial axis is added.',
            power={'values':{'m':power},'source_range_verified':True,'range_statement':'m>1,N>=2; old concrete bistable member retains source zero/sign conditions'} )
    add('1505.05525','S1.E3','reuse-stage1-parabolic-p-laplacian-p4',
        [r'u_t=\partial_x((u_x^2+u_y^2)u_x)+\partial_y((u_x^2+u_y^2)u_y)'],
        ['u'],['real scalar p-caloric field'],'parabolic_p_laplacian',
        r'variable $x\in\mathbb{R}^{n}$','Source uses a general spatial R^n; select n=2',
        supporting_anchors=('S1.E1',),
        note='Use the actual divergence-form parabolic equation (1.3), not the normalized p-Laplacian from the abstract. The only inherited member has p=4, so |grad u|^2=u_x^2+u_y^2 exactly.',
        power={'values':{'p':4},'source_range_verified':True,'range_statement':'p>1; select the inherited p=4 member'})
    for ell,time_power in [(0.5,1),(1,2)]:
        add('2007.12895','S1.EGx1','reuse-stage1-tricomi-time-power-'+str(time_power),
            [fr'u_{{tt}}-t^{time_power}\Delta(u)=u_t^2'],['u'],['real scalar wave field'],
            'generalized_tricomi_wave',r'x\in\mathbb{R}^{n},\ t>0',
            'Original x is an n-dimensional spatial vector and t is the Cauchy evolution variable; select n=2',
            supporting_quotes=(r'\ell>0',r'p>1'),
            note='Reuse the existing ell=1/2 or 1, p=2 choices; do not confuse time-dependent t^(2ell) with a spatial coefficient. For a real field |u_t|^2=(u_t)^2.',
            power={'values':{'ell':ell,'p':2},'source_range_verified':True,'range_statement':'ell>0,p>1; spatial dimension n includes 2'})
    add('2011.04895','S1.E1','reuse-stage1-tricomi-combined-source',
        [r'u_{tt}-t\Delta(u)=u_t^2+u^2'],['u'],['real scalar wave field'],
        'generalized_tricomi_wave',r'N\geq 1$ denotes the space dimension',
        'N>=1 explicitly denotes spatial dimension; select N=2','N',
        note='Reuse only the existing two-space-dimensional m=1/2,p=q=2 member. The old 3D member is excluded rather than deleting its z derivative.',
        power={'values':{'m':0.5,'p':2,'q':2},'source_range_verified':True,'range_statement':'m>=0,p,q>1,N>=1'})
    add('1911.10834','S1.E4','reuse-stage1-symmetric-linear-dispersion',
        [r'v_t+v_{xxx}+v_{yyy}=0'],['v'],['real scalar linear dispersive field'],
        'linear_planar_dispersion',r'(x,y)\in\mathbb{R}^{2}',
        'The source explicitly defines x/y in R^2 and t as evolution',kind='native_2d',supporting_anchors=('S1.E1',),
        note='Retain the source separately written symmetric linear propagator equation; this is not a copied Fourier multiplier identity.')
    add('1005.5070','S0.E4','reuse-stage1-r-modified-dispersionless-kp',
        [r'w_{yy}=w_{tx}+(\frac{1}{2}(\kappa+1)w_x^2+w_y)w_{xx}+\kappa w_xw_{xy}'],
        ['w'],['real scalar r-modified dispersionless KP potential'],
        'modified_dispersionless_kp','(2+1) dispersionless integrable equations',
        'The original hierarchy explicitly distinguishes two spatial coordinates and one evolution coordinate',kind='native_2d',
        note='Reuse the exact displayed source equation (4), retaining the structural nonlinearity and evolution t. Kappa remains an outer structural coefficient after algebraic expansion; no values are swept.')
    add('1103.1292','S1.E6','reuse-stage1-kp-burgers',
        [r'\partial_x(u_t+u_{xxx}+u u_x-u_{xx})+\varepsilon u_{yy}=0'],['u'],['real scalar dissipative dispersive wave'],
        'kp_burgers',r'(x,y)\in{\mathbb{R}}^{2}',
        'The source defines its 2D KP-type framework on R^2',kind='native_2d',supporting_anchors=('S1.E1',))
    add('1512.05817','S4.EGx70','reuse-stage1-pavlov',
        [r'v_{xt}=v_{yy}+v_xv_{xy}-v_yv_{xx}'],['v'],['real scalar Pavlov field'],
        'pavlov_integrable','(2+1)', 'Original (2+1)-dimensional hierarchy, with the explicit t/x/y Pavlov equation',kind='native_2d')
    (OUT/'legacy-stage1-arxiv-recheck-holds.json').write_text(json.dumps(held,indent=2,ensure_ascii=False)+'\n')
    print('Stage1 arXiv members reviewed:',len(rows),'held:',len(held))
    return rows
