#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""调用LLM分析项目代码，获取专业修改建议"""
import urllib.request, json, os

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

# 读取项目快照
snapshot_path = "/tmp/project_snapshot.json"
with open(snapshot_path, "r", encoding="utf-8") as f:
    snapshot = json.load(f)

project_overview = f"""
# 知识空战项目概况

## 技术栈
- 游戏引擎: Phaser 3 (v3.80.1)
- 语言: TypeScript (v5.4)
- 构建: Vite (v5.2)
- UI: HTML/CSS 混合架构 (Phaser Canvas + HTML浮层)
- 数据: localStorage 持久化
- AI: 阿里云 Model Studio (deepseek-v4-flash / qwen3.7-max)

## 核心架构
- 10个Phaser场景 + 1个HTML浮层
- 题目引擎: 支持静态题库 + 动态变异 + 掌握度追踪
- 玩家系统: 双人独立数据(P1/P2)、飞机等级、XP、维修站

## 关键文件内容摘要
"""

# 读取关键文件的全量内容
key_files = {}
for name in ['GameScene.ts', 'PlayerData.ts', 'index.html', 'main.ts', 'types.ts']:
    # 重新读取完整文件
    path_map = {
        'GameScene.ts': 'src/game/GameScene.ts',
        'PlayerData.ts': 'src/systems/PlayerData.ts',
        'index.html': 'index.html',
        'main.ts': 'src/main.ts',
        'types.ts': 'src/types.ts',
    }
    full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), path_map[name])
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            key_files[name] = f.read()

user_prompt = f"""你是一位资深游戏架构师和技术顾问，专精于Phaser游戏引擎、教育游戏设计和TypeScript全栈开发。

请分析"知识空战"教育游戏项目的代码，从以下7个维度给出**具体的、可执行的修改建议**和**头脑风暴**：

{project_overview}

## 关键代码

### GameScene.ts (核心游戏逻辑 - 约1000行)
```typescript
{key_files['GameScene.ts'][:5000]}
...
```

### PlayerData.ts (数据持久化 - 约400行)
```typescript
{key_files['PlayerData.ts'][:4000]}
...
```

### index.html (首页/浮层 - 约350行)
```html
{key_files['index.html'][:4000]}
...
```

### main.ts (游戏入口)
```typescript
{key_files['main.ts']}
```

### types.ts (类型定义)
```typescript
{key_files['types.ts'][:2000]}
```

---

## 请从以下7个维度分析并给出建议

### 1. 架构设计
- 目录结构和模块划分是否有优化空间？
- HTML浮层 + Phaser Canvas 混合架构的优缺点？
- 是否有更好的状态管理方案？

### 2. 代码质量
- 可读性、可维护性评分
- 存在哪些代码异味(code smells)？
- 是否有冗余代码可以删除？

### 3. 性能优化
- Phaser画布性能瓶颈可能在哪？
- localStorage大量读写是否影响性能？
- 星空背景动画是否有性能开销？

### 4. 游戏体验
- 从教育游戏角度，有哪些UX改进点？
- 新手引导缺失了什么？
- 游戏循环(玩→错→修→升级)是否有断裂？

### 5. 数据安全与合规
- localStorage 存储敏感数据是否有风险？
- 多玩家数据是否完全隔离？
- 数据清空/重置机制是否完善？

### 6. 扩展性
- 新增一个年级/学科的代码改动量？
- 从单机→联机的架构改造路径？
- 接入后端API的最佳方式？

### 7. 创新头脑风暴
- 最值得投入的3个创新功能
- 现有LLM API(300万tokens)的最佳利用方式
- 游戏化教育产品的差异化方向

请直接输出分析报告，结构化呈现每个维度的发现、风险等级(🔴高/🟡中/🟢低)和具体建议。"""

data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是一位资深游戏架构师，专精Phaser游戏开发。输出专业、结构化、可执行的代码审查报告。"},
        {"role": "user", "content": user_prompt},
    ],
    "temperature": 0.3,
    "max_tokens": 8192,
}

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

print(">> 调用 LLM 分析项目代码...", flush=True)
req = urllib.request.Request(API_URL, data=json.dumps(data).encode(), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read().decode())
        report = result["choices"][0]["message"]["content"]
        print(report)
        # 保存报告
        report_path = os.path.join(os.path.dirname(__file__), "code_review_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n\n报告已保存: {report_path}")
except Exception as e:
    print(f"错误: {e}", flush=True)
