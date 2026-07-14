#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""调试：发送一个小型测试prompt，查看返回格式"""
import urllib.request, json

API_URL = "https://ws-144djw94kcgpfgdy.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-ws-H.EMRLLLR.S4WJ.MEUCIQCorM5hVKodL4hm8HyPFb5-f1z0ASTwPcWwed0qhF51xQIgcnnUxFvD8xt1IEJTe4cF3UkQYMsOqifF-avxzGtnVr4"
MODEL = "deepseek-v4-flash"

prompt = """生成3道chinese_g3科目选择题给三年级学生。
每道题JSON格式，放在JSON数组中。
要求：answer在options中，options共3个且不重复。

1. 《大青树下的小学》，问题：大青树下的学校里有哪些民族的学生？
答案：多个不同民族，干扰项：全是汉族、全是傣族
2. 词语"飘扬"的意思？答案：在空中飘动，干扰项：飘扬的意思、快速移动
3. 第一单元成语"摇头晃脑"形容什么？答案：自得其乐的样子，干扰项：头疼、困惑

直接输出JSON数组，不要任何其他文字。"""

data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "严格输出JSON数组。"},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.3,
    "max_tokens": 2000,
}
headers = {"Content-Type":"application/json","Authorization":f"Bearer {API_KEY}"}
req = urllib.request.Request(API_URL, data=json.dumps(data).encode(), headers=headers, method="POST")
with urllib.request.urlopen(req, timeout=60) as resp:
    r = json.loads(resp.read().decode())
    text = r["choices"][0]["message"]["content"]
    print("=== 返回内容 ===")
    print(text)
    print("=== 结束 ===")
    print(f"\n总字符: {len(text)}")
    
    # 尝试解析
    import re
    print("\n=== 尝试解析 ===")
    # 找JSON数组
    s = text.find('[')
    e = text.rfind(']')
    if s != -1 and e != -1:
        try:
            parsed = json.loads(text[s:e+1])
            print(f"直接解析: {len(parsed)} 个对象")
            for p in parsed:
                print(f"  {p.get('question','?')[:30]} -> {p.get('answer','?')}")
        except Exception as ex:
            print(f"直接解析失败: {ex}")
            # 试试去掉尾部逗号
            cleaned = re.sub(r',(\s*[\]}])', r'\1', text[s:e+1])
            try:
                parsed = json.loads(cleaned)
                print(f"修复后解析: {len(parsed)} 个对象")
            except Exception as ex2:
                print(f"修复后仍失败: {ex2}")
    else:
        print("未找到JSON数组")
