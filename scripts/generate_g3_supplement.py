#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""补充生成至500+题 + 生成缺失的单元3"""
import urllib.request, json, os, re, time
from collections import Counter

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

SCRIPT_DIR = os.path.dirname(__file__)
EXISTING_PATH = os.path.join(SCRIPT_DIR, "g3_batch_temp.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "generated_g3_full.json")

def call_llm(prompt, name):
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你严格输出JSON数组。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 8192,
    }
    headers = {"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}
    print(f"  [{name}] 调用API...", flush=True)
    try:
        with urllib.request.urlopen(
            urllib.request.Request(API_URL, data=json.dumps(data).encode(), headers=headers, method="POST"),
            timeout=300,
        ) as resp:
            r = json.loads(resp.read().decode())
            text = r["choices"][0]["message"]["content"]
            print(f"  [{name}] 返回{len(text)}字符", flush=True)
            return text
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

def fix(q, new_id, knowledge_override=None):
    q['id'] = new_id
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
    if 'explain' not in q or not q['explain']: q['explain'] = '请参考课文内容学习。'
    if knowledge_override:
        q['knowledge'] = knowledge_override
    elif 'knowledge' not in q or not q['knowledge']:
        q['knowledge'] = '三年级-其他'
    if not q['knowledge'].startswith('三年级-'):
        q['knowledge'] = '三年级-' + q['knowledge']
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

# ================================================================
#  第2轮生成：4个补充批次
# ================================================================
ADDITIONAL_PROMPTS = {
    "补充-课文理解": """生成chinese_g3科目选择题。每题必须明确knowledge字段。

第三单元课文：
1. 总也倒不了的老屋：老屋帮小猫和老母鸡、预测策略、多音字倒/缝/弹
2. 犟龟：坚持参加婚礼、被蜘蛛蜗牛壁虎劝阻、仍坚持
3. 小狗学叫：学各种动物叫、故事预测、多音字吗/担/压
4. 名字里的故事口语交际：名字含义
5. 习作续写故事
6. 语文园地三：识字加油站+日积月累

每道题的knowledge字段必须指定具体课文名：
- "三年级-课文-总也倒不了的老屋"
- "三年级-课文-犟龟"
- "三年级-课文-小狗学叫"
- "三年级-课文-语文园地三"

至少50题。JSON数组输出。id从后续递增。""",

    "补充-生字词语": """生成chinese_g3科目选择题，专门针对生字和词语理解。

要求：每道题的knowledge必须明确：
- 生字类用"三年级-生字-课文名"
- 词语类用"三年级-词语-课文名"
- 古诗生字用"三年级-古诗-诗名"

内容覆盖全部8个单元的生字：
- 第一单元：绒/昂/扬/凤/墙/晃/荒/笛/舞/狂/罚/假/诵/例/糊/戒/厉/挨
- 第二单元：径/斜/霜/挑/促/铺/印/列/规/则/凌/缤/枚/邮/爽/频/勾
- 第三单元：暴/壁/饿/饱/晒/眯/喵/孵/叽/陌/吗/讨/厌/怒/批/访/忍
- 第四单元：妖/乖/撵/烫/溜/拽/福/舔/旅/咱/偷/卷/骨/宣/诱/舔/捎
- 第五单元：搭/父/嘴/悄/吞/捕/旧/蒲/英/耍/钓/拢/欠/喜
- 第六单元：富/饶/优/瑰/岩/虾/粪/辈/滨/灰/渔/遍/躺/载/抽/嫩/汇/挡/刮/软/港/贸/商/旅
- 第七单元：妙/演/奏/琴/柔/感/受/激/击/册/覆/姿/态/笋/暑
- 第八单元：司/跌/皆/弃/持/争/努/础/研/考/试/绩/术/斗/血/仍/棒/粗/瓷/碗/抗

题型举例：看拼音选字、形近字辨析、字义选择
至少50题。JSON数组。""",

    "补充-多音字与词语": """生成chinese_g3科目选择题，专门针对多音字和词语积累。

多音字（每个出2题）：
假(jiǎ/jià)、背(bēi/bèi)、圈(quān/juàn)、好(hǎo/hào)、倒(dǎo/dào)、缝(féng/fèng)、弹(dàn/tán)、塞(sāi/sài/sè)、吗(má/ma)、担(dān/dàn)、压(yā/yà)、答(dā/dá)、骨(gū/gǔ)、嚼(jiáo/jué)、盛(shèng/chéng)、臂(bei/bì)、斗(dǒu/dòu)、血(xuè/xiě)、旋(xuán/xuàn)、铺(pū/pù)

词语积累（每个出2题）：
明朗、凌乱、五彩缤纷、摇头晃脑、面红耳赤、张牙舞爪、提心吊胆、口干舌燥、手忙脚乱、手疾眼快、披头散发

knowledge用"三年级-多音字"、"三年级-词语积累"
至少50题。JSON数组。""",

    "补充-古诗与园地": """生成chinese_g3科目选择题。

古诗综合（每首3题：内容、作者、字词）：
1. 望洞庭(刘禹锡) - 湖光秋月两相和/潭面无风镜未磨/遥望洞庭山水翠/白银盘里一青螺
2. 山行(杜牧) - 远上寒山石径斜/白云生处有人家/停车坐爱枫林晚/霜叶红于二月花
3. 夜书所见(叶绍翁) - 萧萧梧叶送寒声/江上秋风动客情/知有儿童挑促织/夜深篱落一灯明
4. 鹿柴(王维) - 空山不见人/但闻人语响/返景入深林/复照青苔上
5. 望天门山(李白) - 天门中断楚江开/碧水东流至此回/两岸青山相对出/孤帆一片日边来
6. 饮湖上初晴后雨(苏轼) - 水光潋滟晴方好/山色空蒙雨亦奇/欲把西湖比西子/淡妆浓抹总相宜

语文园地（每个园地3题）：
园地一：成语+所见(袁枚)
园地二：日记格式+词语理解
园地三：识字加油站+谚语
园地四：识字+词句段
园地五：观察交流
园地六：词句段+古诗名句
园地七：词句段+日积月累
园地八：识字+词句段+日积月累

knowledge用"三年级-古诗-诗名"、"三年级-语文园地X"
至少50题。JSON数组。"""
}

def main():
    # 读取已有题目
    existing = []
    if os.path.exists(EXISTING_PATH):
        with open(EXISTING_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)
    
    next_id = max((q['id'] for q in existing), default=278) + 1 if existing else 279
    print(f"已有: {len(existing)} 题, 起始ID: {next_id}")
    print(f"目标: 500+ 题")
    
    all_q = list(existing)
    
    for name, prompt in ADDITIONAL_PROMPTS.items():
        print(f"\n>>> {name} <<<")
        text = call_llm(prompt, name)
        raw = parse(text)
        valid_batch = []
        for item in raw:
            fixed = fix(item, next_id + len(valid_batch))
            if valid(fixed):
                valid_batch.append(fixed)
        all_q.extend(valid_batch)
        next_id += len(valid_batch)
        print(f"  有效: {len(valid_batch)}, 累计: {len(all_q)}")
        
        # 保存中间结果
        with open(EXISTING_PATH, "w", encoding="utf-8") as f:
            json.dump(all_q, f, ensure_ascii=False, indent=2)
        
        time.sleep(2)
    
    # 最终保存
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_q, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"最终结果: {len(all_q)} 题")
    if len(all_q) >= 500:
        print(f"✅ 达标! ≥500题")
    else:
        print(f"⚠️ 还差 {500 - len(all_q)} 题")
    
    kp = Counter(q['knowledge'] for q in all_q)
    print(f"\n知识点 (前20):")
    for k, c in kp.most_common(20):
        print(f"  {k}: {c}题")
    
    diff = Counter(q['difficulty'] for q in all_q)
    print(f"\n难度:")
    for d in sorted(diff):
        print(f"  难度{d}: {diff[d]}题")
    
    print(f"\n输出文件: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
