"""
test_pdf_layout.py
Premium invoice PDF generator for AI-Umroh using ReportLab.
Color palette: Emerald Green (#1A6B4A) and Dark Gold (#C9A84C).
"""

import os
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─── Colour palette ────────────────────────────────────────────────────────────
EMERALD      = colors.HexColor("#1A6B4A")
EMERALD_DARK = colors.HexColor("#124D35")
EMERALD_SOFT = colors.HexColor("#E8F5EE")
GOLD         = colors.HexColor("#C9A84C")
GOLD_LIGHT   = colors.HexColor("#F9F1DC")
DARK_TEXT    = colors.HexColor("#1C1C1C")
MID_TEXT     = colors.HexColor("#4A4A4A")
LIGHT_TEXT   = colors.HexColor("#7A7A7A")
WHITE        = colors.HexColor("#FFFFFF")
RULE_GREY    = colors.HexColor("#D9D9D9")

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm

# ─── Sample data ───────────────────────────────────────────────────────────────
INVOICE_ID   = "INV-UMR-2026-0042"
INVOICE_DATE = date(2026, 5, 21).strftime("%d %B %Y")
DUE_DATE     = date(2026, 6, 10).strftime("%d %B %Y")
CUSTOMER     = "H. Budi Santoso"
PHONE        = "+62 812-3456-7890"
PACKAGE      = "Paket Umroh Reguler 14 Hari – Keberangkatan September 2026"

PILGRIMS = [
    ("H. Budi Santoso",      "Surabaya",   1),
    ("Hj. Sri Wahyuningsih", "Surabaya",   1),
    ("Muhammad Farhan",       "Sidoarjo",   1),
    ("Aisyah Rahmawati",      "Gresik",     1),
    ("Drs. Agus Firmansyah",  "Malang",     1),
]

FEES = [
    ("Paket Dasar Umroh 14 Hari", 5, 28_500_000),
    ("Biaya Visa & Asuransi",     5,  1_250_000),
    ("Perlengkapan Jemaah",       5,    750_000),
]
DP_AMOUNT    = 50_000_000
UNIQUE_CODE  = 42
TOTAL_GROSS  = sum(qty * price for _, qty, price in FEES)
REMAINING    = TOTAL_GROSS - DP_AMOUNT + UNIQUE_CODE

# ─── Custom flowables ──────────────────────────────────────────────────────────

class ColorRect(Flowable):
    """Solid colour rectangle – used for the header banner."""
    def __init__(self, w, h, fill, radius=0):
        Flowable.__init__(self)
        self.w, self.h, self.fill, self.radius = w, h, fill, radius

    def draw(self):
        self.canv.setFillColor(self.fill)
        if self.radius:
            self.canv.roundRect(0, 0, self.w, self.h, self.radius, fill=1, stroke=0)
        else:
            self.canv.rect(0, 0, self.w, self.h, fill=1, stroke=0)


class CalloutBox(Flowable):
    """Highlighted callout box (used for BSI bank transfer info)."""
    def __init__(self, w, lines, bg, border, text_color, font_size=9.5, radius=6):
        Flowable.__init__(self)
        self.w = w
        self.lines = lines        # list of (label, value, bold_value)
        self.bg = bg
        self.border = border
        self.text_color = text_color
        self.font_size = font_size
        self.radius = radius
        self.line_h = font_size + 5
        self.pad = 14
        self.h = self.pad * 2 + len(lines) * self.line_h + 4

    def wrap(self, *args):
        return self.w, self.h

    def draw(self):
        c = self.canv
        # Background
        c.setFillColor(self.bg)
        c.setStrokeColor(self.border)
        c.setLineWidth(1.2)
        c.roundRect(0, 0, self.w, self.h, self.radius, fill=1, stroke=1)
        # Left accent bar
        c.setFillColor(self.border)
        c.roundRect(0, 0, 5, self.h, self.radius, fill=1, stroke=0)
        # Text
        c.setFillColor(self.text_color)
        y = self.h - self.pad - self.line_h + 3
        for label, value, bold_val in self.lines:
            c.setFont("Helvetica", self.font_size)
            c.drawString(14, y, label)
            if bold_val:
                c.setFont("Helvetica-Bold", self.font_size + 0.5)
            else:
                c.setFont("Helvetica", self.font_size)
            c.drawRightString(self.w - self.pad, y, value)
            y -= self.line_h


# ─── Helpers ──────────────────────────────────────────────────────────────────

def rp(amount: int) -> str:
    """Format integer as Indonesian Rupiah string."""
    return f"Rp {amount:,.0f}".replace(",", ".")


def styles():
    base = getSampleStyleSheet()
    s = {}

    s["company"] = ParagraphStyle("company",
        fontName="Helvetica-Bold", fontSize=17, textColor=WHITE,
        leading=21, alignment=TA_LEFT)

    s["company_sub"] = ParagraphStyle("company_sub",
        fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#AADFC4"),
        leading=13, alignment=TA_LEFT)

    s["invoice_tag"] = ParagraphStyle("invoice_tag",
        fontName="Helvetica-Bold", fontSize=22, textColor=GOLD,
        leading=26, alignment=TA_RIGHT)

    s["invoice_meta"] = ParagraphStyle("invoice_meta",
        fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#AADFC4"),
        leading=14, alignment=TA_RIGHT)

    s["section_title"] = ParagraphStyle("section_title",
        fontName="Helvetica-Bold", fontSize=10, textColor=EMERALD,
        leading=14, spaceAfter=4, spaceBefore=12)

    s["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=9.5, textColor=DARK_TEXT, leading=14)

    s["body_bold"] = ParagraphStyle("body_bold",
        fontName="Helvetica-Bold", fontSize=9.5, textColor=DARK_TEXT, leading=14)

    s["small"] = ParagraphStyle("small",
        fontName="Helvetica", fontSize=8.5, textColor=LIGHT_TEXT, leading=12)

    s["footer"] = ParagraphStyle("footer",
        fontName="Helvetica", fontSize=8, textColor=LIGHT_TEXT,
        leading=11, alignment=TA_CENTER)

    return s


# ─── Build PDF ─────────────────────────────────────────────────────────────────

def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"Invoice {INVOICE_ID}",
        author="PT Berkah Umroh Internasional",
    )

    s = styles()
    usable_w = PAGE_W - 2 * MARGIN
    story = []

    # ── HEADER BANNER ───────────────────────────────────────────────────────────
    BANNER_H = 3.8 * cm

    left_col = [
        [Paragraph("PT Berkah Umroh Internasional", s["company"])],
        [Paragraph(
            "Jl. Sudirman No. 88, Jakarta Selatan 12190<br/>"
            "Telp: (021) 5550-1234  |  www.berkah-umroh.co.id",
            s["company_sub"]
        )],
    ]
    right_col = [
        [Paragraph("INVOICE", s["invoice_tag"])],
        [Paragraph(
            f"<b>{INVOICE_ID}</b><br/>"
            f"Tanggal: {INVOICE_DATE}<br/>"
            f"Jatuh Tempo: {DUE_DATE}",
            s["invoice_meta"]
        )],
    ]

    header_table = Table(
        [[
            Table(left_col,  colWidths=[usable_w * 0.6], rowHeights=None),
            Table(right_col, colWidths=[usable_w * 0.4], rowHeights=None),
        ]],
        colWidths=[usable_w * 0.6, usable_w * 0.4],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), EMERALD_DARK),
        ("TOPPADDING",   (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 18),
        ("LEFTPADDING",  (0, 0), (0, -1), 18),
        ("RIGHTPADDING", (1, 0), (1, -1), 18),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5 * cm))

    # Gold accent line
    story.append(HRFlowable(width=usable_w, thickness=2, color=GOLD, spaceAfter=6))

    # ── BILL-TO / CUSTOMER INFO ─────────────────────────────────────────────────
    story.append(Paragraph("DITAGIHKAN KEPADA", s["section_title"]))

    bill_data = [
        [Paragraph(f"<b>{CUSTOMER}</b>", s["body_bold"]),
         Paragraph(f"<b>Paket:</b> {PACKAGE}", s["body"])],
        [Paragraph(f"Telp: {PHONE}", s["small"]),
         Paragraph("", s["small"])],
    ]
    bill_table = Table(bill_data, colWidths=[usable_w * 0.38, usable_w * 0.62])
    bill_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), EMERALD_SOFT),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW",    (0, -1), (-1, -1), 0.5, EMERALD),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(bill_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── PILGRIM MANIFEST TABLE ──────────────────────────────────────────────────
    story.append(Paragraph("MANIFEST JEMAAH", s["section_title"]))

    manifest_header = ["No.", "Nama Jemaah", "Domisili", "Jumlah Pax"]
    manifest_rows = [manifest_header]
    for i, (name, dom, pax) in enumerate(PILGRIMS, 1):
        manifest_rows.append([str(i), name, dom, str(pax)])
    manifest_rows.append(["", "", Paragraph("<b>Total Jemaah</b>", s["body_bold"]),
                           Paragraph(f"<b>{sum(p for _, _, p in PILGRIMS)}</b>", s["body_bold"])])

    manifest_col_w = [0.8 * cm, usable_w * 0.45, usable_w * 0.28, usable_w * 0.15]
    manifest_table = Table(manifest_rows, colWidths=manifest_col_w, repeatRows=1)
    manifest_style = [
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0), EMERALD),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        # Data rows
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 1), (-1, -1), DARK_TEXT),
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("ALIGN",         (3, 0), (3, -1), "CENTER"),
        # Alternating rows
        *[("BACKGROUND", (0, r), (-1, r), EMERALD_SOFT)
          for r in range(2, len(manifest_rows) - 1, 2)],
        # Total row
        ("BACKGROUND",    (0, -1), (-1, -1), GOLD_LIGHT),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE",     (0, -1), (-1, -1), 1, GOLD),
        # Grid
        ("GRID",          (0, 0), (-1, -1), 0.4, RULE_GREY),
        ("ROWBACKGROUND", (0, 0), (-1, 0), EMERALD),
        # Padding
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    manifest_table.setStyle(TableStyle(manifest_style))
    story.append(manifest_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── FEE BREAKDOWN TABLE ─────────────────────────────────────────────────────
    story.append(Paragraph("RINCIAN BIAYA", s["section_title"]))

    fee_header = ["Deskripsi", "Jml Pax", "Harga / Pax", "Subtotal"]
    fee_rows   = [fee_header]
    for desc, qty, price in FEES:
        fee_rows.append([desc, str(qty), rp(price), rp(qty * price)])

    # Subtotal, DP, unique code, remaining
    fee_rows.append(["", "", Paragraph("<b>Subtotal</b>", s["body_bold"]),
                     Paragraph(f"<b>{rp(TOTAL_GROSS)}</b>", s["body_bold"])])
    fee_rows.append(["", "", "DP yang Diterima",
                     Paragraph(f"<font color='#1A6B4A'>- {rp(DP_AMOUNT)}</font>", s["body"])])
    fee_rows.append(["", "", "Kode Unik",
                     Paragraph(f"<font color='#C9A84C'>+ Rp {UNIQUE_CODE:,.0f}</font>", s["body"])])
    fee_rows.append(["", "", Paragraph("<b>SISA TAGIHAN</b>", s["body_bold"]),
                     Paragraph(f"<b>{rp(REMAINING)}</b>",
                                ParagraphStyle("tot", fontName="Helvetica-Bold",
                                               fontSize=11, textColor=EMERALD))])

    fee_col_w = [usable_w * 0.44, 0.9 * cm, usable_w * 0.26, usable_w * 0.22]
    fee_table = Table(fee_rows, colWidths=fee_col_w, repeatRows=1)
    n_data = len(FEES) + 1   # header + data rows
    fee_style = [
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0), EMERALD),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("ALIGN",         (1, 0), (-1, 0), "RIGHT"),
        # Data
        ("FONTNAME",      (0, 1), (-1, n_data - 1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 1), (-1, n_data - 1), DARK_TEXT),
        ("ALIGN",         (1, 1), (-1, -1), "RIGHT"),
        # Alternating rows
        *[("BACKGROUND", (0, r), (-1, r), EMERALD_SOFT)
          for r in range(2, n_data, 2)],
        # Summary rows
        ("BACKGROUND",    (0, n_data), (-1, n_data), colors.HexColor("#F0F0F0")),
        ("BACKGROUND",    (0, n_data + 1), (-1, n_data + 1), WHITE),
        ("BACKGROUND",    (0, n_data + 2), (-1, n_data + 2), WHITE),
        ("BACKGROUND",    (0, n_data + 3), (-1, n_data + 3), GOLD_LIGHT),
        ("LINEABOVE",     (0, n_data), (-1, n_data), 0.8, EMERALD),
        ("LINEABOVE",     (0, n_data + 3), (-1, n_data + 3), 1.5, GOLD),
        ("LINEBELOW",     (0, n_data + 3), (-1, n_data + 3), 1.5, GOLD),
        # Grid
        ("GRID",          (0, 0), (-1, n_data + 3), 0.4, RULE_GREY),
        # Padding
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        # Span description col for summary rows
        ("SPAN",          (0, n_data), (1, n_data)),
        ("SPAN",          (0, n_data + 1), (1, n_data + 1)),
        ("SPAN",          (0, n_data + 2), (1, n_data + 2)),
        ("SPAN",          (0, n_data + 3), (1, n_data + 3)),
    ]
    fee_table.setStyle(TableStyle(fee_style))
    story.append(fee_table)
    story.append(Spacer(1, 0.6 * cm))

    # ── BSI BANK TRANSFER CALLOUT ───────────────────────────────────────────────
    story.append(Paragraph("INFORMASI PEMBAYARAN", s["section_title"]))

    bsi_lines = [
        ("Bank",           "Bank Syariah Indonesia (BSI)",    True),
        ("No. Rekening",   "7 1234 5678 9",                   True),
        ("Atas Nama",      "PT Berkah Umroh Internasional",   False),
        ("Nominal Transfer", rp(REMAINING),                   True),
        ("Kode Unik",      f"Rp {UNIQUE_CODE} (wajib disertakan)", False),
    ]
    callout = CalloutBox(
        w=usable_w,
        lines=bsi_lines,
        bg=GOLD_LIGHT,
        border=GOLD,
        text_color=DARK_TEXT,
        font_size=9.5,
        radius=8,
    )
    story.append(callout)
    story.append(Spacer(1, 0.4 * cm))

    # Note
    note_style = ParagraphStyle("note", fontName="Helvetica", fontSize=8.5,
                                textColor=LIGHT_TEXT, leading=13,
                                borderPad=8, borderColor=RULE_GREY,
                                borderWidth=0.5, backColor=colors.HexColor("#F9F9F9"))
    story.append(Paragraph(
        "<b>Catatan:</b> Harap menyertakan <b>Kode Unik</b> pada akhir nominal transfer "
        "agar pembayaran dapat diverifikasi secara otomatis oleh sistem kami. "
        "Konfirmasi pembayaran via WhatsApp ke nomor: <b>+62 811-2233-4455</b>.",
        note_style
    ))

    # ── FOOTER ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8 * cm))
    story.append(HRFlowable(width=usable_w, thickness=1, color=GOLD, spaceAfter=6))
    story.append(Paragraph(
        "PT Berkah Umroh Internasional  •  Izin Penyelenggara Perjalanan Ibadah Umroh No. D/xxx/2024  "
        "•  Dokumen ini digenerate secara otomatis dan sah tanpa tanda tangan.",
        s["footer"]
    ))

    doc.build(story)
    print(f"[OK] PDF berhasil dibuat: {output_path}")


# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(out_dir, "test_invoice_sample.pdf")
    build_pdf(output_path)
