#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
知识空战 - 一次调用生成全部题目（修复版）
增加更健壮的 JSON 解析和修复
"""
import urllib.request
import json
import sys
import os
import re

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "generated_questions.json")
RAW_PATH = os.path.join(os.path.dirname(__file__), "llm_raw_response.txt")

SYSTEM_PROMPT = """你是"知识空战"教育游戏的题目生成专家。严格输出 JSON 数组，不要包含任何额外说明文字。"""

USER_PROMPT = """生成"知识空战"教育游戏的题目，面向三年级学生。

## JSON 格式（严格）
每个题目对象格式如下：
{
  "id": 136,
  "subject": "math_su",
  "type": "fill",
  "question": "题目文字",
  "answer": "正确答案",
  "options": ["正确答案", "干扰项1", "干扰项2"],
  "explain": "解题解析",
  "difficulty": 2,
  "knowledge": "知识点名"
}

## 约束
- answer 必须在 options 中，options 恰好3个且互不重复
- 除法必须能整除
- difficulty 1-5
- 只输出 JSON 数组，不要任何其他文字

## 数学题（25道，id 136-160）

### 两三位数乘一位数（5道，进位乘法，难度2-3）
包括：36×4, 128×3, 24×6, 47×2, 18×5
应用题变式如："每箱牛奶24瓶，3箱共多少瓶？"
解析要分步：先算十位再算个位再相加

### 两三位数除以一位数（5道，首位不能整除，难度2-3）
包括：52÷4, 75÷5, 96÷8, 84÷6, 91÷7
必须能整除。解析：拆成整十部分+个位部分

### 千克和克（3道，应用，难度2）
如："妈妈买了2千克苹果和500克葡萄，共（ ）克"
"5千克-3000克=（ ）千克"
"一袋米重25千克，2袋米共重（ ）千克"

### 长方形和正方形（4道，逆向/变式，难度2-3）
如："正方形周长36厘米，边长（ ）厘米"
"长方形长12厘米，宽比长少4厘米，周长（ ）厘米"
"用一根80厘米铁丝围正方形，边长（ ）厘米"
"长10厘米宽6厘米的长方形，周长（ ）厘米"

### 分数的初步认识（4道，比较/加减，难度2-3）
如："3/8（ ）5/8"答案"小于"
"2/6+3/6=（ ）"答案"5/6"
"1-3/7=（ ）"答案"4/7"
"把蛋糕平均分8份，吃3份剩（ ）"答案"5/8"

### 综合应用（4道，两步计算，难度2）
如："3盒铅笔每盒12支，卖出18支，还剩（ ）支"答案"18"
"84页书每天看6页，（ ）天看完"答案"14"
"每排8棵树共6排，又种了12棵，共（ ）棵"答案"60"
"50元买书花28元，买笔花15元，还剩（ ）元"答案"7"

## 语文题（24道，id 161-184，每首诗4道）
每首诗：2道补全诗句 + 1道作者识别 + 1道字词/修辞

### 1.《山行》杜牧
全诗：远上寒山石径斜，白云生处有人家。停车坐爱枫林晚，霜叶红于二月花。
补全："远上寒山石径斜"→"白云生处有人家"
补全："停车坐爱枫林晚"→"霜叶红于二月花"
作者：杜牧
"坐"的意思是"因为"

### 2.《赠刘景文》苏轼
全诗：荷尽已无擎雨盖，菊残犹有傲霜枝。一年好景君须记，最是橙黄橘绿时。
补全："荷尽已无擎雨盖"→"菊残犹有傲霜枝"
补全："一年好景君须记"→"最是橙黄橘绿时"
作者：苏轼
"擎雨盖"指"荷叶"

### 3.《夜书所见》叶绍翁
全诗：萧萧梧叶送寒声，江上秋风动客情。知有儿童挑促织，夜深篱落一灯明。
补全："萧萧梧叶送寒声"→"江上秋风动客情"
补全："知有儿童挑促织"→"夜深篱落一灯明"
作者：叶绍翁
"挑促织"指"捉蟋蟀"；这首诗表达"思乡之情"

### 4.《望天门山》李白
全诗：天门中断楚江开，碧水东流至此回。两岸青山相对出，孤帆一片日边来。
补全："天门中断楚江开"→"碧水东流至此回"
补全："两岸青山相对出"→"孤帆一片日边来"
作者：李白
"中断"意思是"从中间断开"

### 5.《饮湖上初晴后雨》苏轼
全诗：水光潋滟晴方好，山色空蒙雨亦奇。欲把西湖比西子，淡妆浓抹总相宜。
补全："水光潋滟晴方好"→"山色空蒙雨亦奇"
补全："欲把西湖比西子"→"淡妆浓抹总相宜"
作者：苏轼
"西子"指"西施"，用了"比喻"修辞

### 6.《望洞庭》刘禹锡
全诗：湖光秋月两相和，潭面无风镜未磨。遥望洞庭山水翠，白银盘里一青螺。
补全："湖光秋月两相和"→"潭面无风镜未磨"
补全："遥望洞庭山水翠"→"白银盘里一青螺"
作者：刘禹锡
"镜未磨"形容"湖面平静"，用了"比喻"修辞

## 干扰项要求
补全诗句的干扰项从其他古诗诗句中选取（不能编造）
字词释义的干扰项是真实存在的误导选项
数学干扰项是常见的计算错误结果

直接输出 JSON 数组。"""

def call_llm() -> str:
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.strip()},
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

def extract_json_objects(text: str) -> list:
    """尝试多种方式提取 JSON"""
    text = text.strip()
    # 存原始响应
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    
    # 1) 去掉 markdown 代码块
    text = re.sub(r'^```(?:json)?\s*\n', '', text)
    text = re.sub(r'\n\s*```$', '', text)
    text = re.sub(r'```', '', text)
    
    # 2) 找 [ 和 ]
    start = text.find('[')
    end = text.rfind(']')
    if start != -1 and end != -1:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass
        
        # 3) 逐行修复 - 去掉注释、末尾逗号等
        lines = candidate.split('\n')
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('#'):
                continue
            cleaned.append(line)
        candidate2 = '\n'.join(cleaned)
        # 去掉对象最后一个属性后的逗号
        candidate2 = re.sub(r',(\s*[}\]])', r'\1', candidate2)
        try:
            return json.loads(candidate2)
        except json.JSONDecodeError:
            pass
    
    # 4) 最后一个办法：逐对象提取
    print("[DEBUG] 尝试逐行解析...", file=sys.stderr)
    objs = []
    # 用正则找每个 {} 对象
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, text)
    for m in matches:
        try:
            obj = json.loads(m)
            if 'question' in obj and 'answer' in obj:
                objs.append(obj)
        except:
            pass
    if objs:
        return objs
    
    raise ValueError(f"无法解析 JSON。原始响应已保存到 {RAW_PATH}")

def validate(q: dict) -> bool:
    required = ['id', 'subject', 'type', 'question', 'answer', 'options', 'explain', 'difficulty', 'knowledge']
    for r in required:
        if r not in q:
            return False
    if q.get('type') != 'fill':
        return False
    if q['subject'] not in ('math_su', 'chinese'):
        return False
    if q['answer'] not in q['options']:
        return False
    if len(set(q['options'])) != len(q['options']):
        return False
    if len(q['options']) < 3:
        return False
    return True

def fix(q: dict, new_id: int) -> dict:
    q['id'] = new_id
    q['type'] = 'fill'
    if 'subject' not in q:
        q['subject'] = 'math_su'
    opts = list(dict.fromkeys([str(o).strip() for o in q.get('options', [])]))
    ans = str(q.get('answer', '')).strip()
    if ans not in opts:
        opts.insert(0, ans)
    while len(opts) < 3:
        opts.append('其他')
    q['options'] = opts[:3]
    q['answer'] = ans
    if 'difficulty' in q:
        try:
            q['difficulty'] = max(1, min(5, int(str(q['difficulty']))))
        except:
            q['difficulty'] = 1
    else:
        q['difficulty'] = 1
    return q

def main():
    print(">> 调用 LLM...", flush=True)
    raw_text = call_llm()
    print(f">> 返回 {len(raw_text)} 字符", flush=True)
    
    raw_list = extract_json_objects(raw_text)
    print(f">> 解析到 {len(raw_list)} 条", flush=True)
    
    valid = []
    for i, item in enumerate(raw_list):
        fixed_item = fix(item, 136 + len(valid))
        if validate(fixed_item):
            valid.append(fixed_item)
        else:
            print(f"  [跳过] {fixed_item.get('question','?')[:40]}", flush=True)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}", flush=True)
    print(f"有效题目: {len(valid)} 题", flush=True)
    print(f"输出: {OUTPUT_PATH}", flush=True)
    
    math_c = len([q for q in valid if q['subject'] == 'math_su'])
    chn_c = len([q for q in valid if q['subject'] == 'chinese'])
    print(f"  数学: {math_c} 题", flush=True)
    print(f"  语文: {chn_c} 题", flush=True)
    
    from collections import Counter
    kp = Counter(q['knowledge'] for q in valid)
    print(f"\n知识点:", flush=True)
    for k, c in kp.most_common():
        print(f"  {k}: {c}题", flush=True)

if __name__ == "__main__":
    main()
