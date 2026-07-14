#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""最终补充：古诗+园地+几篇缺覆盖的课文"""
import urllib.request, json, os, re, time

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

SCRIPT_DIR = os.path.dirname(__file__)
EXISTING_PATH = os.path.join(SCRIPT_DIR, "generated_g3_full.json")

def call(text, name):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是语文命题专家。输出JSON数组。"},
            {"role": "user", "content": text},
        ],
        "temperature": 0.3, "max_tokens": 8192,
    }
    h = {"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}
    print(f"  [{name}] 调用API...", flush=True)
    try:
        with urllib.request.urlopen(urllib.request.Request(API_URL, data=json.dumps(data).encode(), headers=h, method="POST"), timeout=300) as r:
            t = json.loads(r.read().decode())["choices"][0]["message"]["content"]
            print(f"  [{name}] 返回{len(t)}字符", flush=True)
            return t
    except Exception as e:
        print(f"  [{name}] 错误: {e}", flush=True)
        return "[]"

def parse(text):
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?\s*```$', '', text)
    s, e = text.find('['), text.rfind(']')
    if s == -1 or e == -1: return []
    c = text[s:e+1]
    while len(c) > 50:
        try: return json.loads(c) if isinstance(json.loads(c), list) else []
        except:
            last = c.rfind('{')
            if last <= 1: break
            c = c[:last]
            c = c.rstrip(',') + ']'
    return []

def fix(q, nid):
    q['id'] = nid
    q['type'] = 'fill'
    q['subject'] = 'chinese_g3'
    opts = list(dict.fromkeys([str(o).strip() for o in q.get('options',[])]))
    ans = str(q.get('answer','')).strip()
    if ans not in opts: opts.insert(0, ans)
    while len(opts) < 3: opts.append('其他')
    q['options'] = opts[:3]
    q['answer'] = ans
    try: q['difficulty'] = max(1, min(5, int(str(q.get('difficulty',1)))))
    except: q['difficulty'] = 1
    if 'explain' not in q or not q['explain']: q['explain'] = '请学习课文内容。'
    if 'knowledge' not in q or not q['knowledge']: q['knowledge'] = '三年级-其他'
    if not q['knowledge'].startswith('三年级-'): q['knowledge'] = '三年级-' + q['knowledge']
    return q

def valid(q):
    for r in ['id','subject','type','question','answer','options','explain','difficulty','knowledge']:
        if r not in q: return False
    if q.get('type') not in ('fill','choice'): return False
    if q['subject'] != 'chinese_g3': return False
    if q['answer'] not in q['options']: return False
    if len(set(q['options'])) != len(q['options']): return False
    if len(q['options']) < 3: return False
    return True

prompts = [
    ("古诗最终批", """生成chinese_g3选择题。JSON数组。

古诗（每首出3题：内容+作者+字词）：
1. 望洞庭(刘禹锡) - 湖光秋月两相和/潭面无风镜未磨/遥望洞庭山水翠/白银盘里一青螺
2. 山行(杜牧) - 远上寒山石径斜/白云生处有人家/停车坐爱枫林晚/霜叶红于二月花
3. 夜书所见(叶绍翁) - 萧萧梧叶送寒声/江上秋风动客情/知有儿童挑促织/夜深篱落一灯明
4. 鹿柴(王维) - 空山不见人/但闻人语响/返景入深林/复照青苔上
5. 望天门山(李白) - 天门中断楚江开/碧水东流至此回/两岸青山相对出/孤帆一片日边来
6. 饮湖上初晴后雨(苏轼) - 水光潋滟晴方好/山色空蒙雨亦奇/欲把西湖比西子/淡妆浓抹总相宜

knowledge字段必须用"三年级-古诗-诗名"格式。至少30题。"""),

    ("课文补充", """生成chinese_g3选择题。

出题课文及knowledge格式要求：
- "三年级-课文-大自然的声音"：风是音乐家、水是音乐家、动物是歌手
- "三年级-课文-读不完的大书"：大自然无穷奥秘
- "三年级-课文-司马光"：砸缸救小孩文言文
- "三年级-课文-一定要争气"：童第周刻苦学习
- "三年级-课文-手术台就是阵地"：白求恩
- "三年级-课文-一个粗瓷大碗"：赵一曼
- "三年级-语文园地二"：日记格式+理解词语
- "三年级-语文园地四""：童话+识字
- "三年级-语文园地五"：观察方法
- "三年级-语文园地六"：词句段+古诗名句
- "三年级-语文园地七"：词句段+日积月累
- "三年级-语文园地八"：识字+词句段

至少30题。JSON数组。""")
]

# 读取已有
with open(EXISTING_PATH, "r", encoding="utf-8") as f:
    existing = json.load(f)

next_id = max(q['id'] for q in existing) + 1
all_q = list(existing)
print(f"已有: {len(all_q)} 题, 起始ID: {next_id}")

for name, prompt in prompts:
    print(f"\n>>> {name} <<<")
    text = call(prompt, name)
    raw = parse(text)
    vb = []
    for item in raw:
        fixed = fix(item, next_id + len(vb))
        if valid(fixed):
            vb.append(fixed)
    all_q.extend(vb)
    next_id += len(vb)
    print(f"  有效: {len(vb)}, 累计: {len(all_q)}")
    time.sleep(2)

with open(EXISTING_PATH, "w", encoding="utf-8") as f:
    json.dump(all_q, f, ensure_ascii=False, indent=2)

from collections import Counter
kp = Counter(q['knowledge'] for q in all_q)
print(f"\n{'='*60}")
print(f"最终: {len(all_q)} 题")
print(f"{'✅ 达标!' if len(all_q) >= 500 else f'⚠️ 还差{500-len(all_q)}题'}")
print(f"\n知识点分布:")
for k, c in kp.most_common(25):
    print(f"  {k}: {c}题")
