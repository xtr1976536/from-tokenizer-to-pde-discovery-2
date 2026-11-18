"""Compare scalar transcriptions to independently formed complex/vector PDEs.

This checks the signed, coefficient-bearing equations BEFORE coefficients are
removed. It catches sign errors that unsigned structural normalization cannot.
"""
import json
from hashlib import sha256
import sympy as sp
from sympy.core.function import AppliedUndef
from curation import OUT
from direct_parser import parse

x,y,t = sp.symbols('x y t', real=True)
axes = {'x':x,'y':y,'t':t}
U,V,P,W,R = [sp.Function(name, real=True)(x,y,t) for name in ('u','v','p','w','r')]
field_expressions = {'u':U,'v':V,'p':P,'w':W,'r':R}


def lap(expression):
    return sp.diff(expression,x,2) + sp.diff(expression,y,2)


def symbolic(node,fields):
    kind = node[0]
    if kind == 'n': return sp.Rational(str(node[1]))
    if kind == 'v':
        name = node[1].lstrip('\\').replace('{','').replace('}','')
        return fields.get(node[1], axes.get(node[1],sp.Symbol(name,real=True)))
    if kind == 'neg': return -symbolic(node[1],fields)
    if kind == 'add': return sum(symbolic(child,fields) for child in node[1:])
    if kind == 'mul': return sp.prod(symbolic(child,fields) for child in node[1:])
    if kind == 'div': return symbolic(node[1],fields)/symbolic(node[2],fields)
    if kind == 'pow': return symbolic(node[1],fields)**symbolic(node[2],fields)
    if kind == 'fn':
        function = {'abs':sp.Abs,'ln':sp.log}.get(node[1],getattr(sp,node[1],None))
        if function is None: raise ValueError('Unsupported explicit function: '+node[1])
        return function(symbolic(node[2],fields))
    if kind == 'd': return sp.diff(symbolic(node[1],fields),*[axes[a] for a in node[2]])
    if kind == 'lap':
        result = symbolic(node[1],fields)
        for _ in range(node[2]): result = lap(result)
        return result
    raise ValueError('Unneeded operator in component-equivalence audit: '+kind)


def real_jets(expression):
    expression = sp.expand(expression.doit())
    replacements = {derivative:sp.Symbol(str(derivative),real=True) for derivative in expression.atoms(sp.Derivative)}
    replacements.update({function:sp.Symbol(str(function.func),real=True) for function in expression.atoms(AppliedUndef)})
    return expression.xreplace(replacements)


def complex_parts(expression):
    value = real_jets(expression)
    return [sp.expand(sp.re(value)),sp.expand(sp.im(value))]


def main():
    rows = {row['id']:row for row in [json.loads(line) for line in (OUT/'reviewed-unique-structures.jsonl').read_text().splitlines()]}
    psi = U+sp.I*V
    density = U**2+V**2
    expected = {}
    expected['cubic-quadratic-klein-gordon-schrodinger'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)-P**2*psi+P*psi) + [sp.diff(P,t,2)-lap(P)+P+2*density*P-density]
    expected['zakharov-schrodinger-wave'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)-P*psi) + [sp.diff(P,t,2)-lap(P)-lap(density)]
    for exponent in (3,5):
        expected[f'generalized-davey-stewartson-power-{exponent}'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)+density**((exponent-1)//2)*psi+P*psi) + [lap(P)-sp.diff(density,x,2)]
    a,b,gamma_1,gamma_2,kappa = sp.symbols('a b gamma_1 gamma_2 kappa',real=True)
    div = sp.diff(U,x)+sp.diff(V,y)
    expected['classical-thermoelasticity-fourier'] = [
        sp.diff(U,t,2)-a**2*lap(U)-(b**2-a**2)*sp.diff(div,x)+gamma_1*sp.diff(P,x),
        sp.diff(V,t,2)-a**2*lap(V)-(b**2-a**2)*sp.diff(div,y)+gamma_1*sp.diff(P,y),
        sp.diff(P,t)-kappa*lap(P)+gamma_2*sp.diff(div,t)]
    alpha,beta = sp.symbols('alpha beta',real=True)
    spin = sp.Matrix([U,V,P]); diffused = spin.applyfunc(lap)
    expected['landau-lifshitz-precession-damping'] = list(spin.diff(t)-alpha*spin.cross(diffused)+beta*spin.cross(spin.cross(diffused)))
    norm = sum(sp.diff(field,axis)**2 for field in spin for axis in (x,y))
    expected['harmonic-map-heat-flow-sphere'] = list(spin.diff(t)-diffused-norm*spin)
    coupling = sp.Symbol('lambda',real=True)
    expected['planar-schrodinger-poisson'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)/2-coupling*P*psi) + [-lap(P)-density]
    for gamma in (3,4):
        mass = sp.diff(R,t)+sp.diff(R*U,x)+sp.diff(R*V,y)
        pressure = R**gamma/gamma
        momentum_x = sp.diff(R*U,t)+sp.diff(R*U**2,x)+sp.diff(R*U*V,y)+sp.diff(pressure,x)
        momentum_y = sp.diff(R*V,t)+sp.diff(R*U*V,x)+sp.diff(R*V**2,y)+sp.diff(pressure,y)
        expected[f'compressible-euler-density-gamma-{gamma}'] = [mass,
            sp.expand((momentum_x-U*mass)/R),sp.expand((momentum_y-V*mass)/R)]
    g,g_R,pump,rate,gamma_c,gamma_R = sp.symbols('g g_R P_0 R gamma_c gamma_R',real=True)
    expected['polariton-uniform-incoherent-reservoir'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)/2-g*density*psi-g_R*P*psi-sp.I*(rate*P-gamma_c)*psi/2) + [sp.diff(P,t)-pump+(gamma_R+rate*density)*P]
    beta = sp.Symbol('beta',real=True)
    gamma_x,gamma_y,Omega = sp.symbols('gamma_x gamma_y Omega',real=True)
    trap = (gamma_x**2*x**2+gamma_y**2*y**2)/2
    expected['cubic-nonlinear-schrodinger-untrapped'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)/2-beta*density*psi)
    expected['gross-pitaevskii-harmonic-trap'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)/2-trap*psi-beta*density*psi)
    angular_momentum = -sp.I*(x*sp.diff(psi,y)-y*sp.diff(psi,x))
    expected['rotating-gross-pitaevskii-harmonic-trap'] = complex_parts(sp.I*sp.diff(psi,t)+lap(psi)/2-trap*psi-beta*density*psi+Omega*angular_momentum)
    beta_11,beta_12,beta_22,delta = sp.symbols('beta_11 beta_12 beta_22 delta',real=True)
    psi_2 = P+sp.I*W
    density_2 = P**2+W**2
    for coupled in (False,True):
        rate = coupling if coupled else 0
        expected['two-component-gpe-'+('josephson' if coupled else 'without-josephson')] = complex_parts(
            sp.I*sp.diff(psi,t)+lap(psi)/2-trap*psi-delta*psi-(beta_11*density+beta_12*density_2)*psi-rate*psi_2) + complex_parts(
            sp.I*sp.diff(psi_2,t)+lap(psi_2)/2-trap*psi_2-(beta_12*density+beta_22*density_2)*psi_2-rate*psi)
    mu,beta_r,beta_i,gamma_r,gamma_i,D_r,D_i = sp.symbols('mu beta_r beta_i gamma_r gamma_i D_r D_i',real=True)
    expected['cubic-quintic-complex-ginzburg-landau'] = complex_parts(sp.diff(psi,t)-mu*psi-(beta_r+sp.I*beta_i)*density*psi-(gamma_r+sp.I*gamma_i)*density**2*psi-(D_r+sp.I*D_i)*lap(psi))
    D_0,A,epsilon,gamma_1,gamma_2,gamma_3 = sp.symbols('D_0 A epsilon gamma_1 gamma_2 gamma_3',real=True)
    gain = -gamma_1+gamma_2*density-gamma_3*density**2
    expected['dissipative-gap-wave-periodic-lattice'] = complex_parts(sp.I*sp.diff(psi,t)+D_0*lap(psi)-density*psi+A*(sp.cos(x)+sp.cos(y))*psi-sp.I*epsilon*gain*psi)
    # Original two-layer block matrix plus source-defined nonlinear vector.
    B,alpha,beta,D1,D2,D3,D4 = sp.symbols('B alpha beta D_1 D_2 D_3 D_4',real=True)
    layer_1,layer_2 = sp.Matrix([U,V]),sp.Matrix([P,W])
    linear = sp.Matrix([[B-1,A**2],[-B,-A**2]])
    exchange = sp.diag(alpha,beta)
    nlt_1,nlt_2 = B/A*U**2+2*A*U*V+U**2*V,B/A*P**2+2*A*P*W+P**2*W
    rhs_1 = sp.diag(D1,D2)*layer_1.applyfunc(lap)+linear*layer_1+exchange*(layer_2-layer_1)+sp.Matrix([nlt_1,-nlt_1])
    rhs_2 = sp.diag(D3,D4)*layer_2.applyfunc(lap)+linear*layer_2+exchange*(layer_1-layer_2)+sp.Matrix([nlt_2,-nlt_2])
    expected['brusselator-planar-two-layers'] = list(layer_1.diff(t)-rhs_1)+list(layer_2.diff(t)-rhs_2)
    # Check the actual field-unit substitution, not an arbitrary chi=1 choice.
    nutrient = sp.Function('m',real=True)(x,y,t)
    chi,theta_1 = sp.symbols('chi theta_1',real=True)
    original_signal = V/chi
    expected['local-sensing-exponential-motility-nutrient'] = [
        sp.diff(U,t)-lap(U*sp.exp(-chi*original_signal))-alpha*U*nutrient,
        chi*(sp.diff(original_signal,t)-lap(original_signal)+original_signal-theta_1*U),
        sp.diff(nutrient,t)-lap(nutrient)+U*nutrient]
    rho = sp.Function('rho',real=True)(x,y,t)
    a,b,eta,J_e,k_1,k_2,c,gamma,delta,q,a_0,r = sp.symbols('a b eta J_e k_1 k_2 c gamma delta q a_0 r',real=True)
    for law in ('quadratic','tanh'):
        phi = c+gamma*rho+delta*rho**2 if law=='quadratic' else sp.tanh(rho)
        expected['memristive-hindmarsh-rose-'+law] = [
            sp.diff(U,t)-eta*lap(U)-a*U**2+b*U**3-V+W-J_e+k_1*phi*U,
            sp.diff(V,t)-alpha+beta*U**2+V,
            sp.diff(W,t)-q*(U-a_0)+r*W,
            sp.diff(rho,t)-U+k_2*rho]
    checked = []
    for name,equations in expected.items():
        row = rows[name]
        declared_fields = {field:field_expressions.get(field,sp.Function(field.lstrip('\\'),real=True)(x,y,t))
                           for field in row['source_fields']}
        assert len(equations) == len(row['reviewed_transcription'])
        for index,(transcription,reference) in enumerate(zip(row['reviewed_transcription'],equations)):
            left,right = transcription.split('=')
            left,_ = parse(left,tuple(row['source_fields']),row['explicit_scalar_parameters'])
            right,_ = parse(right,tuple(row['source_fields']),row['explicit_scalar_parameters'])
            difference = real_jets(symbolic(left,declared_fields)-symbolic(right,declared_fields)) - real_jets(reference)
            assert sp.simplify(sp.expand(difference)) == 0, (name,index,difference)
        checked.append(name)
    report = {'status':'PASS','signed_coefficient_bearing_systems_checked':len(checked),
              'scalar_equations_checked':sum(len(expected[name]) for name in checked),
              'systems':checked,'method':'independent complex/vector PDEs, source block matrices, constitutive laws and exact field-unit transformations compared symbolically before coefficient removal',
              'input_corpus_sha256':sha256((OUT/'reviewed-unique-structures.jsonl').read_bytes()).hexdigest(),
              'not_a_claim_of_entire_corpus_acceptance':True}
    (OUT/'component-expansion-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__ == '__main__':
    main()
