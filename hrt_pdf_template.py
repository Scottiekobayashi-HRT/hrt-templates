"""
HRT_PDF_TEMPLATE.py
Hawaii Reward Travel — PDF Report Scaffold
Version: 3.1 | Printer-friendly | White background throughout

USAGE:
Import this file and call build_report(output_path, story_elements, route_label, date_label, cabin_label)
All styles, colors, and layout components are defined here.
Report content is assembled by the caller using the helper functions below.

LOGO NOTE:
Currently using a vector placeholder logo (white background, teal/gold).
Replace the HRTLogo class with a final branded version when available.
"""

import base64, io, math, os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.platypus.flowables import Flowable

# ─────────────────────────────────────────────
# BRAND COLORS
# ─────────────────────────────────────────────
TEAL        = colors.HexColor("#0C5E73")
GOLD        = colors.HexColor("#C9A457")
BLACK       = colors.HexColor("#1a1a1a")
WHITE       = colors.white
LIGHT_GRAY  = colors.HexColor("#f5f5f5")
MID_GRAY    = colors.HexColor("#cccccc")
DARK_GRAY   = colors.HexColor("#555555")
AMBER_BG    = colors.HexColor("#fff8e1")
AMBER_BORDER= colors.HexColor("#e6c87a")
AMBER_TEXT  = colors.HexColor("#5a3010")
AMBER_LABEL = colors.HexColor("#8B4513")

# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
F_HEAD      = "Times-Roman"
F_HEAD_B    = "Times-Bold"
F_BODY      = "Helvetica"
F_BODY_B    = "Helvetica-Bold"
F_BODY_I    = "Helvetica-Oblique"

# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────
PAGE_W, PAGE_H  = letter
ML = MR = 0.75 * inch
MT = MB = 0.75 * inch
CW = PAGE_W - ML - MR          # content width

# ─────────────────────────────────────────────
# LOGO — Vector placeholder (white background)
# Replace HRTLogo class with final branded version when available
# ─────────────────────────────────────────────
class HRTLogo(Flowable):
    """
    Vector HRT logo for white-background reports.
    HAWAII / REWARD / TRAVEL stacked text + flight arc + island silhouettes.
    Placeholder until a final white-background branded logo is provided.
    """
    def __init__(self, width=3.8*inch):
        Flowable.__init__(self)
        self.logo_width  = width
        self.logo_height = width * (90 / 500)
        self.width  = self.logo_width
        self.height = self.logo_height
        self.hAlign = "CENTER"

    def draw(self):
        c = self.canv
        w = self.logo_width
        h = self.logo_height
        fs = h * 0.36

        # Text block
        c.setFont("Helvetica-Bold", fs)
        c.setFillColor(TEAL);  c.drawString(0, h * 0.64, "HAWAII")
        c.setFillColor(GOLD);  c.drawString(0, h * 0.30, "REWARD")
        c.setFillColor(TEAL);  c.drawString(0, h * -0.04, "TRAVEL")

        # Graphic area
        gx = w * 0.54
        gw = w - gx - w * 0.01
        gh = h
        arc_cx = gx + gw * 0.18
        arc_cy = gh * 0.18

        # Dotted arcs
        def dotted_arc(rx, ry, s_deg, e_deg, segs=14):
            step = (e_deg - s_deg) / segs
            for i in range(segs):
                if i % 2 == 0:
                    a1 = math.radians(s_deg + i * step)
                    a2 = math.radians(s_deg + (i + 0.55) * step)
                    c.setStrokeColor(TEAL)
                    c.setLineWidth(0.9)
                    c.line(arc_cx + rx*math.cos(a1), arc_cy + ry*math.sin(a1),
                           arc_cx + rx*math.cos(a2), arc_cy + ry*math.sin(a2))

        dotted_arc(gw*0.30, gh*0.58, 22, 112)
        dotted_arc(gw*0.48, gh*0.76, 18, 106)
        dotted_arc(gw*0.64, gh*0.92, 14, 100)

        def plane(px, py, angle, s):
            c.saveState()
            c.translate(px, py); c.rotate(angle)
            c.setFillColor(TEAL)
            for pts in [
                [(-s*.12,-s*.55),(-s*.12,s*.55),(s*.12,s*.55),(s*.12,-s*.55)],
                [(-s*.62,s*.05),(s*.62,s*.05),(s*.12,s*.35),(-s*.12,s*.35)],
                [(-s*.30,-s*.50),(s*.30,-s*.50),(s*.12,-s*.20),(-s*.12,-s*.20)],
            ]:
                p = c.beginPath()
                p.moveTo(*pts[0])
                for pt in pts[1:]: p.lineTo(*pt)
                p.close(); c.drawPath(p, fill=1, stroke=0)
            c.restoreState()

        plane(arc_cx + gw*.48*math.cos(math.radians(106)),
              arc_cy + gh*.76*math.sin(math.radians(106)), 38, h*.115)
        plane(arc_cx + gw*.64*math.cos(math.radians(100)),
              arc_cy + gh*.92*math.sin(math.radians(100)), 35, h*.080)

        # Islands
        c.setFillColor(TEAL)
        bx = gx + gw*.60; by = gh*.01; bs = gw*.30
        for path_pts in [
            # Big Island
            [(bx,by+bs*.48),(bx+bs*.32,by+bs*.88),(bx+bs*.72,by+bs*.72),
             (bx+bs*.88,by+bs*.28),(bx+bs*.55,by),(bx+bs*.12,by+bs*.08)],
        ]:
            p = c.beginPath()
            p.moveTo(*path_pts[0])
            for pt in path_pts[1:]: p.lineTo(*pt)
            p.close(); c.drawPath(p, fill=1, stroke=0)

        mx = bx-bs*.20; my = by+bs*.62; ms = gw*.15
        p = c.beginPath()
        p.moveTo(mx,my+ms*.28); p.lineTo(mx+ms*.48,my+ms*.62)
        p.lineTo(mx+ms*.82,my+ms*.40); p.lineTo(mx+ms*.62,my)
        p.lineTo(mx+ms*.08,my+ms*.08); p.close()
        c.drawPath(p, fill=1, stroke=0)

        ox = mx-bs*.24; oy = my+ms*.30
        c.ellipse(ox-gw*.048, oy-gw*.022, ox+gw*.048, oy+gw*.022, fill=1, stroke=0)
        c.circle(ox-bs*.20, oy+ms*.22, gw*.028, fill=1, stroke=0)


def get_logo(width=3.8*inch):
    logo = HRTLogo(width=width)
    logo.hAlign = "CENTER"
    return logo
# ─────────────────────────────────────────────
# PARAGRAPH STYLES
# ─────────────────────────────────────────────
_STYLES = {}

def _s(name):
    if name in _STYLES:
        return _STYLES[name]
    defs = {
        "heading_main": ParagraphStyle("heading_main",
            fontName=F_HEAD_B, fontSize=22, textColor=TEAL,
            alignment=TA_CENTER, spaceAfter=4),
        "heading_sub": ParagraphStyle("heading_sub",
            fontName=F_HEAD, fontSize=11, textColor=GOLD,
            alignment=TA_CENTER, spaceAfter=2),
        "report_line": ParagraphStyle("report_line",
            fontName=F_BODY, fontSize=10, textColor=DARK_GRAY,
            alignment=TA_CENTER),
        "section_label": ParagraphStyle("section_label",
            fontName=F_BODY_B, fontSize=7, textColor=TEAL,
            spaceAfter=2, leading=10),
        "section_title": ParagraphStyle("section_title",
            fontName=F_HEAD_B, fontSize=16, textColor=TEAL,
            spaceAfter=6),
        "option_label": ParagraphStyle("option_label",
            fontName=F_BODY_B, fontSize=7, textColor=GOLD,
            spaceAfter=2, leading=10),
        "option_title": ParagraphStyle("option_title",
            fontName=F_HEAD_B, fontSize=18, textColor=TEAL,
            spaceAfter=2),
        "option_subtitle": ParagraphStyle("option_subtitle",
            fontName=F_BODY, fontSize=10, textColor=DARK_GRAY,
            spaceAfter=10),
        "body": ParagraphStyle("body",
            fontName=F_BODY, fontSize=10, textColor=BLACK,
            leading=15, spaceAfter=8),
        "body_bold": ParagraphStyle("body_bold",
            fontName=F_BODY_B, fontSize=10, textColor=BLACK, leading=15),
        "body_small": ParagraphStyle("body_small",
            fontName=F_BODY, fontSize=9, textColor=DARK_GRAY,
            leading=13, spaceAfter=4),
        "spoiler": ParagraphStyle("spoiler",
            fontName=F_HEAD_B, fontSize=13, textColor=GOLD, spaceAfter=6),
        "scottie": ParagraphStyle("scottie",
            fontName=F_BODY_I, fontSize=10, textColor=BLACK,
            leading=16, spaceAfter=8),
        "checklist_item": ParagraphStyle("checklist_item",
            fontName=F_BODY, fontSize=9.5, textColor=BLACK,
            leading=14, leftIndent=0),
        "math_normal": ParagraphStyle("math_normal",
            fontName=F_BODY, fontSize=9.5, textColor=BLACK,
            leading=14, spaceAfter=3),
        "math_highlight": ParagraphStyle("math_highlight",
            fontName=F_BODY_B, fontSize=10, textColor=TEAL, leading=14),
        "footer": ParagraphStyle("footer",
            fontName=F_BODY, fontSize=7.5, textColor=MID_GRAY,
            alignment=TA_CENTER),
        "mini_brand": ParagraphStyle("mini_brand",
            fontName=F_BODY_B, fontSize=8, textColor=TEAL),
        "mini_detail": ParagraphStyle("mini_detail",
            fontName=F_BODY, fontSize=8, textColor=DARK_GRAY,
            alignment=TA_RIGHT),
        # Table cell styles
        "tbl_label": ParagraphStyle("tbl_label",
            fontName=F_BODY_B, fontSize=7, textColor=TEAL, leading=10),
        "tbl_value": ParagraphStyle("tbl_value",
            fontName=F_BODY, fontSize=9.5, textColor=BLACK, leading=13),
        "tbl_value_b": ParagraphStyle("tbl_value_b",
            fontName=F_BODY_B, fontSize=9.5, textColor=BLACK, leading=13),
        "glance_label": ParagraphStyle("glance_label",
            fontName=F_BODY_B, fontSize=7, textColor=GOLD, leading=10),
        "glance_value": ParagraphStyle("glance_value",
            fontName=F_BODY_B, fontSize=10, textColor=TEAL, leading=13),
        "box_label_teal": ParagraphStyle("box_label_teal",
            fontName=F_BODY_B, fontSize=7, textColor=TEAL,
            leading=10, spaceAfter=4),
        "box_label_amber": ParagraphStyle("box_label_amber",
            fontName=F_BODY_B, fontSize=7, textColor=AMBER_LABEL,
            leading=10, spaceAfter=4),
        "box_body_dark": ParagraphStyle("box_body_dark",
            fontName=F_BODY, fontSize=9.5, textColor=BLACK, leading=14),
        "box_body_amber": ParagraphStyle("box_body_amber",
            fontName=F_BODY, fontSize=9.5, textColor=AMBER_TEXT, leading=14),
    }
    _STYLES.update(defs)
    return _STYLES[name]

# ─────────────────────────────────────────────
# PRIMITIVES
# ─────────────────────────────────────────────
def divider(color=TEAL, thickness=0.75, sb=4, sa=10):
    return HRFlowable(width="100%", thickness=thickness,
                      color=color, spaceBefore=sb, spaceAfter=sa)

def gold_divider():
    return HRFlowable(width="100%", thickness=1.0,
                      color=GOLD, spaceBefore=2, spaceAfter=8)

def section_header(label, title):
    return [
        Paragraph(label.upper(), _s("section_label")),
        Paragraph(title, _s("section_title")),
        divider(),
    ]

def option_header(tag, title, subtitle):
    return [
        Paragraph(tag.upper(), _s("option_label")),
        Paragraph(title, _s("option_title")),
        Paragraph(subtitle, _s("option_subtitle")),
    ]

# ─────────────────────────────────────────────
# COVER HEADER
# ─────────────────────────────────────────────
def cover_header(route_label, date_label, cabin_label):
    logo = get_logo(width=3.8*inch)
    sub  = Paragraph("BOOKING RESEARCH &amp; STEP-BY-STEP RECOMMENDATIONS",
                     _s("heading_sub"))
    rep  = Paragraph(f"Award Flight Report &mdash; {route_label} &mdash; {date_label}",
                     _s("report_line"))
    return [logo, Spacer(1,6), sub, Spacer(1,4), rep,
            Spacer(1,6), gold_divider()]

# ─────────────────────────────────────────────
# MINI PAGE HEADER (option pages)
# ─────────────────────────────────────────────
def mini_header(route_label, date_label, cabin_label):
    brand  = Paragraph("HAWAII REWARD TRAVEL", _s("mini_brand"))
    detail = Paragraph(f"{route_label}  |  {date_label}  |  {cabin_label}",
                       _s("mini_detail"))
    t = Table([[brand, detail]], colWidths=[3*inch, CW-3*inch])
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1),5),
        ("BOTTOMPADDING", (0,0),(-1,-1),5),
        ("LEFTPADDING",   (0,0),(-1,-1),0),
        ("RIGHTPADDING",  (0,0),(-1,-1),0),
        ("LINEBELOW",     (0,0),(-1,-1),1.2,TEAL),
    ]))
    return t

# ─────────────────────────────────────────────
# AT A GLANCE TABLE (white bg, teal borders/text)
# ─────────────────────────────────────────────
def at_a_glance(fields, transfer_path):
    """
    fields: list of (label, value) tuples — up to 8, shown 4-per-row
    transfer_path: string shown in full-width row at bottom
    """
    rows = []
    for i in range(0, len(fields), 4):
        chunk = fields[i:i+4]
        while len(chunk) < 4:
            chunk.append(("", ""))
        rows.append([Paragraph(f[0].upper(), _s("glance_label")) for f in chunk])
        rows.append([Paragraph(f[1],         _s("glance_value")) for f in chunk])

    cw = CW / 4
    t = Table(rows, colWidths=[cw]*4)
    style = [
        ("BACKGROUND",    (0,0),(-1,-1), WHITE),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("BOX",           (0,0),(-1,-1), 1,   TEAL),
        ("INNERGRID",     (0,0),(-1,-1), 0.4, MID_GRAY),
    ]
    # Shade alternate label rows lightly
    for i in range(0, len(rows), 2):
        style.append(("BACKGROUND", (0,i),(-1,i), LIGHT_GRAY))
    t.setStyle(TableStyle(style))

    # Transfer path full-width row
    tp_label = Paragraph("TRANSFER PATH", _s("glance_label"))
    tp_value = Paragraph(transfer_path,   _s("tbl_value_b"))
    tp = Table([[tp_label],[tp_value]], colWidths=[CW])
    tp.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), WHITE),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("BOX",           (0,0),(-1,-1), 1, TEAL),
        ("LINEABOVE",     (0,0),(-1,0),  0.4, MID_GRAY),
    ]))
    return [t, tp]

# ─────────────────────────────────────────────
# TRIP REQUEST TABLE
# ─────────────────────────────────────────────
def trip_request_table(fields):
    """fields: list of (label, value) tuples"""
    rows = [[
        Paragraph(label, _s("tbl_label")),
        Paragraph(value, _s("tbl_value"))
    ] for label, value in fields]
    t = Table(rows, colWidths=[2.1*inch, CW-2.1*inch])
    style = [
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("BOX",           (0,0),(-1,-1), 0.5, TEAL),
        ("LINEBELOW",     (0,0),(-1,-1), 0.3, MID_GRAY),
    ]
    for i in range(0, len(rows), 2):
        style.append(("BACKGROUND",(0,i),(-1,i), LIGHT_GRAY))
    t.setStyle(TableStyle(style))
    return t

# ─────────────────────────────────────────────
# FLIGHT DETAILS TABLE
# ─────────────────────────────────────────────
def flight_details_table(segments):
    """segments: list of dicts {segment, route, departure, arrival, duration}"""
    hdrs = ["Segment","Route","Departure","Arrival","Duration"]
    header_row = [Paragraph(h, ParagraphStyle("fh",
        fontName=F_BODY_B, fontSize=9, textColor=TEAL)) for h in hdrs]
    rows = [header_row]
    for s in segments:
        rows.append([
            Paragraph(s.get("segment",""),   _s("body_small")),
            Paragraph(s.get("route",""),     _s("body_small")),
            Paragraph(s.get("departure",""), _s("body_small")),
            Paragraph(s.get("arrival",""),   _s("body_small")),
            Paragraph(s.get("duration",""),  _s("body_small")),
        ])
    cws = [1.4*inch, 1.1*inch, 1.5*inch, 1.55*inch, 1.0*inch]
    t = Table(rows, colWidths=cws)
    style = [
        ("BACKGROUND",    (0,0),(-1,0),  LIGHT_GRAY),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("BOX",           (0,0),(-1,-1), 0.5, TEAL),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, MID_GRAY),
        ("LINEBELOW",     (0,0),(- 1,0), 1.0, TEAL),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND",(0,i),(-1,i), LIGHT_GRAY))
    t.setStyle(TableStyle(style))
    return t

# ─────────────────────────────────────────────
# CALLOUT BOXES  (all white bg, colored borders/labels)
# ─────────────────────────────────────────────
def _bordered_box(label_text, body_text, label_style, body_style,
                  bg=WHITE, border_color=TEAL, border_w=1.0):
    label = Paragraph(label_text, _s(label_style))
    body  = Paragraph(body_text,  _s(body_style))
    t = Table([[label],[body]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("BOX",           (0,0),(-1,-1), border_w, border_color),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
    ]))
    return t

def start_here_box(text):
    """Teal-bordered START HERE box."""
    return _bordered_box("START HERE", text,
                         "box_label_teal", "box_body_dark",
                         bg=WHITE, border_color=TEAL, border_w=1.5)

def safety_rule_box(text):
    """Gold-bordered Safety Rule box."""
    return _bordered_box("SAFETY RULE", text,
                         "box_label_teal", "box_body_dark",
                         bg=WHITE, border_color=GOLD, border_w=1.5)

def availability_note_box(text):
    """Light teal-bordered Availability Note box."""
    return _bordered_box("AVAILABILITY NOTE", text,
                         "box_label_teal", "box_body_dark",
                         bg=LIGHT_GRAY, border_color=TEAL, border_w=0.8)

def routing_tradeoffs_box(text):
    """
    Amber-bordered Routing Trade-offs box.
    Required for any option with a geographic detour flag.
    Place between Flight Details and Transfer Math.
    """
    return _bordered_box("ROUTING TRADE-OFFS", text,
                         "box_label_amber", "box_body_amber",
                         bg=AMBER_BG, border_color=AMBER_BORDER, border_w=1.2)

def transfer_math_box(lines):
    """
    lines: list of (text, is_highlight) tuples
    is_highlight=True = bold teal (remaining balance line)
    """
    label = Paragraph("TRANSFER MATH", _s("box_label_teal"))
    content = [label]
    for text, hi in lines:
        content.append(Paragraph(text, _s("math_highlight" if hi else "math_normal")))
    rows = [[item] for item in content]
    t = Table(rows, colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT_GRAY),
        ("BOX",           (0,0),(-1,-1), 0.8, TEAL),
        ("LINEBELOW",     (0,0),(0,0),   0.5, TEAL),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
    ]))
    return t

# ─────────────────────────────────────────────
# BOOKING CHECKLIST
# ─────────────────────────────────────────────
def booking_checklist(steps):
    items = []
    for i, step in enumerate(steps, 1):
        num = Paragraph(str(i), ParagraphStyle("cn",
            fontName=F_BODY_B, fontSize=9, textColor=TEAL,
            alignment=TA_CENTER, leading=12))
        txt = Paragraph(step, _s("checklist_item"))
        row = Table([[num, txt]], colWidths=[0.28*inch, CW-0.38*inch])
        row.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(0,0),  WHITE),
            ("BACKGROUND",    (1,0),(1,0),  WHITE),
            ("BOX",           (0,0),(0,0),  1.0, TEAL),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(0,0),   0),
            ("RIGHTPADDING",  (0,0),(0,0),   0),
            ("LEFTPADDING",   (1,0),(1,0),  10),
            ("VALIGN",        (0,0),(-1,-1),"TOP"),
            ("LINEBELOW",     (0,0),(-1,-1), 0.3, MID_GRAY),
        ]))
        items.append(row)
        items.append(Spacer(1,2))
    return items

# ─────────────────────────────────────────────
# PAGE FOOTER
# ─────────────────────────────────────────────
def _draw_footer(canvas, doc, route_label, date_label):
    canvas.saveState()
    # Separator line
    canvas.setStrokeColor(MID_GRAY)
    canvas.setLineWidth(0.3)
    canvas.line(ML, 0.60*inch, PAGE_W-MR, 0.60*inch)
    # Footer text — dark on white, no background
    canvas.setFont(F_BODY, 7.5)
    canvas.setFillColor(DARK_GRAY)
    txt = f"Hawaii Reward Travel  |  {route_label}  |  {date_label}  |  hawaiirewardtravel.com"
    canvas.drawCentredString(PAGE_W/2, 0.44*inch, txt)
    # Page number — right-aligned, same style
    canvas.setFont(F_BODY, 7.5)
    canvas.setFillColor(DARK_GRAY)
    canvas.drawRightString(PAGE_W - MR, 0.44*inch, f"Page {doc.page}")
    canvas.restoreState()

# ─────────────────────────────────────────────
# MAIN BUILD FUNCTION
# ─────────────────────────────────────────────
def build_report(output_path, story, route_label, date_label, cabin_label="Economy"):
    """
    output_path : full file path for the output PDF
    story       : list of ReportLab flowables
    route_label : e.g. "HNL to HND"
    date_label  : e.g. "October 2, 2026"
    cabin_label : e.g. "Economy"
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            leftMargin=ML, rightMargin=MR,
                            topMargin=MT, bottomMargin=MB)
    def footer_cb(canvas, doc):
        _draw_footer(canvas, doc, route_label, date_label)
    doc.build(story, onFirstPage=footer_cb, onLaterPages=footer_cb)
    return output_path


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    story = []

    # Cover
    story += cover_header("HNL to HND", "October 2, 2026", "Economy")
    story.append(Spacer(1,14))
    story += section_header("Section 1", "Your Trip Request")
    story.append(trip_request_table([
        ("Origin",                  "HNL — Daniel K. Inouye International, Honolulu, Hawaii"),
        ("Destination",             "HND — Tokyo International (Haneda), Japan"),
        ("Departure Date",          "Friday, October 2, 2026"),
        ("Preferred Cabin",         "Economy"),
        ("Chase Ultimate Rewards",  "170,000 points"),
        ("Capital One Miles",       "85,000 miles"),
        ("Amex Membership Rewards", "Not provided"),
    ]))
    story.append(Spacer(1,14))
    story += section_header("Section 2", "Your Best Booking Path")
    story.append(Paragraph("Spoiler Alert:", _s("spoiler")))
    story.append(Paragraph(
        "Your most straightforward booking right now is the United Airlines Economy "
        "flight via Guam, bookable today by transferring 55,000 Chase Ultimate Rewards "
        "points to United MileagePlus at a 1:1 ratio. Your 170,000 Chase balance covers "
        "this comfortably, leaving you 115,000 points after the transfer. Out-of-pocket "
        "cash for taxes and fees is just $11.00.", _s("body")))

    # Option page
    story.append(PageBreak())
    story.append(mini_header("HNL to HND", "October 2, 2026", "Economy"))
    story.append(Spacer(1,10))
    story += option_header("Option 2",
        "United Airlines Economy via Guam",
        "1 Stop  |  HNL to GUM to HND  |  Chase Ultimate Rewards to United MileagePlus")
    story += at_a_glance([
        ("Airline",        "United Airlines"),
        ("Route",          "HNL > GUM > HND"),
        ("Departure",      "2:25 PM (Oct 2)"),
        ("Arrival",        "10:30 PM (Oct 3)"),
        ("Total Duration", "13h 5m"),
        ("Stops",          "1 (Guam)"),
        ("Points Cost",    "55,000 miles"),
        ("Taxes & Fees",   "$11.00 cash"),
    ], "Chase Ultimate Rewards > United MileagePlus (1:1)")
    story.append(Spacer(1,12))
    story.append(Paragraph("Flight Details", _s("section_title")))
    story.append(flight_details_table([
        {"segment":"Outbound (Leg 1)","route":"HNL > GUM",
         "departure":"2:25 PM, Oct 2","arrival":"Approx. 7:00 PM, Oct 2","duration":"Approx. 6h"},
        {"segment":"Outbound (Leg 2)","route":"GUM > HND",
         "departure":"Approx. GUM layover","arrival":"10:30 PM, Oct 3","duration":"Approx. 4h"},
    ]))
    story.append(Spacer(1,10))
    story.append(routing_tradeoffs_box(
        "This flight connects through Guam, which sits southwest of Hawaii and south of "
        "Japan. That means the route travels away from Tokyo before turning back toward it, "
        "adding significant distance to the journey. Total travel time on this option is "
        "approximately 13 hours and 5 minutes. The best nonstop alternative runs approximately "
        "8 hours and 30 minutes — a difference of roughly 4.5 hours. This option is included "
        "because it is fully bookable online today using your Chase points with no phone call "
        "required. Whether the added travel time is worth the convenience is your call."
    ))
    story.append(Spacer(1,10))
    story.append(transfer_math_box([
        ("Chase Ultimate Rewards transfers to United MileagePlus at 1:1", False),
        ("Award cost: 55,000 United miles", False),
        ("Chase points required: 55,000", False),
        ("Your current Chase balance: 170,000", False),
        ("Remaining Chase balance after transfer: 115,000 points", True),
        ("Out-of-pocket taxes and fees: $11.00", False),
    ]))
    story.append(Spacer(1,10))
    story.append(start_here_box(
        "Log in to your United MileagePlus account and confirm that award seats in economy "
        "are available on the October 2 HNL to GUM to HND routing for your traveling party. "
        "Do not transfer any points until you have visually confirmed the seat count you need "
        "is showing as available."
    ))
    story.append(Spacer(1,8))
    story.append(Paragraph("Booking Checklist", _s("section_title")))
    story += booking_checklist([
        "Go to united.com and search for award availability: HNL to HND, October 2, economy, one way.",
        "Confirm you see the HNL to GUM to HND routing showing available seats for everyone in your traveling party.",
        "Log in to your Chase Ultimate Rewards account at ultimaterewards.com.",
        "Transfer 55,000 Chase points to your United MileagePlus account. Transfers are typically instant.",
        "Return to united.com, search the same itinerary, and complete the award booking.",
        "Pay the $11.00 taxes and fees with your credit card at checkout.",
        "Save or screenshot your booking confirmation and MileagePlus balance for your records.",
    ])
    story.append(Spacer(1,8))
    story.append(safety_rule_box(
        "Do not transfer Chase points to United MileagePlus until you have confirmed that "
        "award seats are available for your full traveling party. Points transfers are instant "
        "and non-reversible."
    ))
    story.append(Spacer(1,6))
    story.append(availability_note_box(
        "This result shows that at least one award seat was available at the time of search. "
        "You will need to confirm the full seat inventory for your traveling party before "
        "transferring points and completing the booking."
    ))

    build_report("/home/claude/HRT_Template_v3_test.pdf",
                 story, "HNL to HND", "October 2, 2026", "Economy")
    print("Template v3 test written")
