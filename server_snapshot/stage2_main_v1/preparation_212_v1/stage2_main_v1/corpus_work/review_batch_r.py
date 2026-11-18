"""Full canonical 2D diffusion/convection structures from a reviewed Stage1 source.

Each entry uses a literal classified row, not arbitrary functions in a generic
RDC equation. At most two power assignments per source row are instantiated.
"""
from curation import reviewed_model,source_cache


def table_anchor(table,case):
    soup=source_cache('2004.10434')[2]
    active=False;anchors=[]
    for tr in soup.find(id=table).select('tr'):
        cells=tr.find_all(['td','th'],recursive=False)
        number=cells[0].get_text(' ',strip=True) if cells else ''
        if number:
            if active:break
            active=number==str(case)
        if active:anchors.append(tr['id'])
    if not anchors:raise ValueError('Source classified case not found')
    return anchors


def build():
    rows=[]
    def add(case,name,equation,values=None,range_statement='',table='S5.T4'):
        anchors=table_anchor(table,case)
        rows.append(reviewed_model('2004.10434',anchors[0],name,[equation],['u'],
            ['real scalar planar reaction-diffusion-convection field'],
            'classified_planar_reaction_diffusion_convection','time and two space variables',
            'Source explicitly defines one time variable and two spatial variables',kind='native_2d',
            model_dimension_link='The full LSC of the class of RDC equations ( 6 )',
            supporting_anchors=tuple(anchors[1:]),scalar_parameters=('g','a','b'),
            original_model_key=table+'-case-'+str(case),
            power=({'values':values,'source_range_verified':True,'range_statement':range_statement} if values else None),
            note='Literal classified Case '+str(case)+' of '+table+'. The complete table-row fragments and parameter restrictions are retained as evidence. Preserve the PDE structure before coefficient stripping. Equivalent product-rule, Laplacian and term-order forms are deduplicated; the canonical form and its point-transformation precursor are not separately harvested. Any specific nonlinear parameters are recorded, not silently treated as outer coefficients.'))
    def diffusion(profile):return r'\partial_x(('+profile+r')u_x)+\partial_y(('+profile+r')u_y)'
    add(3,'classified-planar-linear-heat',r'u_t=\Delta(u)')
    add(4,'classified-planar-logarithmic-reaction',r'u_t=\Delta(u)+g u\ln(u)')
    add(5,'classified-planar-exponential-diffusion','u_t='+diffusion(r'\exp(u)'))
    add(6,'classified-planar-exponential-diffusion-reaction','u_t='+diffusion(r'\exp(u)')+r'+g\exp(2u)')
    for k in (1,2):
        add(7,'classified-planar-power-diffusion-'+str(k),'u_t='+diffusion(fr'u^{k}'),
            {'k':k},'k!=0,-1; retain only k=1 and k=2')
    for k,m in [(1,3),(2,3)]:
        add(8,f'classified-planar-power-diffusion-reaction-{k}-{m}',
            'u_t='+diffusion(fr'u^{k}')+fr'+g u^{m}',{'k':k,'m':m},'k!=0,-1; m!=1')
    add(9,'classified-planar-logarithmic-diffusion','u_t='+diffusion(r'\frac{1}{u}'))
    add(10,'classified-planar-exponential-rotating-field-drift',
        'u_t='+diffusion(r'\exp(u)')+r'+\exp(2u)(u_x\cos(u)+u_y\sin(u))+g\exp(3u)',
        {'delta':1,'m':2,'p':1},'m!=delta and (m,p)!=(0,0)')
    add(11,'classified-planar-exponential-diffusion-linear-drift',
        'u_t='+diffusion(r'\exp(u)')+r'+u u_x+g\exp(-u)')
    add(12,'classified-planar-exponential-trigonometric-drift',
        'u_t='+diffusion(r'\exp(u)')+r'+\exp(u)(u_x\cos(u)+u_y\sin(u))+g\exp(u)',
        {'p':1},'p=1 is an explicitly permitted trigonometric-drift parameter')
    for k,m in [(1,2),(2,3)]:
        add(13,f'classified-planar-power-log-trigonometric-drift-{k}-{m}',
            'u_t='+diffusion(fr'u^{k}')+fr'+u^{m}(u_x\cos(\ln(u))+u_y\sin(\ln(u)))+g u^{2*m-k+1}',
            {'k':k,'m':m,'p':1},'m!=k and (m,p)!=(0,0); positive u')
    for k in (1,2):
        add(14,'classified-planar-power-diffusion-log-drift-'+str(k),
            'u_t='+diffusion(fr'u^{k}')+fr'+\ln(u)u_x+g u^{{{1-k}}}',
            {'k':k},'k!=0; positive u')
        add(15,'classified-planar-power-log-oscillatory-drift-'+str(k),
            'u_t='+diffusion(fr'u^{k}')+fr'+u^{k}(u_x\cos(\ln(u))+u_y\sin(\ln(u)))+g u^{k+1}',
            {'k':k,'p':1},'k!=0,p!=0; positive u')
        add(16,'classified-planar-power-longitudinal-drift-'+str(k),
            'u_t='+diffusion(fr'u^{k}')+fr'+u^{k}u_x+u^{k+1}',
            {'k':k,'lambda_3':1},'k!=0 and k^2*lambda_3!=4*(k+1); lambda_3=1 satisfies for k=1,2')
    add(18,'classified-planar-burgers-linear-reaction',r'u_t=\Delta(u)+u u_x+g u')
    add(19,'classified-planar-burgers-longitudinal',r'u_t=\Delta(u)+u u_x')
    add(20,'classified-planar-log-advection',r'u_t=\Delta(u)+\ln(u)u_x')
    add(21,'classified-planar-log-advection-reaction',r'u_t=\Delta(u)+\ln(u)u_x+g u\ln(u)')
    add(22,'classified-planar-log-square-reaction',r'u_t=\Delta(u)+2g\ln(u)u_x+u((\ln(u))^2+q)')
    return rows
