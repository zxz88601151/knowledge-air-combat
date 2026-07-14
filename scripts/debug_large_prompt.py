#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""调试：用批量脚本中的第一个大prompt测试"""
import urllib.request, json, re

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

# Use the exact same format as the working small test
prompt = """生成chinese_g3科目选择题给三年级学生，部编版三年级上册第一单元。

覆盖课文：
1. 大青树下的小学：课文理解、生字、词语
2. 花的学校：课文理解、作者泰戈尔、修辞
3. 不懂就要问：孙中山故事、多音字
4. 语文园地一：成语、日积月累《所见》、词句段运用
5. 口语交际、习作

每道题JSON格式，放在JSON数组中。
要求：每个对象必须有id,subject,type,question,answer,options,explain,difficulty,knowledge
id从279开始递增。answer必须在options中，options共3个且不重复。
knowledge前缀为"三年级-课文-课名"。

总计至少30题。

示例格式：
{"id":279,"subject":"chinese_g3","type":"fill","question":"《大青树下的小学》中同学们来自哪里？","answer":"从山坡上、坪坝里和小路上","options":["从山坡上、坪坝里和小路上","从附近的村庄里","从城里和镇上"],"explain":"课文开头说：早晨，从山坡上...","difficulty":1,"knowledge":"三年级-课文-大青树下的小学"}

直接输出JSON数组，不要任何其他文字。"""

data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "严格输出JSON数组，不要任何其他文字。"},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.3,
    "max_tokens": 8192,
}
headers = {"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}
req = urllib.request.Request(API_URL, data=json.dumps(data).encode(), headers=headers, method="POST")
with urllib.request.urlopen(req, timeout=180) as resp:
    r = json.loads(resp.read().decode())
    text = r["choices"][0]["message"]["content"]
    
    # 保存原始响应
    with open("scripts/debug_raw.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"返回 {len(text)} 字符")
    print(f"前200字符: {text[:200]}")
    print(f"后200字符: {text[-200:]}")
    
    # 尝试各种解析方法
    text2 = text.strip()
    text2 = re.sub(r'^```(?:json)?\s*\n?', '', text2)
    text2 = re.sub(r'\n?\s*```$', '', text2)
    
    print(f"\n清理后首字符: '{text2[0] if text2 else '空'}'")
    
    s = text2.find('[')
    e = text2.rfind(']')
    print(f"[位置: {s}, ]位置: {e}")
    
    if s != -1 and e != -1:
        c = text2[s:e+1]
        try:
            parsed = json.loads(c)
            print(f"✅ 直接解析成功: {len(parsed)} 个对象")
            for p in parsed[:3]:
                print(f"  [{p.get('knowledge','?')}] {p.get('question','?')[:30]} -> {p.get('answer','?')}")
        except Exception as ex:
            print(f"❌ 直接解析失败: {ex}")
            # 修复尾逗号
            c2 = re.sub(r',(\s*[\]}])', r'\1', c)
            try:
                parsed = json.loads(c2)
                print(f"✅ 修复后解析成功: {len(parsed)} 个对象")
            except Exception as ex2:
                print(f"❌ 修复后也失败: {ex2}")
                print(f"\nJSON片段(前500): {c[:500]}")
    else:
        print("❌ 未找到JSON数组边界")
