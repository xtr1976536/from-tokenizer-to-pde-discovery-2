"""Two equally primary upstream splits; four metrics, no ranking/selection."""
import json,csv,sys,argparse
from pathlib import Path
from hashlib import sha256
from curation import ROOT
sys.path.insert(0,str(ROOT/'math_tokenizer_project_release/src'))
from compact_ast_bpe import CompactAlphabet,HardASTBPE,derive_alphabet
from run_upstream import evaluate


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT/'outputs/eqgpt-research/stage2-preparation-2026-11-16');args=ap.parse_args()
    all_rows=[]
    for name in ('811','622'):
        frozen=args.root/name/'frozen';folder=args.root/name/'upstream';folder.mkdir(parents=True,exist_ok=True)
        splits={key:[json.loads(l) for l in (frozen/(key+'.jsonl')).read_text().splitlines()] for key in ('train','validation')}
        texts=[r['normalized']['text'] for r in splits['train']];alphabet=derive_alphabet(texts)
        sizes=list(range(64,500,32))
        assert min(sizes)>len(alphabet)+3
        protocol=dict(experiment=name,role='primary',capacities=sizes,step=32,capacity_includes_control_ids=True,
            metrics=['compression','command_integrity','number_integrity','added_token_usage'],
            integrity_threshold=None,ranking=None,automatic_selection=False,
            vocabulary_fit='unaugmented training only',table_scope='validation for user vocabulary choice; test unopened until choice frozen',
            split_manifest_sha256=sha256((frozen/'split-manifest.json').read_bytes()).hexdigest(),alphabet_size=len(alphabet))
        (folder/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
        largest=CompactAlphabet('ast_bpe',alphabet,HardASTBPE.train(texts,max(sizes)+256-len(alphabet)-3))
        results=[]
        for capacity in sizes:
            n=capacity+256-len(alphabet)-3;merges=[]
            for merge in largest.internal.merges:
                if max(merge)>=n:break
                merges.append(merge)
            model=CompactAlphabet('ast_bpe',alphabet,HardASTBPE(largest.internal.vocab[:n],merges))
            assert len(model.vocab)+3==capacity
            model.save(folder/f'ast-bpe-{capacity}.json')
            metrics=evaluate(model,splits['validation'])
            result=dict(experiment=name,vocab_size=capacity,split='validation',**metrics)
            results.append(result);all_rows.append(result)
        (folder/'four-metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
        with (folder/'four-metrics.csv').open('w') as f:
            writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
        print(name,'capacities',len(results),'train',len(splits['train']),'validation',len(splits['validation']),flush=True)
    lines=['# 两套主实验的上游词表指标','',
        '8:1:1与6:2:2均为主实验；词表大小包含PAD/EOS/BOS三个控制符。词表只从各自未增强训练集学习。取消完整率门槛，不排序、不自动选词表。',
        '', '以下给出验证集四项指标供用户选择词表；测试集在词表选择冻结前不读取。来源/近似结构按整组隔离，因此实际条数允许偏离精确比例。',
        '', '|划分|词表大小|压缩率|命令完整率|数字完整率|新增词表使用率|',
        '|---|---:|---:|---:|---:|---:|']
    for r in all_rows:lines.append(f'|{r["experiment"]}|{r["vocab_size"]}|{r["compression"]:.4f}|{r["command_integrity"]:.2%}|{r["number_integrity"]:.2%}|{r["added_token_usage"]:.2%}|')
    lines+=['','四项指标沿用用户提供阶段0定义：压缩率=初始单字节token数/编码后token数；命令/数字完整率为内部没有token边界的完整命令/数字串比例；新增词表使用率=验证中实际出现的新增token种数/全部新增token种数。无损编解码与重新解析另作正确性检查，不用完整率剔除容量。','']
    (args.root/'UPSTREAM_TABLES.md').write_text('\n'.join(lines))
    with (args.root/'UPSTREAM_TABLES.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)


if __name__=='__main__':main()
