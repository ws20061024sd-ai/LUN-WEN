#!/usr/bin/env python3
"""
正文.md → HTML（学术期刊排版） → 浏览器打印为 PDF
"""

import re, os

MD = "/Users/xoln/Desktop/编程/论文/正文.md"
HTML_OUT = "/Users/xoln/Desktop/编程/论文/正文.html"

with open(MD, "r") as f:
    lines = f.readlines()

# ── CSS（学术期刊风格） ──
css = r"""
@page {
  size: A4;
  margin: 2.54cm 3.18cm 2.54cm 3.18cm;
}

@media print {
  body { -webkit-print-color-adjust: exact; }
  .page-break { page-break-before: always; }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: "Songti SC", "STSong", "SimSun", "宋体", serif;
  font-size: 12pt;
  line-height: 1.85;
  color: #111;
}

/* ====== 论文标题 ====== */
.title {
  font-family: "Heiti SC", "STHeiti", "SimHei", "黑体", sans-serif;
  font-size: 20pt;
  font-weight: 700;
  text-align: center;
  line-height: 1.4;
  margin: 0 0 0.5cm 0;
  letter-spacing: 0.5pt;
}
.author {
  font-size: 10.5pt;
  text-align: center;
  color: #555;
  margin: 0 0 1.0cm 0;
}

/* ====== 摘要 ====== */
.abstract-label {
  font-family: "Heiti SC", "STHeiti", "SimHei", "黑体", sans-serif;
  font-size: 14pt;
  font-weight: 700;
  text-align: center;
  margin: 0.35cm 0 0.3cm 0;
}
.abstract-text {
  font-family: "KaiTi SC", "STKaiti", "KaiTi", "楷体", serif;
  font-size: 11pt;
  line-height: 1.75;
  text-indent: 2em;
  text-align: justify;
  margin: 0 1.2em 0.1cm 1.2em;
  padding: 0;
}
.keywords {
  font-size: 11pt;
  margin: 0.3cm 1.2em 0 1.2em;
}
.keywords b {
  font-family: "Heiti SC", "STHeiti", "SimHei", sans-serif;
  font-weight: 700;
}

/* ====== 正文标题 ====== */
h2.section {
  font-family: "Heiti SC", "STHeiti", "SimHei", "黑体", sans-serif;
  font-size: 14pt;
  font-weight: 700;
  text-align: center;
  margin: 0.75cm 0 0.3cm 0;
  line-height: 1.5;
}

/* ====== 正文段落 ====== */
p.text {
  font-family: "Songti SC", "STSong", "SimSun", "宋体", serif;
  font-size: 12pt;
  line-height: 1.85;
  text-indent: 2em;
  text-align: justify;
  margin: 0.06cm 0;
}

/* ====== 上标引用 ====== */
sup { font-size: 0.7em; vertical-align: super; line-height: 0; }

/* ====== 注释 ====== */
.notes-sep {
  text-align: center;
  font-size: 9pt;
  color: #999;
  margin: 1cm 0 0.4cm 0;
  letter-spacing: 4pt;
}
.notes-title {
  font-family: "Heiti SC", "STHeiti", "SimHei", sans-serif;
  font-size: 14pt;
  font-weight: 700;
  text-align: center;
  margin: 0 0 0.35cm 0;
}
.note {
  font-size: 8.5pt;
  line-height: 1.6;
  text-align: justify;
  margin: 0.04cm 0;
  padding-left: 0.8em;
  text-indent: -0.8em;
}
"""

# ── 解析 Markdown → HTML ──
out = []
state = "pre"       # pre / abstract / intro / body / notes
abstract_lines = []
body_lines = []     # [(html, type)]
notes_lines = []
title_text = ""

for line in lines:
    s = line.rstrip()
    if not s or s == "---":
        continue

    # 主标题
    if s.startswith("# ") and not s.startswith("## "):
        title_text = s[2:].strip()
        continue

    # 二级标题
    if s.startswith("## "):
        h = s[3:].strip()
        if h == "摘要":
            state = "abstract"
            continue
        if h == "引言":
            state = "body"
            body_lines.append((f'<h2 class="section">引言</h2>', "html"))
            continue
        if h == "注释":
            state = "notes"
            continue
        if h.startswith("关键词"):
            continue
        # 一～六 正文标题
        if re.match(r'^[一二三四五六]、', h):
            state = "body"
            body_lines.append((f'<h2 class="section">{h}</h2>', "html"))
            continue
        state = "body"
        body_lines.append((f'<h2 class="section">{h}</h2>', "html"))
        continue

    # 关键词
    if s.startswith("**关键词**"):
        kw = s.replace("**关键词**：", "").replace("**", "").strip()
        abstract_lines.append(("kw", kw))
        continue

    # 正文 / 摘要 / 注释
    clean = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    clean = re.sub(r'\^\((\d+)\)', r'<sup>\1</sup>', clean)

    if state == "abstract":
        abstract_lines.append(("text", clean))
    elif state == "body":
        body_lines.append((f'<p class="text">{clean}</p>', "html"))
    elif state == "notes":
        notes_lines.append(clean)

# ── 组装 HTML ──
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

<!-- 摘要 -->
<div class="abstract-label">摘要</div>
"""

for typ, content in abstract_lines:
    if typ == "text":
        html += f'<div class="abstract-text">{content}</div>\n'
    elif typ == "kw":
        html += f'<div class="keywords"><b>关键词：</b>{content}</div>\n'

# 正文
for content, btype in body_lines:
    html += content + "\n"

# 注释
html += '<div class="notes-sep">— — — — — — — — — —</div>\n'
html += '<div class="notes-title">注释</div>\n'
for n in notes_lines:
    html += f'<div class="note">{n}</div>\n'

html += "\n</body>\n</html>"

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html)

# 同时输出绝对路径方便用户找
print(f"✅ HTML 已生成: {HTML_OUT}")
print(f"   文件路径: {os.path.abspath(HTML_OUT)}")
print()
print("→ 在浏览器中打开 → 文件 → 打印 → 另存为 PDF")
print("   (推荐 Chrome/Safari，边距选'无'，勾选'背景图形')")
