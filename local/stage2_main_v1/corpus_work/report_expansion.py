# -*- coding: utf-8 -*-
"""Summarize an audited, unfrozen collection batch without counting search hits."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from curation import OUT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--previous-count',type=int,required=True)
    parser.add_argument('--unit-tests-passed',type=int,required=True)
    args=parser.parse_args()
    audit=json.loads((OUT/'reviewed-corpus-audit.json').read_text())
    components=json.loads((OUT/'component-expansion-audit.json').read_text())
    digest=sha256((OUT/'reviewed-unique-structures.jsonl').read_bytes()).hexdigest()
    assert audit['input_corpus_sha256']==components['input_corpus_sha256']==digest
    assert components['status']=='PASS'
    rows=[json.loads(line) for line in (OUT/'audited-structures.jsonl').read_text().splitlines()]
    assert len(rows)==len({row['structure_key'] for row in rows})
    assert all(row['review_status']=='SOURCE_AND_STRUCTURE_AUDITED_BATCH_NOT_FROZEN' for row in rows)
    assert all(not row['leakage_review_reasons'] for row in rows)
    assert max(audit['power_policy']['instance_counts'].values(),default=0)<=2
    baseline=[json.loads(line) for line in (OUT/'baseline76-before-reuse.jsonl').read_text().splitlines()]
    assert len(baseline)==args.previous_count
    baseline_ids={row['id'] for row in baseline}
    added=[row for row in rows if row['id'] not in baseline_ids]
    removed=sorted(baseline_ids-{row['id'] for row in rows})
    fields=Counter(len(row['normalized']['fields']) for row in rows)
    summary={
        'previous_unique_structures':args.previous_count,
        'added_unique_structures':len(added), 'total_unique_structures':len(rows),
        'source_papers':audit['source_papers'], 'original_model_definitions':audit['original_model_definitions'],
        'field_counts':dict(fields),'three_field_fraction':fields[3]/len(rows),
        'minimum_remaining':max(0,212-len(rows)),'target_remaining':max(0,1000-len(rows)),
        'power_cap':2,'unit_tests_passed':args.unit_tests_passed,
        'source_and_structure_audits':'PASS',
        'signed_component_systems_passed':components['signed_coefficient_bearing_systems_checked'],
        'signed_scalar_equations_passed':components['scalar_equations_checked'],
        'input_corpus_sha256':digest,'frozen_for_training':False,'formal_training_started':False,
        'added_ids':[row['id'] for row in added],
        'baseline_ids_removed':removed,
    }
    (OUT/'expansion-summary-2026-11-15.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    lines=[
        '# 本轮语料扩充记录','',
        f'本轮新增 {len(added)} 个去重基础结构：{args.previous_count} → {len(rows)}。共来自 {audit["source_papers"]} 个文献来源。',
        f'按源方程定义与显式反应函数绑定统计为 {audit["original_model_definitions"]} 个模型定义；这个数包括原文明列的结构分支，不等于独立物理机制数。','',
        f'变量数：单变量 {fields[1]}；两变量 {fields[2]}；三变量 {fields[3]}；四变量 {fields[4]}。三变量占 {fields[3]/len(rows):.2%}。','',
        f'最低 212 条还差 {max(0,212-len(rows))} 条；1000 条目标还差 {max(0,1000-len(rows))} 条。当前未冻结训练语料，未启动正式训练。','',
        '每个原始模型合计最多两个幂次实例；同源实例共享划分组。系数幅值、重命名、排列增强不计入新增数量。源公式、原文位置、维数条件和规范化表达分别保存。','',
        '两轮检查均通过：第一轮复现维数证据、归一化与结构键，并检查幂次上限和三变量任务约束；第二轮重新读取原始 HTML 公式锚点与内容，或核验原始 PDF、重新提取文本，并比对旧目录的函数实例记录。',
        f'独立符号检查覆盖 {components["signed_coefficient_bearing_systems_checked"]} 个需要展开或代入的系统，共 {components["scalar_equations_checked"]} 条保留符号与系数的标量方程。{args.unit_tests_passed} 项工具测试通过。两份审计记录指向同一个语料哈希。','',
        'Gierer–Meinhardt 的稳态椭圆系统按原文明列的结构变体记录，不当作新的物理机制。尚未对最终语料进行整体分组划分、增强或词表选择。','',
        '## 本轮新增条目','',
    ]
    lines.extend('- '+row['id']+' — '+str(len(row['normalized']['fields']))+' 变量 — [原文公式]('+row['source_url']+')' for row in added)
    (OUT/'EXPANSION_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({key:value for key,value in summary.items() if key!='added_ids'},ensure_ascii=False))


if __name__=='__main__':
    main()
