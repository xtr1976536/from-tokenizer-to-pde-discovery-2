"""Canonical direct LaTeX; retain literal powers and derivative order."""


def latex(node):
    kind=node[0]
    if kind=='n':return str(int(node[1])) if node[1]==int(node[1]) else str(node[1])
    if kind=='v':return node[1]
    if kind=='neg':return '-'+('('+latex(node[1])+')' if node[1][0]=='add' else latex(node[1]))
    if kind=='add':
        result=latex(node[1])
        for child in node[2:]:result+=('' if child[0]=='neg' else '+')+latex(child)
        return result
    if kind=='mul':return r'\cdot '.join('('+latex(c)+')' if c[0] in ('add','neg') else latex(c) for c in node[1:])
    if kind=='div':return r'\frac{('+latex(node[1])+')}{'+latex(node[2])+'}'
    if kind=='pow':return (latex(node[1]) if node[1][0] in ('v','n') else '('+latex(node[1])+')')+'^{'+latex(node[2])+'}'
    if kind=='d':return r'\partial_{'+node[2]+'}('+latex(node[1])+')'
    if kind=='lap':return r'\Delta'+('^{'+str(node[2])+'}' if node[2]>1 else '')+'('+latex(node[1])+')'
    if kind=='grad':return r'\nabla('+latex(node[1])+')'
    if kind=='divergence':return r'\nabla\cdot('+latex(node[1])+')'
    if kind=='fn':
        if node[1] in ('sqrt','abs'):return '\\'+node[1]+'{'+latex(node[2])+'}'
        return '\\'+node[1]+'('+latex(node[2])+')'
    raise ValueError('Unsupported canonical LaTeX node: '+kind)
