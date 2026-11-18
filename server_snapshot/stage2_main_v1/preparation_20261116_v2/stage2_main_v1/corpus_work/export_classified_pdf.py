"""Group the unchanged 212 structures by physical/mathematical mechanism."""
import json,subprocess
from hashlib import sha256
from curation import ROOT,OUT
from export_formula_pdf import display

DESCRIPTIONS={
'diffusion_transport_reaction':('扩散、输运与反应','描述热量、物质或种群密度在二维区域中的扩散、定向输运及局部增长或衰减。包括线性扩散、非线性扩散、退化扩散与反应—扩散—对流结构。'),
'elliptic_stationary':('稳态场与椭圆方程','描述达到平衡后的空间分布，例如稳态温度、势场、受迫场及非线性平衡态。这里的两个独立空间坐标均有来源依据，不将一维时间演化公式改称二维稳态。'),
'chemical_reaction_diffusion':('化学反应、酶动力学与反应扩散','描述多种反应物或化学组分在扩散过程中的转化、消耗与生成，包括质量作用反应、激活—抑制、酶促反应和分层耦合反应结构。'),
'chemotaxis_haptotaxis_signalling':('趋化、趋触与信号传递','描述细胞或其他移动群体沿化学信号、组织基质梯度迁移，以及信号产生、消耗和间接传递。不同信号弛豫或组织响应产生不同的演化与代数方程组合。'),
'population_ecology_cross_diffusion':('种群竞争、捕食与交叉扩散','描述物种间竞争、合作、捕食、资源利用及搜索—处理过程。交叉扩散或趋性项表示一种群的移动受到其他种群分布影响。'),
'epidemic_spread':('传染病空间传播','描述易感、暴露、感染或恢复人群在空间中的迁移及状态转化，覆盖普通扩散与交叉扩散传播结构。具体分量数依原模型保留。'),
'tumor_growth_and_virotherapy':('肿瘤相场与溶瘤病毒治疗','描述肿瘤与健康组织的相分离、营养物质交换，或病毒感染肿瘤细胞及组织降解。包括含化学势代数关系的相场系统。'),
'neuronal_memristive_dynamics':('神经反应扩散与忆阻动力学','描述膜电位、恢复变量、慢适应或忆阻状态的耦合演化，以及扩散耦合对空间神经活动的影响。'),
'quantum_and_complex_waves':('复振幅、量子波与凝聚态','描述复波函数或振幅的色散、非线性、自洽势和耗散耦合。原复变量展开为实部与虚部后再统计标量变量数。'),
'compressible_and_surface_fluid_waves':('可压缩流动、浅水与色散水波','描述密度或自由表面与水平速度的耦合、旋转效应和长波色散，也包括二维黏性Burgers结构。所列模型与Cylinder目标不可压缩NS系统有实质结构差异。'),
'integrable_dispersive_waves':('可积与色散波动','描述二维非线性波传播、弱横向效应及色散或耗散修正，覆盖KP类、Pavlov等源二维结构；没有给一维波动方程补加空间坐标。'),
'pattern_forming_higher_order_pdes':('高阶模式形成与局域结构','描述失稳后形成的条纹、斑点、局域图样及界面纹理。高阶空间算子刻画不同尺度之间的竞争或稳定化作用。'),
'elastic_and_coupled_hyperbolic_waves':('弹性、热弹性与耦合双曲波','描述位移、温度或多个波场的传播与耦合，也包括传播系数随时间变化的广义Tricomi结构。微分阶数和混合导数按原式保留。'),
'electromagnetic_waves':('电磁波','描述原文明确定义的二维TM极化下电场和磁场分量的耦合传播，三个标量分量由原Maxwell旋度系统展开得到。'),
'spin_and_geometric_evolution':('自旋与几何演化','描述自旋方向的进动、阻尼或映射的几何弛豫。向量叉积、梯度范数等按源二维坐标展开为完整标量系统。')}


def main():
    rows=[json.loads(l) for l in (OUT/'frozen/base-structures.jsonl').read_text().splitlines()]
    mapping=json.loads((OUT/'coarse-diversity-audit.json').read_text())['mapping']
    target=ROOT/'outputs/eqgpt-research/stage2-preparation-2026-11-16/formula-catalog';target.mkdir(parents=True,exist_ok=True)
    head=r'''\documentclass[UTF8,10pt,a4paper,fontset=mac]{ctexart}
\usepackage[margin=17mm]{geometry}
\usepackage{amsmath,amssymb,adjustbox,hyperref}
\hypersetup{colorlinks=true,urlcolor=blue}
\newcommand{\abs}[1]{\left|#1\right|}
\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}
\begin{document}
{\Large 二维PDE结构语料：分类公式与来源}\par
共212条基础结构，分为15类。以下为统一的无系数拟合项结构；原始带符号和系数公式单独保留。\par
'''
    blocks=[];order=[];counts={}
    for i,(category,(title,description)) in enumerate(DESCRIPTIONS.items(),1):
        selected=[r for r in rows if mapping[r['family']]==category];counts[category]=len(selected)
        blocks.append(r'\section*{'+str(i)+'. '+title+'（'+str(len(selected))+r'条）}'+'\n'+description+'\par\medskip\n')
        for row in selected:
            math=r'\\[5pt]'.join(display(n) for n in row['normalized']['residual_support_ast'])
            label=row['source_group'].replace('_',r'\_')
            if row.get('equation_locator'):label+=' / '+row['equation_locator'].replace('_',r'\_')
            blocks.append(r'\begin{minipage}{\linewidth}\begin{center}\begin{adjustbox}{max width=\linewidth}$\displaystyle\begin{gathered}'+math+
                r'\end{gathered}$\end{adjustbox}\end{center}{\small\href{'+row['source_url']+'}{'+label+r'}}\par\end{minipage}\par\vspace{6mm}'+'\n')
            order.append(row['id'])
    assert len(order)==len(set(order))==212
    (target/'classified-formulas.tex').write_text(head+'\n'.join(blocks)+r'\end{document}'+'\n')
    for _ in range(2):
        result=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','classified-formulas.tex'],cwd=target,capture_output=True,text=True)
        (target/'compile-output.txt').write_text(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError(result.stdout[-2500:])
    (target/'classification.json').write_text(json.dumps(dict(counts=counts,descriptions=DESCRIPTIONS,ids_in_pdf_order=order,
        base_sha256=sha256((OUT/'frozen/base-structures.jsonl').read_bytes()).hexdigest()),ensure_ascii=False,indent=2)+'\n')
    print('Created',target/'classified-formulas.pdf')


if __name__=='__main__':main()
