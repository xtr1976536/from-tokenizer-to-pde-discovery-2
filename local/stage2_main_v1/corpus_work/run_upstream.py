"""Stage0-style train-only AST-BPE capacity sweep; validation-only top-three."""
import json,re,math,csv,sys
from pathlib import Path
from hashlib import sha256
from collections import Counter
import numpy as np
from curation import ROOT,OUT
sys.path.insert(0,str(ROOT/'math_tokenizer_project_release/src'))
from compact_ast_bpe import train_compact,derive_alphabet,CompactAlphabet,HardASTBPE
from structure_latex import normalize_system

SIZES=list(range(100,1501,50))


def evaluate(model,rows):
    initial=final=cmd_total=cmd_good=num_total=num_good=0;used=set();roundtrip=0;lengths=[]
    for row in rows:
        text=row['normalized']['text'];ids=model.encode(text)
        assert model.decode(ids)==text,row['id']
        assert normalize_system(text.split(chr(92)*2),row['normalized']['fields'])['text']==text
        roundtrip+=1;initial+=len(text.encode());final+=len(ids);used.update(ids);lengths.append(len(ids))
        cuts=set(np.cumsum([len(model.vocab[i]) for i in ids]).tolist())
        for pattern,kind in [(r'\\[A-Za-z]+','command'),(r'[0-9]+(?:\.[0-9]+)?','number')]:
            for match in re.finditer(pattern,text):
                begin=len(text[:match.start()].encode());end=len(text[:match.end()].encode())
                good=not any(begin<c<end for c in cuts)
                if kind=='command':cmd_total+=1;cmd_good+=good
                else:num_total+=1;num_good+=good
    added={i for i,b in enumerate(model.vocab) if len(b)>1}
    return dict(formulas=len(rows),initial_tokens=initial,final_tokens=final,compression=initial/final,
                command_integrity=cmd_good/max(1,cmd_total),number_integrity=num_good/max(1,num_total),
                commands=cmd_total,numbers=num_total,added_token_usage=len(used&added)/max(1,len(added)),
                added_token_types=len(added),used_added_token_types=len(used&added),
                roundtrip_success=roundtrip,len_mean=float(np.mean(lengths)),len_max=max(lengths),len_p95=float(np.percentile(lengths,95)))


def main():
    frozen=OUT/'frozen';folder=OUT/'upstream';folder.mkdir(exist_ok=True)
    splits={name:[json.loads(l) for l in (frozen/(name+'.jsonl')).read_text().splitlines()] for name in ('train','validation','test')}
    texts=[r['normalized']['text'] for r in splits['train']]
    # Alphabet depends only on unaugmented training text plus the inherited
    # numeric alphabet. Missing held-out bytes cause failure, never silent UNK.
    alphabet=derive_alphabet(texts)
    sizes=[s for s in SIZES if s>=len(alphabet)+3]
    protocol=dict(capacities=sizes,capacity_includes=['content','PAD','EOS','BOS'],step=50,
        alphabet_size=len(alphabet),alphabet_source='unaugmented train + stage1 numeric alphabet',
        vocab_training='unaugmented train only',selection_data='validation only',
        hard_gates=['exact-byte round trip for every formula','canonical reparse','command integrity=1','number integrity=1'],
        ranking='sqrt((validation compression/max eligible compression)*(validation added-token usage/max eligible usage)); top3, then smaller capacity on ties',
        model='Unmodified Stage1 HardASTBPE + CompactAlphabet; ranked merge prefixes of one maximum-capacity fit',
        scope='Stage0 capacity-selection task and its four metrics; no Transformer pretraining; no generic-tokenizer comparison or separate easy-to-hard experiment claimed',
        range_extension='Initial 100..1000 scan found only two capacities with full command integrity; extend upper bound to1500 without changing gates or reading test data. Rare sinh command is fragmented below950.',
        split_manifest_sha256=sha256((frozen/'split-manifest.json').read_bytes()).hexdigest())
    # Save selection protocol BEFORE training or inspecting validation metrics.
    (folder/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
    largest=CompactAlphabet('ast_bpe',alphabet,HardASTBPE.train(texts,max(sizes)+256-len(alphabet)-3))
    actual_maximum=len(largest.vocab)+3
    protocol['maximum_supported_content_and_control_ids']=actual_maximum
    protocol['unfilled_capacities']=[s for s in sizes if s>actual_maximum]
    protocol['unfilled_rule']='Do not invent unused tokens or report requested capacity as actual capacity'
    sizes=[s for s in sizes if s<=actual_maximum]
    (folder/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
    results=[];models={}
    for capacity in sizes:
        n=capacity+256-len(alphabet)-3
        vocab=largest.internal.vocab[:n]
        merges=[]
        for merge in largest.internal.merges:
            if max(merge)>=n:break
            merges.append(merge)
        model=CompactAlphabet('ast_bpe',alphabet,HardASTBPE(vocab,merges))
        assert len(model.vocab)+3==capacity
        model.save(folder/f'ast-bpe-{capacity}.json');models[capacity]=model
        metrics=evaluate(model,splits['validation'])
        row=dict(vocab_size=capacity,split='validation',**metrics)
        row['eligible']=metrics['command_integrity']==1 and metrics['number_integrity']==1
        results.append(row)
        print(capacity,'compression',round(metrics['compression'],4),'usage',round(metrics['added_token_usage'],4),'eligible',row['eligible'],flush=True)
    eligible=[r for r in results if r['eligible']]
    assert len(eligible)>=3,'Fewer than three capacities meet integrity gates; do not weaken gates automatically'
    maxC=max(r['compression'] for r in eligible);maxU=max(r['added_token_usage'] for r in eligible)
    for r in results:r['selection_score']=math.sqrt(r['compression']/maxC*r['added_token_usage']/maxU) if r['eligible'] else None
    selected=sorted(eligible,key=lambda r:(-r['selection_score'],r['vocab_size']))[:3]
    selection=dict(status='SELECTED_BY_VALIDATION_BEFORE_TEST',vocab_sizes=[r['vocab_size'] for r in selected],
                   ranking=protocol['ranking'],validation_rows=selected,formal_downstream_training_started=False)
    (folder/'selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n')
    # The test set is accessed for metric reporting only AFTER selection saved.
    test=[dict(vocab_size=r['vocab_size'],split='test',**evaluate(models[r['vocab_size']],splits['test'])) for r in selected]
    (folder/'validation-sweep.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    (folder/'selected-test-metrics.json').write_text(json.dumps(test,ensure_ascii=False,indent=2)+'\n')
    with (folder/'validation-sweep.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    lines=['# 阶段2上游词表评估','',
           '复用阶段1 HardASTBPE 与 CompactAlphabet。词表仅从未增强训练集学习；先保存验证选择规则，再运行扫描；选出三个词表并写盘后，才评价测试集。',
           '',f'验证集选出的三个词表（包含三个控制符）：{selection["vocab_sizes"]}。以 50 为步长扫描 100–1500。初始上限1000时只有两个容量满足命令完整率门槛，因此在未访问测试集的情况下扩展上限，门槛保持不变。',
           '', '筛选要求所有公式无损编解码并可重新解析、命令完整率和数字完整率均为100%；在合格词表中按验证压缩率与新增词表使用率的归一化几何平均排序。这个规则属于本轮准备配置，老师修改意见落实后可重新评估，不能依据下游测试结果反选词表。',
           '', '|词表大小|验证压缩率|验证新增词表使用率|命令完整率|数字完整率|选择分数|',
           '|---:|---:|---:|---:|---:|---:|']
    for r in results:lines.append(f'|{r["vocab_size"]}|{r["compression"]:.4f}|{r["added_token_usage"]:.2%}|{r["command_integrity"]:.2%}|{r["number_integrity"]:.2%}|'+(f'{r["selection_score"]:.4f}' if r['eligible'] else '不合格')+'|')
    lines+=['','本轮完成的是阶段0式的容量扫描与分词指标评估；没有声称完成通用分词器对照或独立简单到复杂泛化实验，也没有启动 EQGPT 预训练。原始结果、词表、合并规则和数据哈希随目录保存。','']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    print('SELECTED',selection['vocab_sizes'])


if __name__=='__main__':main()
