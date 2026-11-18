"""Source-named planar dispersive systems and explicitly reduced enzyme systems."""
from curation import reviewed_model


def build():
    rows=[]
    # These seven zero/nonzero patterns are individually named in the source.
    # They are derivative-structure branches, never coefficient-magnitude sweeps.
    branches=[('generic',1,1,1,1,'b>0,d>0,a<0,c<0'),
              ('kdv-kdv',1,0,1,0,'a=c=1/6,b=d=0'),
              ('schrodinger-d',1,0,1,1,'b=0'),
              ('schrodinger-b',1,1,1,0,'d=0'),
              ('bbm-bbm',0,1,0,1,'b>0,d>0,a=c=0'),
              ('original-velocity-bbm',0,0,0,1,'a=c=b=0'),
              ('original-height-bbm',0,1,0,0,'a=c=d=0')]
    for name,a,b,c,d,quote in branches:
        first=r'u_t+v_x+p_y+\varepsilon(\partial_x(uv)+\partial_y(up))'
        if a:first+=r'+\varepsilon a(\partial_x(\Delta(v))+\partial_y(\Delta(p)))'
        if b:first+=r'-\varepsilon b\Delta(u_t)'
        second=r'v_t+u_x+\frac{\varepsilon}{2}\partial_x(v^2+p^2)'
        third=r'p_t+u_y+\frac{\varepsilon}{2}\partial_y(v^2+p^2)'
        if c:
            second+=r'+\varepsilon c\partial_x(\Delta(u))'
            third+=r'+\varepsilon c\partial_y(\Delta(u))'
        if d:
            second+=r'-\varepsilon d\Delta(v_t)'
            third+=r'-\varepsilon d\Delta(p_t)'
        rows.append(reviewed_model('1103.4159','S1.E2','planar-abcd-boussinesq-'+name,
            [e+'=0' for e in (first,second,third)],['u','v','p'],
            ['free-surface elevation eta','first horizontal velocity component','second horizontal velocity component'],
            'dispersive_surface_water_waves',r'x\in{\mathbb{R}}^{n}',
            'Original system U has n+1 scalar components, n=1,2; select n=2',
            supporting_quotes=(quote,),scalar_parameters=('a','b','c','d'),
            note='Exact Cartesian expansion of source equation (2), eta=u, vector velocity=(v,p), horizontal x1=x,x2=y. The source explicitly names this derivative branch. Retain nonzero a,b,c,d as fitted constants satisfying the source constraint; no unsupported values are assigned. Pressure/incompressibility is not a constraint in this surface-wave model.'))
    # curl H=(0,0,H2_x-H1_y), curl E=(E3_y,-E3_x,0).
    rows.append(reviewed_model('1412.2637','S1.EGx1','maxwell-planar-tm-polarization',
        [r'\epsilon u_t=p_x-v_y',r'\mu v_t=-u_y',r'\mu p_t=u_x'],
        ['u','v','p'],['electric component E3','magnetic component H1','magnetic component H2'],
        'electromagnetic_waves',r'\Omega^{\prime}\subset\mathbb{R}^{2}',
        'Source explicitly defines z-independent TM mode E=(0,0,E3), H=(H1,H2,0)',kind='native_2d',
        model_dimension_link='TM mode',
        supporting_quotes=('independent of $z$',),
        note='Exact source-described TM reduction of the full curl system. No three-dimensional component is silently discarded: the source defines the invariant polarization. One polarization only; its coefficient-free dual is not separately counted.'))
    # Source y means total enzyme, NOT the spatial y coordinate. Rename to p.
    rows.append(reviewed_model('1707.04043','S3.EGx5','enzyme-irreversible-total-enzyme-system',
        [r'u_t=d_1\Delta(u)-k_1u(p-v)+k_2v',
         r'v_t=d_2\Delta(v)+k_1u(p-v)-(k_2+k_3)v',
         r'p_t=d_2\Delta(v)+d_3(\Delta(p)-\Delta(v))'],
        ['u','v','p'],['substrate s','complex c','total enzyme y=e+c'],
        'enzyme_reaction_diffusion',r'\Omega=(0,L_{1})\times(0,L_{2})\times\cdots\times(0,L_{n})\subseteq\mathbb{R}^{n}',
        'Original PDE domain is a bounded smooth subset of R^n; select n=2',
        model_dimension_link='irreversible case',scalar_parameters=('d_3',),
        note='Exact source system (3.2)-(3.4); source y is renamed as a dependent field p. Diffusion difference is retained before stripping, with generic unequal enzyme/complex diffusivities. Product concentration is absent because the original irreversible subsystem is closed, not because a coupled row was dropped.'))
    rows.append(reviewed_model('1707.04043','S5.EGx13','enzyme-small-substrate-reversible-reduction',
        [r'u_t=d_1\Delta(u)-a uv+bvp',r'v_t=d_2\Delta(v)',r'p_t=d_3\Delta(p)+a uv-bvp'],
        ['u','v','p'],['substrate s','free enzyme e','product p'],
        'enzyme_reaction_diffusion',r'\Omega=(0,L_{1})\times(0,L_{2})\times\cdots\times(0,L_{n})\subseteq\mathbb{R}^{n}',
        'Same original PDE domain in R^n; select n=2',
        model_dimension_link='Concluding remarks',
        note='Use the separately stated small-substrate reduced PDE, not the full four-species system with a row removed. a=k1*k2/(k-1+k2), b=k-1*k-2/(k-1+k2) are nonzero scalar coefficients. Source evolution tau is renamed t.'))
    rows.append(reviewed_model('2507.06319','S3.EGx34','predator-search-handling-resource',
        [r'u_t=d_1\Delta(u)-a pu-bu+cv',r'v_t=d_2\Delta(v)+2a pu-dv-cv',r'p_t=d_3\Delta(p)-a pu-ep+f'],
        ['u','v','p'],['searching predator','handling predator','resource'],
        'predator_search_handling',r'n=1,\,2,\,3',
        'Original reaction-diffusion framework explicitly permits spatial n=1,2,3',
        model_dimension_link='(3.2)',
        note='Complete source reduced system (3.3), after reservoirs have been eliminated by the original singular limit. Search/handling conversion factors retained in signed transcription; scalar a0 enters only the constant input f.'))
    for anchor,name,power in [('S3.EGx38','bilinear',1),('S3.EGx40','quadratic-activation',2)]:
        rows.append(reviewed_model('2507.06319',anchor,'resource-predator-'+name,
            [fr'u_t=d_1\Delta(u)+a vu^{power}-bu',fr'v_t=d_2\Delta(v)-a vu^{power}-cv+d'],
            ['u','v'],['active predator','resource'],'resource_predator',r'n=1,\,2,\,3',
            'The explicitly written reduced models inherit the source n=1,2,3 spatial domain',
            model_dimension_link='(3.2)',
            note='Literal two-species source reduction. This is not a new power sweep of the three-species model; each is separately displayed and interpreted in the source.'))
    return rows
