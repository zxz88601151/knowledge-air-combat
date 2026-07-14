#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
三年级上册独立模块 - 一站式合并与集成
1. 修复生成题目的OCR错字
2. 补充缺失题目
3. 合并到questions.json
4. 更新levels.json（+2关）
5. 更新GameScene.ts（+chinese_g3科目）
6. 更新ModeSelectScene.ts（+三年级卡片）
"""
import json, os, re

SCRIPT_DIR = os.path.dirname(__file__)
GEN_PATH = os.path.join(SCRIPT_DIR, "generated_g3.json")
EXISTING_PATH = os.path.join(SCRIPT_DIR, "..", "src", "data", "questions.json")
LEVELS_PATH = os.path.join(SCRIPT_DIR, "..", "src", "data", "levels.json")
GAMESCENE_PATH = os.path.join(SCRIPT_DIR, "..", "src", "game", "GameScene.ts")
MODESELECT_PATH = os.path.join(SCRIPT_DIR, "..", "src", "game", "ModeSelectScene.ts")

# ================================================================
#  1. 读取生成题目 + 修复错字
# ================================================================
with open(GEN_PATH, "r", encoding="utf-8") as f:
    gen = json.load(f)

FIXES = {
    "鸣蝍": "鸣蝉",
    "林梎": "林樾",
    "提心调胆": "提心吊胆",
}

for q in gen:
    for old, new in FIXES.items():
        if old in q['question']:
            print(f"  [修复] {old} -> {new}")
            q['question'] = q['question'].replace(old, new)
        if old in q['answer']:
            q['answer'] = q['answer'].replace(old, new)
        if old in q['explain']:
            q['explain'] = q['explain'].replace(old, new)
        q['options'] = [o.replace(old, new) for o in q['options']]

# ================================================================
#  2. 补充缺失题目（补足40题）
# ================================================================
next_id = max(q['id'] for q in gen) + 1

missing = [
    # 词语理解补充（3题）
    {
        "id": next_id, "subject": "chinese_g3", "type": "fill",
        "question": '"凌乱"的意思是？',
        "answer": "不整齐", "options": ["不整齐", "很整齐", "很凌冽"],
        "explain": '"凌乱"指杂乱、不整齐的样子。',
        "difficulty": 2, "knowledge": "三年级-词语理解"
    },
    {
        "id": next_id+1, "subject": "chinese_g3", "type": "fill",
        "question": '"五彩缤纷"形容什么？',
        "answer": "颜色很多很美丽", "options": ["颜色很多很美丽", "只有五种颜色", "五彩的颜色"],
        "explain": '"五彩缤纷"形容色彩繁多而美丽。',
        "difficulty": 2, "knowledge": "三年级-词语理解"
    },
    {
        "id": next_id+2, "subject": "chinese_g3", "type": "fill",
        "question": '"鸦雀无声"形容什么？',
        "answer": "非常安静", "options": ["非常安静", "声音很大", "乌鸦在叫"],
        "explain": '"鸦雀无声"形容非常安静，连乌鸦和麻雀的叫声都没有。',
        "difficulty": 2, "knowledge": "三年级-词语理解"
    },
    # 语文园地补充（4题）
    {
        "id": next_id+3, "subject": "chinese_g3", "type": "fill",
        "question": '"所"字的部首是什么？',
        "answer": "户", "options": ["户", "斤", "一"],
        "explain": '"所"字的部首是"户"（户字头）。',
        "difficulty": 2, "knowledge": "三年级-语文园地"
    },
    {
        "id": next_id+4, "subject": "chinese_g3", "type": "fill",
        "question": '写日记时，正文前一般要先写什么？',
        "answer": "日期和天气", "options": ["日期和天气", "只有日期", "标题和日期"],
        "explain": '日记一般在正文前先写日期和天气情况。',
        "difficulty": 1, "knowledge": "三年级-语文园地"
    },
    {
        "id": next_id+5, "subject": "chinese_g3", "type": "fill",
        "question": '口语交际中，借助什么可以帮助别人更好地理解你讲的内容？',
        "answer": "图片或实物", "options": ["图片或实物", "声音或动作", "文字或表情"],
        "explain": '借助图片或实物，可以让别人更直观地理解你讲的内容。',
        "difficulty": 1, "knowledge": "三年级-语文园地"
    },
    {
        "id": next_id+6, "subject": "chinese_g3", "type": "fill",
        "question": '在"猜猜他是谁"的习作中，不能出现什么？',
        "answer": "他的名字", "options": ["他的名字", "他的特点", "他的外貌"],
        "explain": '习作不能出现名字，要从特点描写让大家猜出是谁。',
        "difficulty": 1, "knowledge": "三年级-语文园地"
    },
]

gen.extend(missing)
print(f"\n补充后总题数: {len(gen)}")

# ================================================================
#  3. 合并到 questions.json
# ================================================================
with open(EXISTING_PATH, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_ids = set(q['id'] for q in existing)
gen = [q for q in gen if q['id'] not in existing_ids]

merged = existing + gen
merged.sort(key=lambda q: q['id'])

with open(EXISTING_PATH, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"题库合并: {len(existing)} + {len(gen)} = {len(merged)}")
g3_count = len([q for q in merged if q['subject'] == 'chinese_g3'])
print(f"  其中 chinese_g3 科目: {g3_count} 题")

# ================================================================
#  4. 更新 levels.json - 新增2关
# ================================================================
with open(LEVELS_PATH, "r", encoding="utf-8") as f:
    levels = json.load(f)

new_levels = []
if not any(l['id'] == 12 for l in levels):
    new_levels.append({
        "id": 12, "name": "古诗日积月累",
        "description": "鹿柴、所见——课文理解与古诗积累",
        "subject": "chinese_g3",
        "questionCount": 20,
        "enemySpeed": 28,
        "enemyCount": 3,
        "distractorCount": 2,
        "movePatterns": ["down"],
        "knowledgeFilter": ["三年级-古诗日积月累", "三年级-课文理解"],
        "difficultyRange": [1, 2],
        "typeFilter": ["fill"]
    })
if not any(l['id'] == 13 for l in levels):
    new_levels.append({
        "id": 13, "name": "成语字词大挑战",
        "description": "成语积累、多音字、词语理解、语文园地",
        "subject": "chinese_g3",
        "questionCount": 14,
        "enemySpeed": 32,
        "enemyCount": 3,
        "distractorCount": 2,
        "movePatterns": ["down"],
        "knowledgeFilter": ["三年级-成语积累", "三年级-多音字", "三年级-词语理解", "三年级-语文园地"],
        "difficultyRange": [1, 2],
        "typeFilter": ["fill"]
    })

levels.extend(new_levels)
with open(LEVELS_PATH, "w", encoding="utf-8") as f:
    json.dump(levels, f, ensure_ascii=False, indent=2)
print(f"Levels更新: {len(new_levels)} 关新增")

# ================================================================
#  5. 更新 GameScene.ts - SUBJECT_LEVELS + subject映射
# ================================================================
with open(GAMESCENE_PATH, "r", encoding="utf-8") as f:
    gs = f.read()

# 更新 SUBJECT_LEVELS 加入 chinese_g3
old_subject_levels = """const SUBJECT_LEVELS: Record<string, { start: number; end: number; label: string }> = {
  math:    { start: 1, end: 5, label: '数学' },
  chinese: { start: 6, end: 9, label: '语文' },
};"""

new_subject_levels = """const SUBJECT_LEVELS: Record<string, { start: number; end: number; label: string }> = {
  math:       { start: 1, end: 5, label: '数学' },
  chinese:    { start: 6, end: 11, label: '语文' },
  chinese_g3: { start: 12, end: 13, label: '三年级上学期' },
};"""

gs = gs.replace(old_subject_levels, new_subject_levels)

# 更新 saveGameSession 中的 subject 映射
gs = gs.replace(
    "const subject = this.selectedSubject === 'math' ? 'math_su' : 'chinese';",
    "const subject = this.selectedSubject === 'math' ? 'math_su' : this.selectedSubject === 'chinese_g3' ? 'chinese_g3' : 'chinese';"
)

# 更新 buildPerPlayerSession 中的 subject 映射  
gs = gs.replace(
    "subject: this.selectedSubject === 'math' ? 'math_su' : 'chinese',",
    "subject: this.selectedSubject === 'math' ? 'math_su' : this.selectedSubject === 'chinese_g3' ? 'chinese_g3' : 'chinese',"
)

with open(GAMESCENE_PATH, "w", encoding="utf-8") as f:
    f.write(gs)
print(f"GameScene.ts 已更新")

# ================================================================
#  6. 更新 ModeSelectScene.ts - 第三张卡片
# ================================================================
with open(MODESELECT_PATH, "r", encoding="utf-8") as f:
    ms = f.read()

# 检查是否已有三年级卡片
if 'chinese_g3' not in ms:
    # 在语文卡片后面插入三年级卡片
    old_card = """    // 语文卡片
    this.createCard(W / 2 + 130, 180, '📜', '语文', '三年级·人教版\\n122 道综合题', '#44aaff', () => {
      this.startGame('chinese');
    });"""

    new_cards = """    // 语文卡片
    this.createCard(W / 2 + 130, 180, '📜', '语文', '三年级·人教版\\n122 道综合题', '#44aaff', () => {
      this.startGame('chinese');
    });

    // 三年级上学期卡片
    this.createCard(W / 2, 390, '📖', '三年级上学期', '部编版语文\\n40 道课文与字词', '#ff8844', () => {
      this.startGame('chinese_g3');
    });"""

    ms = ms.replace(old_card, new_cards)

    # 更新底部提示
    ms = ms.replace(
        "按 1=数学  按 2=语文  按 R=返回首页",
        "按 1=数学  按 2=语文  按 3=三年级  按 R=返回首页"
    )

    # 增加按键3
    old_keys = """      const o = kb.addKey(Phaser.Input.Keyboard.KeyCodes.ONE);
      const t = kb.addKey(Phaser.Input.Keyboard.KeyCodes.TWO);
      const r = kb.addKey(Phaser.Input.Keyboard.KeyCodes.R);"""
    new_keys = """      const o = kb.addKey(Phaser.Input.Keyboard.KeyCodes.ONE);
      const t = kb.addKey(Phaser.Input.Keyboard.KeyCodes.TWO);
      const h = kb.addKey(Phaser.Input.Keyboard.KeyCodes.THREE);
      const r = kb.addKey(Phaser.Input.Keyboard.KeyCodes.R);"""
    ms = ms.replace(old_keys, new_keys)

    old_update = """        if (Phaser.Input.Keyboard.JustDown(o)) this.startGame('math');
        else if (Phaser.Input.Keyboard.JustDown(t)) this.startGame('chinese');
        else if (Phaser.Input.Keyboard.JustDown(r)) this.scene.start('HomeScene');"""
    new_update = """        if (Phaser.Input.Keyboard.JustDown(o)) this.startGame('math');
        else if (Phaser.Input.Keyboard.JustDown(t)) this.startGame('chinese');
        else if (Phaser.Input.Keyboard.JustDown(h)) this.startGame('chinese_g3');
        else if (Phaser.Input.Keyboard.JustDown(r)) this.scene.start('HomeScene');"""
    ms = ms.replace(old_update, new_update)

    with open(MODESELECT_PATH, "w", encoding="utf-8") as f:
        f.write(ms)
    print(f"ModeSelectScene.ts 已更新（含第三卡片）")
else:
    print(f"ModeSelectScene.ts 三年级卡片已存在，跳过")

print(f"\n{'='*50}")
print(f"三年级上册独立模块集成完成！")
print(f"总题数: {g3_count} 题")
print(f"关卡: Level 12 (古诗日积月累) + Level 13 (成语字词大挑战)")
print(f"{'='*50}")
