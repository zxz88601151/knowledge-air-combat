#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
知识空战 - 三年级上册独立模块 LLM 生成
基于部编版三年级上册语文教材PDF内容
"""
import urllib.request, json, sys, os, re

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

SCRIPT_DIR = os.path.dirname(__file__)
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "generated_g3.json")
RAW_PATH = os.path.join(SCRIPT_DIR, "g3_raw.txt")

SYSTEM_PROMPT = "你是一位资深小学语文教师，擅长根据课文内容出选择题。严格输出JSON数组。"

def call_llm(prompt: str) -> str:
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 8192,
    }
    headers = {"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}
    with urllib.request.urlopen(
        urllib.request.Request(API_URL, data=json.dumps(data).encode(), headers=headers, method="POST"),
        timeout=300,
    ) as resp:
        r = json.loads(resp.read().decode())
        return r["choices"][0]["message"]["content"]

def parse_json(text: str) -> list:
    text = text.strip()
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?\s*```$', '', text)
    start, end = text.find('['), text.rfind(']')
    if start != -1 and end != -1:
        c = text[start:end+1]
        try: return json.loads(c)
        except: pass
        c = re.sub(r',(\s*[\]}])', r'\1', c)
        try: return json.loads(c)
        except: pass
    objs = re.findall(r'\{[^{}]*\}', text)
    r = []
    for m in objs:
        try:
            o = json.loads(m)
            if 'question' in o and 'answer' in o:
                r.append(o)
        except: pass
    return r

def fix(q: dict, new_id: int) -> dict:
    q['id'] = new_id
    q['type'] = 'fill'
    if 'subject' not in q: q['subject'] = 'chinese_g3'
    opts = list(dict.fromkeys([str(o).strip() for o in q.get('options',[])]))
    ans = str(q.get('answer','')).strip()
    if ans not in opts: opts.insert(0, ans)
    while len(opts) < 3: opts.append('不知道')
    q['options'] = opts[:3]
    q['answer'] = ans
    try: q['difficulty'] = max(1, min(5, int(str(q.get('difficulty',1)))))
    except: q['difficulty'] = 1
    if 'knowledge' not in q or not q['knowledge']: q['knowledge'] = '三年级-其他'
    return q

def validate(q: dict) -> bool:
    for r in ['id','subject','type','question','answer','options','explain','difficulty','knowledge']:
        if r not in q: return False
    if q.get('type')!='fill': return False
    if q['subject'] not in ('chinese_g3',): return False
    if q['answer'] not in q['options']: return False
    if len(set(q['options']))!=len(q['options']): return False
    if len(q['options'])<3: return False
    return True

PROMPT = f"""生成"知识空战"射击答题游戏题目，面向三年级学生。严格输出 JSON 数组。

每题格式：
{{"id":N,"subject":"chinese_g3","type":"fill","question":"...","answer":"...","options":["...","...","..."],"explain":"...","difficulty":1,"knowledge":"三年级-..."}}

id 从 239 开始递增。

## 以下是根据部编版三年级上册语文教材设计的题目，请严格按照要求生成

### 第一类：古诗与日积月累（10题，knowledge="三年级-古诗日积月累"）

1. 鹿柴（王维）: "空山不见人"的下一句是？答案：但闻人语响。干扰项：但见人语响、近听人语响
2. 鹿柴: "返景入深林"的下一句是？答案：复照青苔上。干扰项：复照青松上、又照青苔上  
3. 鹿柴的作者是？答案：王维。干扰项：孟浩然、杜甫
4. "鹿柴"中"柴"的正确读音是？答案：zhài。干扰项：chái、zài
5. 日积月累《所见》(袁枚): "牧童骑黄牛"的下一句是？答案：歌声振林樾。干扰项：歌声震林樾、歌声满林间
6. 《所见》: "意欲捕鸣蝉"的下一句是？答案：忽然闭口立。干扰项：忽然闭目立、忽然开口立  
7. 《所见》的作者是？答案：袁枚。干扰项：袁牧、杜甫
8. "意欲捕鸣蝉"中"欲"的意思是？答案：想要。干扰项：欲望、将要
9. "歌声振林樾"中"振"的意思是？答案：振荡。干扰项：振奋、振兴
10. 山行描写的是什么季节？答案：秋天。干扰项：春天、夏天

### 第二类：课文内容理解（10题，knowledge="三年级-课文理解"）

11. 《大青树下的小学》中，同学们来自哪些民族？答案：多个不同民族。干扰项：全是汉族、全是傣族
12. 《大青树下的小学》中，窗外为什么安静？答案：大家被读书声吸引。干扰项：没人在外面、天气太冷
13. 《花的学校》的作者是？答案：泰戈尔。干扰项：吴然、张秋生
14. 《不懂就要问》中，孙中山为什么问先生？答案：想弄懂书里意思。干扰项：想捣乱、想考先生
15. 《铺满金色巴掌的水泥道》中，"金色巴掌"指的是？答案：梧桐叶。干扰项：银杏叶、枫叶
16. 《秋天的雨》中，秋天的雨是什么颜色的？答案：五彩缤纷。干扰项：金黄色的、红色的
17. 《总也倒不了的老屋》中，老屋帮助了谁？答案：小猫和老母鸡。干扰项：小狗和小猫、小兔和小猫
18. 《司马光》中，司马光用什么方法救小孩？答案：砸缸。干扰项：拉出水面、叫大人来
19. 《搭船的鸟》中，搭船的是一只什么鸟？答案：翠鸟。干扰项：麻雀、燕子
20. 《美丽的小兴安岭》中，小兴安岭什么季节最美？答案：四季都美。干扰项：只有春天美、只有秋天美

### 第三类：成语积累（8题，knowledge="三年级-成语积累"）

21. "摇头晃脑"形容什么？答案：自得其乐的样子。干扰项：头疼的样子、困倦的样子
22. "面红耳赤"形容什么？答案：激动或害羞的样子。干扰项：脸色红润、生气的样子
23. "张牙舞爪"形容什么？答案：凶恶的样子。干扰项：高兴的样子、跳舞的样子
24. "手忙脚乱"形容什么？答案：慌张的样子。干扰项：勤劳的样子、忙碌的样子
25. "提心吊胆"的意思是？答案：非常担心害怕。干扰项：非常高兴、非常轻松
26. "口干舌燥"的意思是？答案：非常口渴。干扰项：舌头干燥、说话响亮
27. "手疾眼快"形容什么？答案：动作敏捷。干扰项：视力很好、手部受伤
28. "披头散发"形容什么？答案：仪容不整。干扰项：发型好看、头发很乱

### 第四类：字词与语文园地（12题）

29-32: 多音字（knowledge="三年级-多音字"）
29. "假"在"假期"中读？答案：jià。干扰项：jiǎ、jiā
30. "背"在"背诵"中读？答案：bèi。干扰项：bēi、béi
31. "圈"在"羊圈"中读？答案：juàn。干扰项：quān、juān
32. "挨"在"挨打"中读？答案：ái。干扰项：āi、ǎi

33-36: 词语理解（knowledge="三年级-词语理解"）
33. "明朗"在"明朗的天空"中的意思是？答案：明亮晴朗。干扰项：明明、明亮
34. "凌乱"的意思是？答案：不整齐。干扰项：很整齐、很凌冽  
35. "五彩缤纷"的意思是？答案：颜色很多很美丽。干扰项：只有五种颜色、五彩的颜色
36. "鸦雀无声"形容什么？答案：非常安静。干扰项：声音很大、乌鸦在叫

37-40: 语文园地（knowledge="三年级-语文园地"）
37. "所"字的部首是什么？答案：户。干扰项：斤、一
38. "日记"一般在正文前要写什么？答案：日期和天气。干扰项：只有日期、标题和日期
39. 口语交际"我的暑假生活"中，借助什么能让别人更好理解？答案：图片或实物。干扰项：声音或动作、文字或表情
40. 写人的习作中，不能出现什么？答案：他的名字。干扰项：他的特点、他的外貌

直接输出 JSON 数组，不要任何其他文字。确保每个题目的 answer 在 options 中。"""

def main():
    print(">> 调用 LLM 生成三年级上册题目...", flush=True)
    text = call_llm(PROMPT)
    print(f">> 返回 {len(text)} 字符", flush=True)

    raw = parse_json(text)
    print(f">> 解析到 {len(raw)} 条", flush=True)

    valid = []
    start_id = 239
    for i, item in enumerate(raw):
        fixed = fix(item, start_id + len(valid))
        if validate(fixed):
            valid.append(fixed)
        else:
            print(f"  [跳过] {fixed.get('question','?')[:40]}", flush=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)

    print(f"\n有效题目: {len(valid)} 题", flush=True)
    print(f"输出: {OUTPUT_PATH}", flush=True)

    from collections import Counter
    kp = Counter(q['knowledge'] for q in valid)
    print(f"\n知识点:", flush=True)
    for k, c in kp.most_common():
        print(f"  {k}: {c}题", flush=True)

if __name__ == "__main__":
    main()
