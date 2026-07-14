#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
知识空战 - LLM 题目生成脚本
=============================
利用阿里云 Model Studio (deepseek-v4-flash) 大模型，
为三年级上册苏教版数学 + 人教版语文生成衍生题目，
严格遵循项目现有的 QuestionData 格式和验证规则。

使用方法：
  cd E:\知识空战项目
  python3 scripts/generate_questions.py
  输出：scripts/generated_questions.json（合并到 questions.json 的候选文件）
"""

import urllib.request
import json
import sys
import os
import re

# ================================================================
#  配置
# ================================================================

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "generated_questions.json")
EXISTING_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "questions.json")

# 已知的现有 ID 范围（用于校验不冲突）
EXISTING_IDS = set(range(1, 136))
NEXT_ID = 136

# ================================================================
#  API 调用
# ================================================================

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """调用 LLM API 并返回文本内容"""
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": 4096,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(data).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] API call failed: {e}", file=sys.stderr)
        return ""

# ================================================================
#  题目格式定义（QuestionData 接口的 Python 对应）
# ================================================================

"""
{
  "id": int,           // > 0, 从 136 开始
  "subject": "math_su" | "chinese",
  "type": "fill",
  "question": "string",    // 题目文本
  "answer": "string",      // 正确答案
  "options": ["str", ...], // 选项数组（含正确答案，共 3 个）
  "explain": "string",     // 解析
  "difficulty": int,       // 1-5
  "knowledge": "string"    // 知识点标签
}
"""

VALIDATION_RULES = """
验证规则：
1. answer 必须在 options 数组中
2. options 不能有重复
3. options 必须有 3 个选项
4. math_su 的除法必须能整除（结果为正整数）
5. 乘法因子不能为 0
6. 除法除数不能为 0
7. 选项必须各不相同
"""

# ================================================================
#  批次生成函数
# ================================================================

GENERATION_SYSTEM_PROMPT = """你是"知识空战"教育游戏的题目生成器。你的任务是生成符合以下严格规范的 JSON 题目数据。

## 输出格式
必须输出一个 JSON 数组，每个元素严格遵循以下结构：
```json
{
  "id": 0,
  "subject": "math_su",
  "type": "fill",
  "question": "计算题目",
  "answer": "正确答案",
  "options": ["正确答案", "干扰项1", "干扰项2"],
  "explain": "解题解析",
  "difficulty": 1,
  "knowledge": "知识点名称"
}
```

## 严格规范
1. answer 必须在 options 中，且只能出现一次
2. options 恰好 3 个，互不相同
3. 除法必须能整除（结果为正整数）
4. 乘法和除法的因子不能为 0
5. difficulty 取值 1（入门）到 5（挑战），与知识点难度匹配
6. 解析要易懂，面向三年级学生
7. 题目要符合三年级上册的教学内容
8. 每个生成的题目必须有合理的干扰项
9. 只输出 JSON 数组，不要包含任何其他文字说明"""

def generate_math_batch(knowledge: str, count: int, difficulties: list, start_id: int) -> list:
    """生成一批数学题"""
    diff_desc = {
        1: "入门级：一位数乘/除整十整百数，简单的表内乘除法",
        2: "简单级：需要进位的一次乘法，两位数的除法",
        3: "中等：多位数乘法，需要试商的除法",
        4: "较难：复杂的两步运算或实际应用题",
        5: "挑战级：综合应用题",
    }
    diff_str = "; ".join([f"level {d}: {diff_desc[d]}" for d in difficulties])

    user_prompt = f"""请生成 {count} 道关于"{knowledge}"的数学题目。

## 难度要求
{diff_str}

## 题目示例格式
{{
  "id": {start_id},
  "subject": "math_su",
  "type": "fill",
  "question": "计算：36×4 = ?",
  "answer": "144",
  "options": ["144", "124", "164"],
  "explain": "30×4=120，6×4=24，120+24=144。",
  "difficulty": 2,
  "knowledge": "{knowledge}"
}}

## 要求
- 先发式进位乘法（如 36×4, 128×3），难度 2-3
- 两三位数除以一位数首位不能整除（如 52÷4, 75÷6），难度 2-3
- 应用题要贴近三年级学生生活场景
- 生成严格 JSON 格式，不要包含 markdown 代码块标记
- id 从 {start_id} 开始依次递增

直接输出 JSON 数组，不需要其他说明文字。"""

    result_text = call_llm(GENERATION_SYSTEM_PROMPT, user_prompt)
    return parse_and_validate(result_text, start_id)


def generate_chinese_batch(poems: list, start_id: int) -> list:
    """生成一批语文古诗题"""
    poems_desc = []
    for p in poems:
        poems_desc.append(f"- 《{p['title']}》(作者：{p['author']})，全诗：{p['content']}")

    user_prompt = f"""请为以下古诗生成题目，每首诗分别生成 4 道题：
1. 补全诗句（给出上句填下句）×2
2. 作者识别
3. 字词释义（诗中的难词/关键字词含义）

古诗列表：
{chr(10).join(poems_desc)}

## 题目示例格式
{{
  "id": {start_id},
  "subject": "chinese",
  "type": "fill",
  "question": "《山行》"远上寒山石径斜"的下一句是？",
  "answer": "白云生处有人家",
  "options": ["白云生处有人家", "白云深处有人家", "江枫渔火对愁眠"],
  "explain": "全诗：远上寒山石径斜，白云生处有人家。停车坐爱枫林晚，霜叶红于二月花。",
  "difficulty": 1,
  "knowledge": "古诗-山行"
}}

## 要求
- 补全诗句类：必须是一句完整诗句，不能是拼凑的词组
- 干扰项：从其他古诗诗句中选取，不能是随意编造
- 字词释义：解释诗中关键字词的含义
- difficulty 1 级（补全诗句和作者）、2 级（字词释义和修辞理解）交错
- 直接输出 JSON 数组，id 从 {start_id} 开始递增
- 严格 JSON 格式，不要包含 markdown 代码块标记

直接输出 JSON 数组，不需要其他说明文字。"""

    result_text = call_llm(GENERATION_SYSTEM_PROMPT, user_prompt)
    return parse_and_validate(result_text, start_id)


def parse_and_validate(text: str, start_id: int) -> list:
    """从 LLM 返回文本中解析 JSON，做基础验证"""
    if not text:
        print("[WARN] Empty response from LLM", file=sys.stderr)
        return []

    # 尝试提取 JSON 数组
    text = text.strip()
    # 去掉可能的 markdown 代码块标记
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)

    try:
        questions = json.loads(text)
    except json.JSONDecodeError:
        # 尝试找到第一个 [ 和最后一个 ]
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            try:
                questions = json.loads(text[start:end+1])
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON parse failed: {e}", file=sys.stderr)
                print(f"[DEBUG] text snippet: {text[:500]}", file=sys.stderr)
                return []
        else:
            print("[ERROR] No JSON array found in response", file=sys.stderr)
            return []

    if not isinstance(questions, list):
        print("[ERROR] Response is not a JSON array", file=sys.stderr)
        return []

    # 验证和修复
    valid = []
    for i, q in enumerate(questions):
        q = fix_question(q, start_id + len(valid))
        if validate_question(q):
            valid.append(q)
        else:
            print(f"[WARN] Question #{start_id + i} failed validation: {q.get('question', '?')}", file=sys.stderr)

    print(f"[INFO] Batch: got {len(questions)}, valid {len(valid)}", file=sys.stderr)
    return valid


def fix_question(q: dict, new_id: int) -> dict:
    """修复/规范化题目数据"""
    q['id'] = new_id
    q['type'] = 'fill'

    # 确保 subject 正确
    if 'subject' not in q:
        q['subject'] = 'math_su'

    # 确保 options 有 3 项，包含 answer
    if 'options' in q and 'answer' in q:
        opts = list(dict.fromkeys([str(o).strip() for o in q['options']]))  # 去重保留顺序
        answer = str(q['answer']).strip()
        if answer not in opts:
            opts.insert(0, answer)
        if len(opts) < 3:
            # 填充足 3 个
            fillers = ['不知道', '不确定', '其他']
            for f in fillers:
                if f != answer and f not in opts:
                    opts.append(f)
                if len(opts) >= 3:
                    break
        q['options'] = opts[:3]
        q['answer'] = answer

    # 确保 difficulty 是 1-5
    if 'difficulty' in q:
        try:
            q['difficulty'] = int(q['difficulty'])
            q['difficulty'] = max(1, min(5, q['difficulty']))
        except (ValueError, TypeError):
            q['difficulty'] = 1
    else:
        q['difficulty'] = 1

    return q


def validate_question(q: dict) -> bool:
    """基础验证"""
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
    if not isinstance(q['question'], str) or len(q['question']) < 3:
        return False
    if not isinstance(q['explain'], str) or len(q['explain']) < 3:
        return False
    return True


# ================================================================
#  主逻辑
# ================================================================

def main():
    print("=" * 60)
    print("知识空战 - LLM 题目生成器")
    print("=" * 60)

    all_questions = []
    next_id = NEXT_ID

    # -----------------------------------------
    # 1. 数学题 - 每个知识点一批
    # -----------------------------------------
    math_batches = [
        # (knowledge, count, difficulties)
        ("两三位数乘一位数", 5, [2, 3]),
        ("两三位数除以一位数", 5, [2, 3]),
        ("千克和克", 3, [2]),
        ("长方形和正方形", 4, [2, 3]),
        ("分数的初步认识", 4, [2, 3]),
        ("综合应用", 4, [2]),
    ]

    print("\n>> 生成数学题目...")
    for knowledge, count, diffs in math_batches:
        print(f"  知识点: {knowledge} ({count}题, 难度{diffs})...", end=" ", flush=True)
        batch = generate_math_batch(knowledge, count, diffs, next_id)
        all_questions.extend(batch)
        next_id += len(batch)
        print(f"✓ 成功 {len(batch)}题")

    # -----------------------------------------
    # 2. 语文题 - 三年级上册古诗
    # -----------------------------------------
    poems = [
        {"title": "山行", "author": "杜牧",
         "content": "远上寒山石径斜，白云生处有人家。停车坐爱枫林晚，霜叶红于二月花。"},
        {"title": "赠刘景文", "author": "苏轼",
         "content": "荷尽已无擎雨盖，菊残犹有傲霜枝。一年好景君须记，最是橙黄橘绿时。"},
        {"title": "夜书所见", "author": "叶绍翁",
         "content": "萧萧梧叶送寒声，江上秋风动客情。知有儿童挑促织，夜深篱落一灯明。"},
        {"title": "望天门山", "author": "李白",
         "content": "天门中断楚江开，碧水东流至此回。两岸青山相对出，孤帆一片日边来。"},
        {"title": "饮湖上初晴后雨", "author": "苏轼",
         "content": "水光潋滟晴方好，山色空蒙雨亦奇。欲把西湖比西子，淡妆浓抹总相宜。"},
        {"title": "望洞庭", "author": "刘禹锡",
         "content": "湖光秋月两相和，潭面无风镜未磨。遥望洞庭山水翠，白银盘里一青螺。"},
    ]

    print("\n>> 生成语文古诗题目...")
    # 分两批生成，每批 3 首诗（12 题）
    for i in range(0, len(poems), 3):
        batch_poems = poems[i:i+3]
        print(f"  古诗: {[p['title'] for p in batch_poems]}...", end=" ", flush=True)
        batch = generate_chinese_batch(batch_poems, next_id)
        all_questions.extend(batch)
        next_id += len(batch)
        print(f"✓ 成功 {len(batch)}题")

    # -----------------------------------------
    # 3. 最终输出
    # -----------------------------------------
    print(f"\n{'=' * 60}")
    print(f"生成完成！总计 {len(all_questions)} 题")
    print(f"{'=' * 60}")

    # 写入文件
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print(f"输出文件: {OUTPUT_PATH}")
    print()

    # 输出统计
    math_count = len([q for q in all_questions if q['subject'] == 'math_su'])
    chinese_count = len([q for q in all_questions if q['subject'] == 'chinese'])
    print("学科分布：")
    print(f"  math_su: {math_count} 题")
    print(f"  chinese: {chinese_count} 题")
    print()
    print("难度分布：")
    from collections import Counter
    diff_counter = Counter(q['difficulty'] for q in all_questions)
    for d in sorted(diff_counter):
        print(f"  难度 {d}: {diff_counter[d]} 题")


if __name__ == "__main__":
    main()
