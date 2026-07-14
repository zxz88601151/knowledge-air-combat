#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
知识空战 - 语文非古诗题目生成（三年级上册）
覆盖：多音字、形近字、近反义词、量词、看拼音写词语、字义理解
"""
import urllib.request
import json
import sys
import os
import re

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "generated_chinese_words.json")
RAW_PATH = os.path.join(os.path.dirname(__file__), "chinese_words_raw.txt")

SYSTEM_PROMPT = """你是教育游戏题目生成专家。严格输出 JSON 数组，只输出 JSON，不要任何额外文字。"""

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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    req = urllib.request.Request(
        API_URL, data=json.dumps(data).encode(), headers=headers, method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = resp.read().decode()
        result = json.loads(raw)
        return result["choices"][0]["message"]["content"]

def parse_json(text: str) -> list:
    text = text.strip()
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?\s*```$', '', text)
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        candidate = re.sub(r',(\s*[\]}])', r'\1', candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
    # 逐个对象提取
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, text)
    objs = []
    for m in matches:
        try:
            obj = json.loads(m)
            if 'question' in obj and 'answer' in obj:
                objs.append(obj)
        except:
            pass
    if objs:
        return objs
    raise ValueError("无法解析 JSON")

def fix(q: dict, new_id: int) -> dict:
    q['id'] = new_id
    q['type'] = 'fill'
    if 'subject' not in q:
        q['subject'] = 'chinese'
    opts = list(dict.fromkeys([str(o).strip() for o in q.get('options', [])]))
    ans = str(q.get('answer', '')).strip()
    if ans not in opts:
        opts.insert(0, ans)
    while len(opts) < 3:
        opts.append('都不对')
    q['options'] = opts[:3]
    q['answer'] = ans
    try:
        q['difficulty'] = max(1, min(5, int(str(q.get('difficulty', 1)))))
    except:
        q['difficulty'] = 1
    if 'knowledge' not in q or not q['knowledge']:
        q['knowledge'] = '语文基础'
    return q

def validate(q: dict) -> bool:
    required = ['id', 'subject', 'type', 'question', 'answer', 'options', 'explain', 'difficulty', 'knowledge']
    for r in required:
        if r not in q:
            return False
    if q.get('type') != 'fill': return False
    if q['subject'] not in ('math_su', 'chinese'): return False
    if q['answer'] not in q['options']: return False
    if len(set(q['options'])) != len(q['options']): return False
    if len(q['options']) < 3: return False
    if len(q['question']) < 3: return False
    return True

# ================================================================
#  Prompt 构造
# ================================================================
def build_prompt(start_id: int) -> str:
    return f"""生成"知识空战"游戏的语文题目，面向三年级上册。输出严格 JSON 数组，每题格式：
{{"id":N,"subject":"chinese","type":"fill","question":"...","answer":"...","options":["...","...","..."],"explain":"...","difficulty":1,"knowledge":"..."}}

总共 50 题，id 从 {start_id} 开始递增。下面每题我列出了知识点、题目原文、正确答案、干扰项和解析。请按照这些内容严格生成 JSON。

## 第一部分：看拼音选词语（10题，难度1-2，knowledge="看拼音写词语"）

1. 知识点：看拼音写词语，题目：请选出"fēng shōu"对应的词语，答案：丰收，干扰项：分手、风收，解析："fēng shōu"对应"丰收"，表示收成好。难度1
2. 题目：请选出"wēn nuǎn"对应的词语，答案：温暖，干扰项：温软、温乱，解析："wēn nuǎn"对应"温暖"，意思是天气不冷不热。难度1
3. 题目：请选出"yǒng gǎn"对应的词语，答案：勇敢，干扰项：永远、用感，解析："yǒng gǎn"对应"勇敢"，指不怕困难和危险。难度1
4. 题目：请选出"zhǔn bèi"对应的词语，答案：准备，干扰项：准背、尊备，解析："zhǔn bèi"对应"准备"，意思是事先安排好。难度1
5. 题目：请选出"gǎn jī"对应的词语，答案：感激，干扰项：赶急、感机，解析："gǎn jī"对应"感激"，指因别人帮助而心生感谢。难度2
6. 题目：请选出"yǎn zòu"对应的词语，答案：演奏，干扰项：眼走、演奏，解析："yǎn zòu"对应"演奏"，指表演乐器。难度2
7. 题目：请选出"fēng yè"对应的词语，答案：枫叶，干扰项：风叶、丰夜，解析："fēng yè"对应"枫叶"，指枫树的叶子。难度1
8. 题目：请选出"pū mǎn"对应的词语，答案：铺满，干扰项：扑满、普满，解析："pū mǎn"对应"铺满"，意思是铺得很满。难度2
9. 题目：请选出"kě lián"对应的词语，答案：可怜，干扰项：可连、可恋，解析："kě lián"对应"可怜"，指值得同情。难度1
10. 题目：请选出"míng guì"对应的词语，答案：名贵，干扰项：明贵、名柜，解析："míng guì"对应"名贵"，指出名而珍贵。难度2

## 第二部分：量词搭配（10题，难度1-2，knowledge="量词搭配"）

11. 题目："一( )书"中括号里应填什么量词？答案：本，干扰项：张、台，解析："一(本)书"，书用"本"作量词。难度1
12. 题目："一( )马"中括号里应填什么量词？答案：匹，干扰项：头、条，解析："一(匹)马"，马用"匹"作量词。难度1
13. 题目："一( )诗"中括号里应填什么量词？答案：首，干扰项：篇、句，解析："一(首)诗"，诗用"首"作量词。难度1
14. 题目："一( )桥"中括号里应填什么量词？答案：座，干扰项：条、把，解析："一(座)桥"，桥用"座"作量词。难度1
15. 题目："一( )电脑"中括号里应填什么量词？答案：台，干扰项：个、部，解析："一(台)电脑"，电脑用"台"作量词。难度1
16. 题目："一( )画"中括号里应填什么量词？答案：幅，干扰项：张、片，解析："一(幅)画"，画用"幅"作量词。难度2
17. 题目："一( )笔"中括号里应填什么量词？答案：支，干扰项：条、根，解析："一(支)笔"，笔用"支"作量词。难度1
18. 题目："一( )棋"中括号里应填什么量词？答案：盘，干扰项：副、局，解析："一(盘)棋"，棋用"盘"作量词。难度2
19. 题目："一( )牛"中括号里应填什么量词？答案：头，干扰项：匹、条，解析："一(头)牛"，牛用"头"作量词。难度1
20. 题目："一( )被子"中括号里应填什么量词？答案：床，干扰项：条、张，解析："一(床)被子"，被子用"床"作量词。难度2

## 第三部分：近义词/反义词（10题，难度1-2，knowledge="近反义词"）

21. 题目：找出"美丽"的近义词，答案：漂亮，干扰项：难看、高大，解析："美丽"和"漂亮"意思相近，都是好看的意思。难度1
22. 题目：找出"开心"的近义词，答案：快乐，干扰项：伤心、生气，解析："开心"和"快乐"都表示心情愉快。难度1
23. 题目：找出"仔细"的近义词，答案：认真，干扰项：粗心、马虎，解析："仔细"和"认真"都表示做事用心。难度1
24. 题目：找出"温暖"的反义词，答案：寒冷，干扰项：炎热、凉爽，解析："温暖"的反义词是"寒冷"。难度1
25. 题目：找出"安静"的反义词，答案：热闹，干扰项：平静、寂寞，解析："安静"的反义词是"热闹"。难度1
26. 题目：找出"勇敢"的反义词，答案：胆小，干扰项：大胆、勇猛，解析："勇敢"的反义词是"胆小"。难度2
27. 题目：找出"渐渐"的近义词，答案：慢慢，干扰项：快快、突然，解析："渐渐"和"慢慢"都表示缓慢变化。难度2
28. 题目：找出"立刻"的近义词，答案：马上，干扰项：后来、很久，解析："立刻"和"马上"都表示很快。难度2
29. 题目：找出"成功"的反义词，答案：失败，干扰项：成就、胜利，解析："成功"的反义词是"失败"。难度2
30. 题目：找出"开始"的反义词，答案：结束，干扰项：起点、出发，解析："开始"的反义词是"结束"。难度1

## 第四部分：多音字辨析（10题，难度1-2，knowledge="多音字"）

31. 题目："假"字在"放假"中读什么？答案：jià，干扰项：jiǎ、jiā，解析："放假"的"假"读jià；jiǎ如"真假"。难度1
32. 题目："好"字在"爱好"中读什么？答案：hào，干扰项：hǎo、háo，解析："爱好"的"好"读hào；hǎo如"好人"。难度2
33. 题目："朝"字在"朝阳"中读什么？答案：zhāo，干扰项：cháo、zhào，解析："朝阳"的"朝"读zhāo，指早晨；cháo如"朝向"。难度2
34. 题目："发"字在"发现"中读什么？答案：fā，干扰项：fà、fá，解析："发现"的"发"读fā；fà如"头发"。难度1
35. 题目："当"字在"上当"中读什么？答案：dàng，干扰项：dāng、dǎng，解析："上当"的"当"读dàng；dāng如"当时"。难度2
36. 题目："乐"字在"音乐"中读什么？答案：yuè，干扰项：lè、luò，解析："音乐"的"乐"读yuè；lè如"快乐"。难度1
37. 题目："空"字在"有空"中读什么？答案：kòng，干扰项：kōng、kǒng，解析："有空"的"空"读kòng；kōng如"天空"。难度1
38. 题目："觉"字在"睡觉"中读什么？答案：jiào，干扰项：jué、jiǎo，解析："睡觉"的"觉"读jiào；jué如"觉得"。难度1
39. 题目："种"字在"种子"中读什么？答案：zhǒng，干扰项：zhòng、zhōng，解析："种子"的"种"读zhǒng；zhòng如"种地"。难度2
40. 题目："行"字在"银行"中读什么？答案：háng，干扰项：xíng、hǎng，解析："银行"的"行"读háng；xíng如"行走"。难度2

## 第五部分：形近字辨析（10题，难度1-2，knowledge="形近字"）

41. 题目：下列哪个字是"自己"的"己"？答案：己（不封口），干扰项：已（半封口）、巳（全封口），解析："己"自己，不封口；"已"已经，半封口；"巳"巳时，全封口。难度1
42. 题目："未"和"末"中，"未来"的"未"是？答案：上横短下横长，干扰项：上横长下横短、两横一样长，解析："未"未来，上横短下横长；"末"末尾相反。难度2
43. 题目："晴天"应该用哪个字？答案：晴（日字旁），干扰项：睛（目字旁）、情（竖心旁），解析："晴"日字旁，与太阳有关。难度1
44. 题目："分辨"应该用哪个字？答案：辨（中间是点撇），干扰项：辩（中间是言字旁）、辫（中间是绞丝旁），解析："辨"区分；"辩"争辩；"辫"辫子。难度2
45. 题目："折纸"的"折"怎么写？答案：扌+斤，干扰项：扌+斥、扌+拆，解析："折"提手旁加"斤"；"拆"是拆开的拆。难度2
46. 题目："拔河"的"拔"怎么写？答案：扌+友加点，干扰项：扌+友、扌+发，解析："拔"右边是"友"加一点；"拨"是"发"。难度2
47. 题目："蓝天下"应该用哪个"蓝"？答案：草字头蓝，干扰项：竹字头篮、单立人蓝，解析："蓝"草字头，指颜色；"篮"竹字头，指篮子。难度1
48. 题目："历史"的"历"怎么写？答案：厂+力，干扰项：厂+万、厂+立，解析："历"厂字头加"力"；"厉"是"厂"加"万"。难度2
49. 题目："飘落"的"飘"怎么写？答案：风字旁飘，干扰项：三点水漂、风字旁漂，解析："飘"风字旁，与风有关；"漂"三点水，与水有关。难度2
50. 题目："蜜蜂"的"蜜"怎么写？答案：宀+必+虫，干扰项：宀+必+山、宀+心+虫，解析："蜜"上面宝盖头，中间"必"，下面"虫"；"密"是山字底。难度2

## 第六部分：字义与词语理解（4题，难度2-3，knowledge="词语理解"）

51. 题目："骄傲"在"我们为祖国感到骄傲"中的意思是？答案：自豪，干扰项：自大、谦虚，解析：此处的"骄傲"是"自豪"的意思，是褒义词。难度2
52. 题目："意思"在"这朵花很有意思"中的含义是？答案：趣味，干扰项：含义、想法，解析："有意思"指有趣、有吸引力。难度2
53. 题目：形容非常生气的成语是？答案：暴跳如雷，干扰项：眉开眼笑、心平气和，解析："暴跳如雷"形容非常生气。难度3
54. 题目："闻名"的近义词是？答案：著名，干扰项：听闻、无名，解析："闻名"和"著名"都指名气很大。难度2

请严格按照上述内容生成 JSON 数组，id 从 {start_id} 到 {start_id + 53}（54题，含首尾共54题）。确保每个题目的 answer 在 options 中。每个选项恰好3个。"""

def main():
    start_id = 185
    print(">> 调用 LLM 生成语文非古诗题目...", flush=True)
    prompt = build_prompt(start_id)
    text = call_llm(prompt)
    print(f">> 返回 {len(text)} 字符", flush=True)

    raw_list = parse_json(text)
    print(f">> 解析到 {len(raw_list)} 条", flush=True)

    valid = []
    for i, item in enumerate(raw_list):
        fixed = fix(item, start_id + len(valid))
        if validate(fixed):
            valid.append(fixed)
        else:
            print(f"  [跳过] {fixed.get('question','?')[:40]}", flush=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}", flush=True)
    print(f"有效题目: {len(valid)} 题", flush=True)
    print(f"输出: {OUTPUT_PATH}", flush=True)

    from collections import Counter
    kp = Counter(q['knowledge'] for q in valid)
    print(f"\n知识点:", flush=True)
    for k, c in kp.most_common():
        print(f"  {k}: {c}题", flush=True)

if __name__ == "__main__":
    main()
