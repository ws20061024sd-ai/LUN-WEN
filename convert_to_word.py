#!/usr/bin/env python3
"""
将正文.md 转换为排版规范的 Word 文档。
格式遵循《美术观察》来稿体例要求。
"""

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

# ── 字体配置 ──
BODY_FONT_CN = "宋体"
BODY_FONT_EN = "Times New Roman"
HEADING_FONT_CN = "黑体"
HEADING_FONT_EN = "Times New Roman"
TITLE_FONT_CN = "黑体"
BODY_SIZE = Pt(12)         # 小四
HEADING_SIZE = Pt(14)      # 四号
TITLE_SIZE = Pt(18)        # 小二
NOTE_SIZE = Pt(9)          # 小五
ABSTRACT_SIZE = Pt(10.5)   # 五号

def set_font(run, cn_font, en_font, size, bold=False):
    """设置中西文字体"""
    run.font.size = size
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), cn_font)
    rFonts.set(qn('w:ascii'), en_font)
    rFonts.set(qn('w:hAnsi'), en_font)
    rPr.insert(0, rFonts)

def add_paragraph_with_format(doc, text, cn_font, en_font, size, bold=False,
                                alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                                first_line_indent=True, spacing=1.5):
    """添加格式化段落"""
    para = doc.add_paragraph()
    para.alignment = alignment
    pf = para.paragraph_format
    pf.line_spacing = spacing
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    if first_line_indent:
        pf.first_line_indent = Pt(24)  # 2 字符 ≈ 24pt at 12pt font
    run = para.add_run(text)
    set_font(run, cn_font, en_font, size, bold)
    return para

def add_heading_paragraph(doc, text, cn_font=None, en_font=None, size=None,
                          bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER):
    """添加标题段落（无缩进）"""
    if cn_font is None:
        cn_font = HEADING_FONT_CN
    if en_font is None:
        en_font = HEADING_FONT_EN
    if size is None:
        size = HEADING_SIZE
    return add_paragraph_with_format(doc, text, cn_font, en_font, size,
                                     bold=bold, alignment=alignment,
                                     first_line_indent=False, spacing=1.5)

def add_body(doc, text):
    """添加正文段落"""
    return add_paragraph_with_format(doc, text, BODY_FONT_CN, BODY_FONT_EN,
                                     BODY_SIZE, bold=False,
                                     alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                                     first_line_indent=True, spacing=1.5)

def add_note(doc, text):
    """添加注释条目"""
    return add_paragraph_with_format(doc, text, BODY_FONT_CN, BODY_FONT_EN,
                                     NOTE_SIZE, bold=False,
                                     alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                                     first_line_indent=False, spacing=1.15)

# ── 读取 Markdown ──
md_path = "/Users/xoln/Desktop/编程/论文/正文.md"
with open(md_path, "r") as f:
    lines = f.readlines()

# ── 创建 Document ──
doc = Document()

# 页面设置
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

# ── 解析 Markdown ──
i = 0
in_abstract = False
in_notes = False
in_body = False

while i < len(lines):
    line = lines[i].rstrip()

    # 跳过空行和分隔线
    if not line or line == "---":
        i += 1
        continue

    # 一级标题 #
    if line.startswith("# ") and not line.startswith("## "):
        title_text = line[2:].strip()
        add_heading_paragraph(doc, title_text, size=TITLE_SIZE)
        i += 1
        continue

    # 二级标题 ##
    if line.startswith("## "):
        heading_text = line[3:].strip()
        if heading_text == "摘要":
            in_abstract = True
            in_body = False
            add_heading_paragraph(doc, "摘要", alignment=WD_ALIGN_PARAGRAPH.CENTER)
        elif heading_text == "引言":
            in_abstract = False
            in_body = True
            add_heading_paragraph(doc, "引言", alignment=WD_ALIGN_PARAGRAPH.CENTER)
        elif heading_text == "注释":
            in_abstract = False
            in_body = False
            in_notes = True
            add_heading_paragraph(doc, "注释", alignment=WD_ALIGN_PARAGRAPH.CENTER)
        elif heading_text.startswith("一、") or heading_text.startswith("二、") or \
             heading_text.startswith("三、") or heading_text.startswith("四、") or \
             heading_text.startswith("五、") or heading_text.startswith("六、"):
            in_abstract = False
            in_body = True
            add_heading_paragraph(doc, heading_text, alignment=WD_ALIGN_PARAGRAPH.CENTER)
        else:
            # 其他二级标题（如有）
            in_abstract = False
            in_body = True
            add_heading_paragraph(doc, heading_text, alignment=WD_ALIGN_PARAGRAPH.CENTER)
        i += 1
        continue

    # 关键词行
    if line.startswith("**关键词**"):
        kw_text = line.replace("**关键词**：", "").replace("**", "").strip()
        add_paragraph_with_format(doc, f"关键词：{kw_text}",
                                  BODY_FONT_CN, BODY_FONT_EN, ABSTRACT_SIZE,
                                  bold=False, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                                  first_line_indent=False, spacing=1.5)
        i += 1
        continue

    # 正文 / 摘要 / 注释段落
    if in_notes:
        # 注释条目
        add_note(doc, line)
    elif in_abstract or in_body:
        # 去掉 Markdown 粗体标记和脚注标记
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        clean = re.sub(r'\^\((\d+)\)', r'(\1)', clean)
        if clean.strip():
            fs = ABSTRACT_SIZE if in_abstract else BODY_SIZE
            cn = BODY_FONT_CN
            en = BODY_FONT_EN
            if in_abstract:
                # 摘要可用楷体区分
                cn = "楷体"
            add_paragraph_with_format(doc, clean, cn, en, fs,
                                      bold=False,
                                      alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                                      first_line_indent=True,
                                      spacing=1.5)

    i += 1

# ── 添加页码（页脚居中） ──
for section in doc.sections:
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # 添加自动页码字段
    run = fp.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._element.append(fldChar1)
    run2 = fp.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = ' PAGE '
    run2._element.append(instrText)
    run3 = fp.add_run()
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run3._element.append(fldChar2)
    set_font(fp.runs[0], BODY_FONT_CN, BODY_FONT_EN, Pt(9))

# ── 保存 ──
output_path = "/Users/xoln/Desktop/编程/论文/正文.docx"
doc.save(output_path)
print(f"✅ Word 文档已生成: {output_path}")
print("   请在 Word 中打开，检查排版后导出为 PDF。")
