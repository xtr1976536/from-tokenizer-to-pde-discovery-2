"""Source-written NLS/GPE models and explicit trapping/linear-coupling branches."""
from curation import reviewed_model


def build():
    rows = []
    def add(*args, **kwargs):
        rows.append(reviewed_model(*args, **kwargs))
    dimension = 'dimensionless GPE in $d$ ( $d=1,2,3$ ) dimensions'
    trap = r'(\frac{1}{2}\gamma_x^2x^2+\frac{1}{2}\gamma_y^2y^2)'
    density = '(u^2+v^2)'
    add('1212.5341','S2.E1','cubic-nonlinear-schrodinger-untrapped',
        [fr'-v_t=-\frac{{1}}{{2}}\Delta(u)+\beta{density}u',
         fr'u_t=-\frac{{1}}{{2}}\Delta(v)+\beta{density}v'],
        ['u','v'],['real wavefunction component','imaginary wavefunction component'],
        'nonlinear_schrodinger',dimension,'d in {1,2,3}','d',
        supporting_quotes=(r'for $V(\mathbf{x})\equiv 0$',),
        note='Exact real/imaginary split of source (2.1), using the source explicit zero-potential case discussed at (2.54). This is not an arbitrary choice for an unspecified function.')
    add('1212.5341','S2.E1','gross-pitaevskii-harmonic-trap',
        [fr'-v_t=-\frac{{1}}{{2}}\Delta(u)+{trap}u+\beta{density}u',
         fr'u_t=-\frac{{1}}{{2}}\Delta(v)+{trap}v+\beta{density}v'],
        ['u','v'],['real condensate component','imaginary condensate component'],
        'gross_pitaevskii',dimension,'d in {1,2,3}','d',supporting_anchors=('S1.E40',),
        note='Exact split of source (2.1) with the explicit d=2 harmonic potential from (1.40); different trap frequencies are coefficients and do not create extra entries.')
    add('1212.5341','S5.E6','rotating-gross-pitaevskii-harmonic-trap',
        [fr'-v_t=-\frac{{1}}{{2}}\Delta(u)+{trap}u+\beta{density}u-\Omega(xv_y-yv_x)',
         fr'u_t=-\frac{{1}}{{2}}\Delta(v)+{trap}v+\beta{density}v+\Omega(xu_y-yu_x)'],
        ['u','v'],['real rotating condensate component','imaginary rotating condensate component'],
        'gross_pitaevskii',r'V_{2}(x,y)', 'Source explicitly reduced 2D rotating equation',kind='native_2d',
        scalar_parameters=(r'\Omega',),
        supporting_anchors=('S1.E40','S5.E2'),
        note='Source (5.6) is already a 2D reduction. Expand L_z=-i(x*partial_y-y*partial_x) with source dimensionless units; retain the explicit harmonic trap and rotation term.')
    for coupled in (False,True):
        coupling = r'+\lambda\cdot ' if coupled else ''
        extra = lambda variable: coupling+variable if coupled else ''
        first = r'(\beta_{11}(u^2+v^2)+\beta_{12}(p^2+w^2))'
        second = r'(\beta_{12}(u^2+v^2)+\beta_{22}(p^2+w^2))'
        add('1212.5341','S9.E3','two-component-gpe-'+('josephson' if coupled else 'without-josephson'),
            [fr'-v_t=-\frac{{1}}{{2}}\Delta(u)+{trap}u+\delta u+{first}u'+extra('p'),
             fr'u_t=-\frac{{1}}{{2}}\Delta(v)+{trap}v+\delta v+{first}v'+extra('w'),
             fr'-w_t=-\frac{{1}}{{2}}\Delta(p)+{trap}p+{second}p'+extra('u'),
             fr'p_t=-\frac{{1}}{{2}}\Delta(w)+{trap}w+{second}w'+extra('v')],
            ['u','v','p','w'],['real component of psi_1','imaginary component of psi_1','real component of psi_2','imaginary component of psi_2'],
            'coupled_gross_pitaevskii',r'in $d$ -dimensions ( $d=1,2,3$ )', 'd in {1,2,3}','d',
            supporting_anchors=('S1.E40',),
            supporting_quotes=(() if coupled else ('If there is no external driving field in ( 9.3 ), i.e. $\\lambda=0$',)),
            note='Exact split psi_1=u+i*v and psi_2=p+i*w. Use explicit harmonic potential (1.40). '+
                 ('Retain the internal Josephson/Rabi coupling in (9.3).' if coupled else 'Use the separately named no-Josephson branch lambda=0 in Section 9.2; not a sweep of nonzero coefficient magnitudes.'))
    return rows
