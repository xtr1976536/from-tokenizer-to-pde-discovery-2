"""Formula expressions and source links only; no research prose in the PDF."""
import json,subprocess,re
from hashlib import sha256
from curation import OUT
from latex_render import latex


def display(ast):
    terms=ast[1:] if ast[0]=='add' else [ast]
    lines=[];current=''
    for term in terms:
        token=latex(term)
        # Keep each mathematical term intact; break only between outer terms.
        if current and len(current)+len(token)>110:
            lines.append(current);current='{}+'+token
        else:current+=('+' if current else '')+token
    lines.append(current+'=0')
    return r'\begin{gathered}'+r'\\[-1pt]'.join(lines)+r'\end{gathered}'


def main():
    rows=[json.loads(l) for l in (OUT/'frozen/base-structures.jsonl').read_text().splitlines()]
    folder=OUT/'formula-catalog';folder.mkdir(exist_ok=True)
    head=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=17mm]{geometry}
\usepackage{amsmath,amssymb,adjustbox,hyperref}
\hypersetup{colorlinks=true,urlcolor=blue}
\newcommand{\abs}[1]{\left|#1\right|}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\pagestyle{plain}
\begin{document}
'''
    blocks=[]
    for row in rows:
        maths=r'\\[5pt]'.join(display(n) for n in row['normalized']['residual_support_ast'])
        group=row['source_group'].replace('_',r'\_')
        locator=row.get('equation_locator','')
        if locator:group+=' / '+locator.replace('_',r'\_')
        source=r'\href{'+row['source_url']+'}{'+group+'}'
        blocks.append(r'\begin{minipage}{\linewidth}'+ '\n'+
            r'\begin{center}\begin{adjustbox}{max width=\linewidth}$\displaystyle\begin{gathered}'+maths+
            r'\end{gathered}$\end{adjustbox}\end{center}'+ '\n'+
            r'{\small '+source+r'}\par'+ '\n'+r'\end{minipage}\par\vspace{7mm}'+'\n')
    tex=head+'\n'.join(blocks)+r'\end{document}'+'\n'
    (folder/'formulas-and-sources.tex').write_text(tex)
    command=['xelatex','-interaction=nonstopmode','-halt-on-error','formulas-and-sources.tex']
    result=subprocess.run(command,cwd=folder,capture_output=True,text=True)
    (folder/'compile-output.txt').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(result.stdout[-2500:])
    # Preserve exact base order for external review without cluttering the PDF.
    (folder/'entry-order.json').write_text(json.dumps([r['id'] for r in rows],indent=2)+'\n')
    pdf=folder/'formulas-and-sources.pdf'
    print(json.dumps(dict(pdf=str(pdf),formulas=len(rows),sha256=sha256(pdf.read_bytes()).hexdigest())))


if __name__=='__main__':main()
