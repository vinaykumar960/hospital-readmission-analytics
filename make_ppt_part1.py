import sys
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

COLOR_TOP_BAR = RGBColor(194, 65, 12)
COLOR_ACCENT = RGBColor(234, 88, 12)
COLOR_TITLE = RGBColor(15, 23, 42)
COLOR_SUBTITLE = RGBColor(71, 85, 105)
COLOR_BODY = RGBColor(51, 65, 85)
COLOR_MUTED = RGBColor(100, 116, 139)
COLOR_CARD_BG = RGBColor(248, 250, 252)
COLOR_CARD_BORDER = RGBColor(226, 232, 240)
COLOR_WHITE = RGBColor(255, 255, 255)

cmrit_logo_path = Path('presentation_assets/cmrit_logo.png')
dashboard_img_path = Path('presentation_assets/dashboard_screenshot.png')
blank_layout = prs.slide_layouts[6]

def add_template_background(slide, slide_num, title_text):
    top_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
    top_strip.fill.solid()
    top_strip.fill.fore_color.rgb = COLOR_TOP_BAR
    top_strip.line.fill.background()

    if slide_num == 1:
        left_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.25), Inches(7.5))
        left_strip.fill.solid()
        left_strip.fill.fore_color.rgb = COLOR_TOP_BAR
        left_strip.line.fill.background()
        return

    tb_hdr = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(8.5), Inches(0.4))
    p_hdr = tb_hdr.text_frame.paragraphs[0]
    p_hdr.text = 'CMR INSTITUTE OF TECHNOLOGY | DATA ENGINEERING AND MLOps'
    p_hdr.font.size = Pt(11)
    p_hdr.font.bold = True
    p_hdr.font.color.rgb = RGBColor(15, 23, 42)

    tb_hdr_r = slide.shapes.add_textbox(Inches(9.5), Inches(0.35), Inches(3.2), Inches(0.4))
    p_hdr_r = tb_hdr_r.text_frame.paragraphs[0]
    p_hdr_r.text = 'PROJECT PRESENTATION'
    p_hdr_r.font.size = Pt(11)
    p_hdr_r.font.bold = True
    p_hdr_r.font.color.rgb = COLOR_MUTED
    p_hdr_r.alignment = PP_ALIGN.RIGHT

    tb_title = slide.shapes.add_textbox(Inches(0.6), Inches(0.75), Inches(12), Inches(0.7))
    p_title = tb_title.text_frame.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TITLE

    underline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), Inches(1.42), Inches(1.5), Inches(0.06))
    underline.fill.solid()
    underline.fill.fore_color.rgb = COLOR_ACCENT
    underline.line.fill.background()

    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.6), Inches(12.133), Inches(5.2))
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_CARD_BG
    card.line.color.rgb = COLOR_CARD_BORDER
    card.line.width = Pt(1.5)

    tb_ft = slide.shapes.add_textbox(Inches(0.6), Inches(6.9), Inches(8.0), Inches(0.4))
    p_ft = tb_ft.text_frame.paragraphs[0]
    p_ft.text = 'Student Name: Vinay Kumar H R    |    USN: 1CR23AI139'
    p_ft.font.size = Pt(10)
    p_ft.font.color.rgb = COLOR_MUTED

    tb_ft_r = slide.shapes.add_textbox(Inches(9.5), Inches(6.9), Inches(3.2), Inches(0.4))
    p_ft_r = tb_ft_r.text_frame.paragraphs[0]
    p_ft_r.text = f'CMRIT    {slide_num}'
    p_ft_r.font.size = Pt(10)
    p_ft_r.font.bold = True
    p_ft_r.font.color.rgb = RGBColor(194, 65, 12)
    p_ft_r.alignment = PP_ALIGN.RIGHT

def add_two_column_content(slide, left_title, left_bullets, right_title, right_bullets):
    box_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.7))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = COLOR_WHITE
    box_l.line.color.rgb = COLOR_CARD_BORDER
    
    tb_lt = slide.shapes.add_textbox(Inches(1.1), Inches(1.95), Inches(5.2), Inches(0.4))
    p_lt = tb_lt.text_frame.paragraphs[0]
    p_lt.text = left_title
    p_lt.font.size = Pt(15)
    p_lt.font.bold = True
    p_lt.font.color.rgb = RGBColor(194, 65, 12)
    
    tb_l = slide.shapes.add_textbox(Inches(1.1), Inches(2.4), Inches(5.2), Inches(3.9))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    for i, b in enumerate(left_bullets):
        p = tf_l.paragraphs[0] if i == 0 else tf_l.add_paragraph()
        if isinstance(b, tuple):
            h, t = b
            r1 = p.add_run(); r1.text = f'• {h}: '; r1.font.bold = True; r1.font.size = Pt(11); r1.font.color.rgb = COLOR_TITLE
            r2 = p.add_run(); r2.text = t; r2.font.size = Pt(11); r2.font.color.rgb = COLOR_BODY
        else:
            p.text = f'• {b}'; p.font.size = Pt(11); p.font.color.rgb = COLOR_BODY
        p.space_after = Pt(6)

    box_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.7))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = COLOR_WHITE
    box_r.line.color.rgb = COLOR_CARD_BORDER

    tb_rt = slide.shapes.add_textbox(Inches(7.0), Inches(1.95), Inches(5.2), Inches(0.4))
    p_rt = tb_rt.text_frame.paragraphs[0]
    p_rt.text = right_title
    p_rt.font.size = Pt(15)
    p_rt.font.bold = True
    p_rt.font.color.rgb = RGBColor(15, 23, 42)

    tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(2.4), Inches(5.2), Inches(3.9))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    for i, b in enumerate(right_bullets):
        p = tf_r.paragraphs[0] if i == 0 else tf_r.add_paragraph()
        if isinstance(b, tuple):
            h, t = b
            r1 = p.add_run(); r1.text = f'• {h}: '; r1.font.bold = True; r1.font.size = Pt(11); r1.font.color.rgb = COLOR_TITLE
            r2 = p.add_run(); r2.text = t; r2.font.size = Pt(11); r2.font.color.rgb = COLOR_BODY
        else:
            p.text = f'• {b}'; p.font.size = Pt(11); p.font.color.rgb = COLOR_BODY
        p.space_after = Pt(6)

def add_bullet_content(slide, title, bullets):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.8), Inches(11.5), Inches(4.7))
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_WHITE
    box.line.color.rgb = COLOR_CARD_BORDER

    tb = slide.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(10.9), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if isinstance(item, tuple):
            hdr, body = item
            r1 = p.add_run(); r1.text = f'• {hdr}: '; r1.font.bold = True; r1.font.size = Pt(12); r1.font.color.rgb = COLOR_TITLE
            r2 = p.add_run(); r2.text = body; r2.font.size = Pt(12); r2.font.color.rgb = COLOR_BODY
        else:
            p.text = f'• {item}'; p.font.size = Pt(12); p.font.color.rgb = COLOR_BODY
        p.space_after = Pt(8)
