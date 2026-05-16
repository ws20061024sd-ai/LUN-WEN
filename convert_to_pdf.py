#!/usr/bin/env python3
"""
正文.md → HTML（学术期刊排版） → 浏览器打印为 PDF

排版原则：
- 强左对齐轴线：仅主标题居中，其余全部左对齐
- 摘要用内联标签 "摘要：" 而非居中标题
- 正文两端对齐，段首缩进 2 字
- 行距 1.75，字号层级分明
"""

import re, os

MD = "/Users/xoln/Desktop/编程/论文/正文.md"
HTML_OUT = "/Users/xoln/Desktop/编程/论文/正文.html"

with open(MD, "r") as f:
    lines = f.readlines()

css = r"""
@page {
  size: A4;
  margin: 2.54cm 3.18cm 3.0cm 3.18cm;
  @bottom-center {
    content: counter(page);
    font-family: "Times New Roman", serif;
    font-size: 9pt;
    color: #333;
  }
}

@media print {
  body { -webkit-print-color-adjust: exact; }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: "Songti SC", "STSong", "SimSun", "宋体", serif;
  font-size: 12pt;          /* 小四 */
  line-height: 1.75;
  color: #1a1a1a;
  text-align: justify;
}

/* ====== 论文标题（唯一居中） ====== */
.title {
  font-family: "Heiti SC", "STHeiti", "SimHei", "黑体", sans-serif;
  font-size: 20pt;
  font-weight: 700;
  text-align: center;
  line-height: 1.4;
  margin-bottom: 0.5cm;
}
.author {
  font-size: 10.5pt;
  text-align: center;
  color: #666;
  margin-bottom: 1.0cm;
}

/* ====== 摘要（内联标签，左右缩进 1em） ====== */
.abstract-block {
  margin: 0.2cm 0 0.15cm 0;
}
.abstract-block p {
  font-family: "KaiTi SC", "STKaiti", "KaiTi", "楷体", serif;
  font-size: 11pt;
  line-height: 1.75;
  text-indent: 2em;
  text-align: justify;
  margin: 0.08cm 1.2em;
}
.abstract-block .label {
  font-family: "Heiti SC", "STHeiti", "SimHei", sans-serif;
  font-size: 11pt;
  font-weight: 700;
}
.keywords-block {
  font-size: 11pt;
  margin: 0.2cm 1.2em 0.35cm 1.2em;
}
.keywords-block .label {
  font-family: "Heiti SC", "STHeiti", "SimHei", sans-serif;
  font-weight: 700;
}

/* ====== 正文标题（左对齐） ====== */
h2.section {
  font-family: "Heiti SC", "STHeiti", "SimHei", "黑体", sans-serif;
  font-size: 14pt;
  font-weight: 700;
  text-align: left;
  line-height: 1.5;
  margin: 0.65cm 0 0.22cm 0;
  padding-left: 0;
}

/* ====== 正文段落（两端对齐，缩进 2 字） ====== */
p.text {
  font-family: "Songti SC", "STSong", "SimSun", "宋体", serif;
  font-size: 12pt;
  line-height: 1.75;
  text-indent: 2em;
  text-align: justify;
  margin: 0.06cm 0;
}

sup { font-size: 0.7em; vertical-align: super; line-height: 0; }

/* ====== 注释 ====== */
.notes-sep {
  text-align: center;
  font-size: 9pt;
  color: #bbb;
  margin: 0.9cm 0 0.3cm 0;
  letter-spacing: 3pt;
}
.notes-title {
  font-family: "Heiti SC", "STHeiti", "SimHei", sans-serif;
  font-size: 14pt;
  font-weight: 700;
  text-align: left;
  margin: 0 0 0.3cm 0;
}
.note {
  font-size: 8.5pt;
  line-height: 1.55;
  text-align: justify;
  margin: 0.04cm 0;
}
"""

# ── 解析 ──
state = "pre"
abstract_paras = []
keywords = ""
body_html = []
notes_lines = []
title_text = ""

for line in lines:
    s = line.rstrip()
    if not s or s == "---":
        continue

    if s.startswith("# ") and not s.startswith("## "):
        title_text = s[2:].strip()
        continue

    if s.startswith("## "):
        h = s[3:].strip()
        if h == "摘要":
            state = "abstract"
            continue
        if h == "引言":
            state = "body"
            body_html.append('<h2 class="section">引言</h2>')
            continue
        if h == "注释":
            state = "notes"
            continue
        # 一～六 正文标题
        if re.match(r'^[一二三四五六]、', h):
            state = "body"
            body_html.append(f'<h2 class="section">{h}</h2>')
            continue
        state = "body"
        body_html.append(f'<h2 class="section">{h}</h2>')
        continue

    # 关键词
    if s.startswith("**关键词**"):
        keywords = s.replace("**关键词**：", "").replace("**", "").strip()
        continue

    # 内容
    clean = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    clean = re.sub(r'\^\((\d+)\)', r'<sup>\1</sup>', clean)

    if state == "abstract":
        abstract_paras.append(clean)
    elif state == "body":
        body_html.append(f'<p class="text">{clean}</p>')
    elif state == "notes":
        notes_lines.append(clean)

# ── 组装 ──
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title_text}</title>
<style>{css}</style>
</head>
<body>

<div class="title">{title_text}</div>
<div class="author">作者姓名（单位，城市 邮编）</div>

<!-- 摘要（内联标签） -->
<div class="abstract-block">
"""

# 摘要第一段加 "摘要：" 标签
if abstract_paras:
    html += f'<p><span class="label">摘要：</span>{abstract_paras[0]}</p>\n'
    for p in abstract_paras[1:]:
        html += f'<p>{p}</p>\n'

html += '</div>\n'

if keywords:
    html += f'<div class="keywords-block"><span class="label">关键词：</span>{keywords}</div>\n'

html += '\n'.join(body_html) + '\n'

# 注释
html += '<div class="notes-sep">— — — — — — — — — —</div>\n'
html += '<div class="notes-title">注释</div>\n'
for n in notes_lines:
    html += f'<div class="note">{n}</div>\n'

html += "\n</body>\n</html>"

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ HTML 已生成: {HTML_OUT}")
print(f"   路径: {os.path.abspath(HTML_OUT)}")
print("→ 浏览器打开 → Cmd+P → 另存为 PDF")
