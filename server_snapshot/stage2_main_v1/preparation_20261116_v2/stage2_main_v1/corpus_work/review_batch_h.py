"""Explicit fully/partly diffusive three-variable neuron systems."""
from curation import reviewed_model


def build():
    rows=[]
    for anchor,name,diff_v,diff_w in [
        ('S1.EGx1','hindmarsh-rose-fully-diffusive',True,True),
        ('S1.E7','hindmarsh-rose-voltage-only-diffusion',False,False),
        ('S1.E8','hindmarsh-rose-voltage-recovery-diffusion',True,False),
    ]:
        equations=[r'u_t=d_1\Delta(u)+au^2-bu^3+v-w+J',
                   r'v_t='+ (r'd_2\Delta(v)+' if diff_v else '') + r'\alpha-\beta u^2-v',
                   r'w_t='+ (r'd_3\Delta(w)+' if diff_w else '') + r'q(u-c)-rw']
        rows.append(reviewed_model('1907.13225',anchor,name,equations,
            ['u','v','w'],['membrane potential','spiking/recovery variable','slow adaptation/bursting variable'],
            'neuronal_reaction_diffusion',r'\Omega\subset\mathbb{R}^{n}$ ( $n\leq 3$ )',
            'Positive spatial dimension n<=3 includes n=2',
            scalar_parameters=('q',),supporting_anchors=('S1.E4',),
            note='Source explicitly writes all three diffusion configurations as (1.1)-(1.3), (1.7), and (1.8). Substitute the source-defined phi(u)=a*u^2-b*u^3 and psi(u)=alpha-beta*u^2. J and q,c,r are source constants. No diffusion term is deleted merely to generate additional examples.'))
    return rows
