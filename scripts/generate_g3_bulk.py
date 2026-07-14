#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
知识空战 - 三年级上册全量题库生成 v3
分段批量调用deepseek-v4-flash，每批~50题
"""
import urllib.request, json, sys, os, re, time
from collections import Counter

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

SCRIPT_DIR = os.path.dirname(__file__)
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "generated_g3_full.json")

SYSTEM_PROMPT = "你是三年级语文命题专家。严格输出JSON数组，不要任何其他文字。"

def call_llm(prompt: str, name: str) -> str:
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
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

def parse(text: str) -> list:
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?\s*```$', '', text)
    s, e = text.find('['), text.rfind(']')
    if s == -1 or e == -1:
        return []
    c = text[s:e+1]
    # 逐步缩短找有效JSON（处理截断）
    while len(c) > 50:
        try:
            parsed = json.loads(c)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            # 去掉最后一个不完整对象
            last = c.rfind('{')
            if last <= 1:
                break
            c = c[:last]
            c = c.rstrip(',') + ']'
    return []

def fix(q, new_id):
    q['id'] = new_id
    q['type'] = 'fill'
    q['subject'] = 'chinese_g3'
    if 'options' not in q or not q['options']:
        q['options'] = ['不知道', '不确定', '其他']
    opts = list(dict.fromkeys([str(o).strip() for o in q['options']]))
    ans = str(q.get('answer','')).strip()
    if ans not in opts:
        opts.insert(0, ans)
    while len(opts) < 3:
        opts.append('其他')
    q['options'] = opts[:3]
    q['answer'] = ans
    if 'difficulty' not in q:
        q['difficulty'] = 1
    try:
        q['difficulty'] = max(1, min(5, int(str(q['difficulty']))))
    except:
        q['difficulty'] = 1
    if 'explain' not in q or not q['explain']:
        q['explain'] = '请参考课文内容。'
    if 'knowledge' not in q or not q['knowledge']:
        q['knowledge'] = '三年级-其他'
    if not q['knowledge'].startswith('三年级-'):
        q['knowledge'] = '三年级-' + q['knowledge']
    # 规范化knowledge：去掉多余后缀
    q['knowledge'] = q['knowledge'].replace('课文-课文-', '课文-')
    return q

def valid(q):
    for r in ['id','subject','type','question','answer','options','explain','difficulty','knowledge']:
        if r not in q: return False
    if q.get('type') not in ('fill', 'choice'): return False
    if q['subject'] != 'chinese_g3': return False
    if q['answer'] not in q['options']: return False
    if len(set(q['options'])) != len(q['options']): return False
    if len(q['options']) < 3: return False
    if len(q.get('question','')) < 4: return False
    return True

# ================================================================
#  8个单元prompts - 每个至少40题，精简prompt
# ================================================================
PROMPTS = {
    "单元1": """生成chinese_g3科目选择题给三年级学生。JSON数组输出。

第一单元课文：
1. 大青树下的小学：学生来自山坡/坪坝/小路，多个民族，窗外安静听读书，生字绒/昂/扬/凤/墙/晃
2. 花的学校：泰戈尔作品，花在地下学校上学，湿润的东风，生字荒/笛/舞/狂/罚/假/互/所/够/猜/扬/臂
3. 不懂就要问：孙中山背书问先生，挨打也值得，生字诵/例/糊/戒/厉/详/挨/背/圈
4. 语文园地一：成语摇头晃脑/张牙舞爪/面红耳赤/提心吊胆，日积月累《所见》袁枚
5. 口语交际我的暑假生活，习作猜猜他是谁

每课至少6题（内容理解+生字+词语+多音字）。knowledge用"三年级-课文-课名"。
id从279开始。每个对象含id,subject,type,question,answer,options,explain,difficulty,knowledge。
answer在options中，options共3个不重复。至少40题。""",

    "单元2": """生成chinese_g3选择题。JSON数组。

第二单元：
1. 古诗三首：望洞庭(刘禹锡)-湖光秋月两相和/潭面无风镜未磨/遥望洞庭山水翠/白银盘里一青螺。山行(杜牧)-远上寒山石径斜/白云生处有人家/停车坐爱枫林晚/霜叶红于二月花。夜书所见(叶绍翁)-萧萧梧叶送寒声/江上秋风动客情/知有儿童挑促织/夜深篱落一灯明。每首4题
2. 铺满金色巴掌的水泥道：金色巴掌=梧桐叶，水泥道像地毯，词语明朗/凌乱/增添/印
3. 秋天的雨：钥匙打开秋天，五彩缤纷的颜料，生字钥/匙/缤/枚/邮/爽/橘/频
4. 听听秋的声音：刷刷/㘗㘗拟声词
5. 语文园地二：日记格式(日期+天气)，理解词语的方法
6. 习作写日记

至少40题。""",

    "单元3": """生成chinese_g3选择题。JSON数组。

第三单元（阅读策略单元-预测）：
1. 总也倒不了的老屋：老屋帮小猫和老母鸡，多音字倒/缝/弹，生字暴/壁/饿/饱/晒
2. 犟龟：坚持参加狮子婚礼，途中被蜘蛛/蜗牛/壁虎劝退仍坚持
3. 小狗学叫：学各种动物叫，多音字吗/担/压，生字吗/讨/厌/怒/批/访
4. 口语交际名字里的故事，习作续写故事
5. 语文园地三：识字加油站+日积月累

至少40题。""",

    "单元4": """生成chinese_g3选择题。JSON数组。

第四单元：
1. 宝葫芦的秘密：王葆想要宝葫芦，宝葫芦能变出一切，生字妖/乖/撵/烫/溜/拽/福/舔
2. 在牛肚子里旅行：红头在牛嘴里→肚子→回来的路线，反刍知识，多音字答/骨/嚼
3. 一块奶酪：蚂蚁队长，奶酪渣，生字宣/诱/舔/捎/跺/聚/毅
4. 习作我来编童话，语文园地四

至少40题。""",

    "单元5": """生成chinese_g3选择题。JSON数组。

第五单元（习作单元-观察）：
1. 搭船的鸟：翠鸟-翠绿羽毛/红色长嘴，捕鱼动作冲/飞/衔/站/吞，生字搭/父/嘴/悄/吞/捕/旧
2. 金色的草地：早上绿→中午金→晚上绿，蒲公英花瓣开合，多音字盛，生字蒲/英/耍/钓/拢/欠/喜
3. 习作我们眼中的缤纷世界+我家的小狗+我爱故乡的杨梅
4. 语文园地五：交流观察所得

至少40题。""",

    "单元6": """生成chinese_g3选择题。JSON数组。

第六单元：
1. 富饶的西沙群岛：海水五光十色，珊瑚/海参/龙虾/鸟类，生字富/饶/优/瑰/岩/虾/粪/辈
2. 海滨小城：大海-沙滩-庭院-公园-街道，生字滨/灰/渔/遍/躺/载/栽/亚
3. 美丽的小兴安岭：春夏秋冬四季景色，抽新枝/长嫩叶/封/挡/刮，生字抽/嫩/汇/挡/刮/软
4. 香港璀璨的明珠：东方之珠，万国市场/美食天堂/旅游胜地，生字港/贸/商/旅
5. 习作这儿真美，语文园地六

至少40题。""",

    "单元7": """生成chinese_g3选择题。JSON数组。

第七单元：
1. 古诗三首：鹿柴(王维)-空山不见人/但闻人语响/返景入深林/复照青苔上。望天门山(李白)-天门中断楚江开/碧水东流至此回/两岸青山相对出/孤帆一片日边来。饮湖上初晴后雨(苏轼)-水光潋滟晴方好/山色空蒙雨亦奇/欲把西湖比西子/淡妆浓抹总相宜。每首4题
2. 大自然的声音：风是音乐家，水是音乐家，动物是歌手，生字妙/演/奏/琴/柔/感/受/激/击
3. 读不完的大书：大自然有无穷奥秘，生字册/覆/姿/态/笋/暑，多音字旋
4. 口语交际身边的小事，习作我有一个想法
5. 语文园地七

至少40题。""",

    "单元8": """生成chinese_g3选择题。JSON数组。

第八单元：
1. 司马光：文言文-群儿戏于庭/一儿登瓮/足跌没水中/众皆弃去/光持石击瓮破之，生字司/跌/皆/弃/持
2. 一定要争气：童第周刻苦学习，一定要争气精神，生字争/努/础/研/考/试/绩
3. 手术台就是阵地：白求恩在战场做手术，多音字斗/血/弹，生字术/斗/血/仍/棒
4. 一个粗瓷大碗：赵一曼粗瓷大碗，生字粗/瓷/碗/抗/联/感/谢
5. 口语交际请教，习作那次经历真难忘
6. 语文园地八

至少40题。"""
}

def main():
    next_id = 279
    print("="*60)
    print(f"三年级上册全量题库生成 v3")
    print(f"模型: {MODEL}, 共 {len(PROMPTS)} 批")
    print("="*60)

    all_q = []
    for unit_key, prompt in PROMPTS.items():
        print(f"\n>>> {unit_key} <<<")
        text = call_llm(prompt, unit_key)
        raw = parse(text)
        valid_batch = []
        for item in raw:
            fixed = fix(item, next_id + len(valid_batch))
            if valid(fixed):
                valid_batch.append(fixed)
        all_q.extend(valid_batch)
        next_id += len(valid_batch)
        print(f"  有效: {len(valid_batch)}, 累计: {len(all_q)}")
        
        # 每批保存临时
        with open(os.path.join(SCRIPT_DIR, "g3_batch_temp.json"), "w", encoding="utf-8") as f:
            json.dump(all_q, f, ensure_ascii=False, indent=2)
        
        time.sleep(2)

    # 最终输出
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_q, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"生成完成! 总 {len(all_q)} 题")
    if len(all_q) >= 500:
        print(f"✅ 达到目标 ≥500题!")
    else:
        print(f"还需 {500 - len(all_q)} 题达目标")

    kp = Counter(q['knowledge'] for q in all_q)
    print(f"\n知识点分布 (前20):")
    for k, c in kp.most_common(20):
        print(f"  {k}: {c}题")
    
    diff = Counter(q['difficulty'] for q in all_q)
    print(f"\n难度分布:")
    for d in sorted(diff):
        print(f"  难度{d}: {diff[d]}题")

if __name__ == "__main__":
    main()
