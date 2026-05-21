"""
PDF Invoice Generator for AI-Umroh.

Generates a professional Umroh booking invoice PDF using ReportLab.
"""

import os
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Colour palette  (Islamic green / gold theme)
# ---------------------------------------------------------------------------
COLOR_PRIMARY = colors.HexColor("#1B4332")   # deep Islamic green
COLOR_ACCENT = colors.HexColor("#D4A017")    # warm gold
COLOR_LIGHT_GREEN = colors.HexColor("#D8F3DC")  # pale mint for row fill
COLOR_HEADER_BG = colors.HexColor("#1B4332")
COLOR_FOOTER = colors.HexColor("#6C757D")
COLOR_TEXT = colors.HexColor("#212529")
COLOR_WHITE = colors.white

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
INVOICE_DIR = Path(__file__).resolve().parent.parent / "static" / "invoices"
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


# ---------------------------------------------------------------------------
# Helper: format currency (IDR)
# ---------------------------------------------------------------------------
def _fmt_idr(amount) -> str:
    """Return a human-readable IDR string, e.g. 'Rp 5.000.000'."""
    try:
        value = int(amount)
    except (TypeError, ValueError):
        return str(amount)
    return "Rp {:,.0f}".format(value).replace(",", ".")


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------
def generate_invoice_pdf(data: dict) -> str:
    """
    Generate a professional Umroh booking invoice PDF.

    Parameters
    ----------
    data : dict
        Keys expected:
          - invoice_id      : str   e.g. "INV-UMROH-1002"
          - date            : str   e.g. "2026-05-21"
          - fullname        : str   Pilgrim's full name
          - domicile        : str   City / province of origin
          - pax_count       : int   Number of pilgrims
          - package_name    : str   e.g. "Paket Economy 9 Hari"
          - total_tagihan   : int   Grand total in IDR (including unique code)
          - kode_unik       : int   3-digit unique code already included in total
          - bank_name       : str   e.g. "Bank Syariah Indonesia"
          - account_number  : str   e.g. "7123456789"
          - account_name    : str   Name on the bank account

    Returns
    -------
    str
        Absolute path to the generated PDF file.
    """

    # ------------------------------------------------------------------
    # 1. Ensure output directory exists
    # ------------------------------------------------------------------
    INVOICE_DIR.mkdir(parents=True, exist_ok=True)

    invoice_id = data["invoice_id"]
    output_path = INVOICE_DIR / f"{invoice_id}.pdf"

    # ------------------------------------------------------------------
    # 2. Document setup
    # ------------------------------------------------------------------
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"Invoice {invoice_id}",
        author="AI-Umroh System",
    )

    styles = getSampleStyleSheet()
    story = []

    # ------------------------------------------------------------------
    # 3. Paragraph styles
    # ------------------------------------------------------------------
    style_company = ParagraphStyle(
        "company",
        fontSize=20,
        leading=24,
        textColor=COLOR_WHITE,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
    )
    style_tagline = ParagraphStyle(
        "tagline",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#A8D8A8"),
        fontName="Helvetica",
        alignment=TA_LEFT,
    )
    style_invoice_label = ParagraphStyle(
        "inv_label",
        fontSize=9,
        textColor=COLOR_ACCENT,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
    )
    style_invoice_number = ParagraphStyle(
        "inv_number",
        fontSize=18,
        leading=22,
        textColor=COLOR_WHITE,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
    )
    style_section_title = ParagraphStyle(
        "section_title",
        fontSize=9,
        textColor=COLOR_PRIMARY,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )
    style_body = ParagraphStyle(
        "body",
        fontSize=9,
        textColor=COLOR_TEXT,
        fontName="Helvetica",
        leading=14,
    )
    style_bold = ParagraphStyle(
        "bold",
        fontSize=9,
        textColor=COLOR_TEXT,
        fontName="Helvetica-Bold",
        leading=14,
    )
    style_footer = ParagraphStyle(
        "footer",
        fontSize=8,
        textColor=COLOR_FOOTER,
        fontName="Helvetica",
        alignment=TA_CENTER,
        leading=12,
    )
    style_amount_label = ParagraphStyle(
        "amount_label",
        fontSize=11,
        textColor=COLOR_TEXT,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
    )
    style_amount_value = ParagraphStyle(
        "amount_value",
        fontSize=14,
        textColor=COLOR_PRIMARY,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
    )
    style_note = ParagraphStyle(
        "note",
        fontSize=8,
        textColor=COLOR_FOOTER,
        fontName="Helvetica-Oblique",
        leading=11,
    )

    # ------------------------------------------------------------------
    # 4. Header banner  (dark green background)
    # ------------------------------------------------------------------
    header_left = [
        [Paragraph("🕌  AI-Umroh", style_company)],
        [Paragraph("Sistem Pemesanan Umroh Berbasis AI", style_tagline)],
    ]
    header_right = [
        [Paragraph("INVOICE", style_invoice_label)],
        [Paragraph(str(data["invoice_id"]), style_invoice_number)],
    ]

    header_table = Table(
        [[
            Table(header_left, colWidths=[None]),
            Table(header_right, colWidths=[None]),
        ]],
        colWidths=[(PAGE_W - 2 * MARGIN) * 0.55,
                   (PAGE_W - 2 * MARGIN) * 0.45],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_HEADER_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, -1), 14),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8 * mm))

    # ------------------------------------------------------------------
    # 5. Meta row  (Date | Status)
    # ------------------------------------------------------------------
    try:
        date_obj = datetime.strptime(str(data["date"]), "%Y-%m-%d")
        date_str = date_obj.strftime("%d %B %Y")
    except ValueError:
        date_str = str(data["date"])

    meta_table = Table(
        [[
            Paragraph(f"<b>Tanggal Invoice:</b>  {date_str}", style_body),
            Paragraph("<b>Status:</b>  <font color='#1B4332'><b>PENDING DP</b></font>", style_body),
        ]],
        colWidths=[(PAGE_W - 2 * MARGIN) * 0.5,
                   (PAGE_W - 2 * MARGIN) * 0.5],
    )
    meta_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ACCENT,
                            spaceAfter=5 * mm))

    # ------------------------------------------------------------------
    # 6. Pilgrim information
    # ------------------------------------------------------------------
    story.append(Paragraph("DATA JEMAAH", style_section_title))

    pilgrim_data = [
        ["Nama Lengkap", ":", data["fullname"]],
        ["Domisili", ":", data["domicile"]],
        ["Jumlah Pax", ":", f"{data['pax_count']} orang"],
    ]
    pilgrim_table = Table(
        pilgrim_data,
        colWidths=[45 * mm, 5 * mm, None],
    )
    pilgrim_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_TEXT),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(pilgrim_table)
    story.append(Spacer(1, 6 * mm))

    # ------------------------------------------------------------------
    # 7. Package detail table
    # ------------------------------------------------------------------
    story.append(Paragraph("DETAIL PAKET", style_section_title))

    # Derive DP per pax and base total from total & kode_unik
    try:
        total_tagihan = int(data["total_tagihan"])
        kode_unik = int(data["kode_unik"])
        pax_count = int(data["pax_count"])
        base_total = total_tagihan - kode_unik
        dp_per_pax = base_total // pax_count if pax_count else 0
    except (TypeError, ValueError, ZeroDivisionError):
        total_tagihan = data["total_tagihan"]
        kode_unik = data["kode_unik"]
        dp_per_pax = "-"
        base_total = "-"

    package_header = [
        Paragraph("Deskripsi", ParagraphStyle("th", fontSize=9, fontName="Helvetica-Bold",
                                               textColor=COLOR_WHITE)),
        Paragraph("Qty", ParagraphStyle("th", fontSize=9, fontName="Helvetica-Bold",
                                         textColor=COLOR_WHITE, alignment=TA_CENTER)),
        Paragraph("Harga / Pax", ParagraphStyle("th", fontSize=9, fontName="Helvetica-Bold",
                                                  textColor=COLOR_WHITE, alignment=TA_RIGHT)),
        Paragraph("Subtotal", ParagraphStyle("th", fontSize=9, fontName="Helvetica-Bold",
                                              textColor=COLOR_WHITE, alignment=TA_RIGHT)),
    ]
    package_rows = [
        package_header,
        [
            data["package_name"],
            str(pax_count),
            _fmt_idr(dp_per_pax),
            _fmt_idr(base_total),
        ],
        [
            "Kode Unik Pembayaran",
            "1",
            _fmt_idr(kode_unik),
            _fmt_idr(kode_unik),
        ],
    ]
    avail_w = PAGE_W - 2 * MARGIN
    package_table = Table(
        package_rows,
        colWidths=[avail_w * 0.42, avail_w * 0.10, avail_w * 0.24, avail_w * 0.24],
    )
    package_table.setStyle(TableStyle([
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        # Alternating rows
        ("BACKGROUND", (0, 1), (-1, 1), COLOR_LIGHT_GREEN),
        ("BACKGROUND", (0, 2), (-1, 2), COLOR_WHITE),
        # All rows
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), COLOR_TEXT),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CED4DA")),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_PRIMARY),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(package_table)
    story.append(Spacer(1, 4 * mm))

    # ------------------------------------------------------------------
    # 8. Total amount box
    # ------------------------------------------------------------------
    total_table = Table(
        [[
            Paragraph("TOTAL YANG HARUS DIBAYAR", style_amount_label),
            Paragraph(_fmt_idr(total_tagihan), style_amount_value),
        ]],
        colWidths=[avail_w * 0.55, avail_w * 0.45],
    )
    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_LIGHT_GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (0, -1), 12),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 12),
        ("BOX", (0, 0), (-1, -1), 1.5, COLOR_PRIMARY),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 6 * mm))

    # ------------------------------------------------------------------
    # 9. Payment information box
    # ------------------------------------------------------------------
    story.append(Paragraph("INFORMASI PEMBAYARAN", style_section_title))

    payment_data = [
        ["Bank", ":", data["bank_name"]],
        ["Nomor Rekening", ":", data["account_number"]],
        ["Atas Nama", ":", data["account_name"]],
        ["Nominal Transfer", ":",
         f"{_fmt_idr(total_tagihan)}  "
         f"<font color='#1B4332'><b>(termasuk kode unik {kode_unik})</b></font>"],
    ]
    payment_table = Table(
        payment_data,
        colWidths=[45 * mm, 5 * mm, None],
    )
    payment_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_TEXT),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    payment_wrapper = Table(
        [[payment_table]],
        colWidths=[avail_w],
    )
    payment_wrapper.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8E7")),
        ("BOX", (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(payment_wrapper)
    story.append(Spacer(1, 4 * mm))

    # Important note about unique code
    story.append(Paragraph(
        "⚠️  Mohon transfer sesuai nominal di atas <b>termasuk kode unik</b> agar "
        "verifikasi pembayaran dapat dilakukan secara otomatis.",
        style_note,
    ))
    story.append(Spacer(1, 8 * mm))

    # ------------------------------------------------------------------
    # 10. Steps / instructions
    # ------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CED4DA"),
                            spaceAfter=4 * mm))
    steps = [
        "1.  Lakukan transfer sesuai nominal di atas ke rekening yang tertera.",
        "2.  Foto / screenshot bukti transfer Anda.",
        "3.  Kirimkan foto bukti transfer melalui WhatsApp ke nomor yang sama.",
        "4.  Tim kami akan memverifikasi pembayaran dalam 1×24 jam kerja.",
    ]
    story.append(Paragraph("<b>LANGKAH SELANJUTNYA</b>", style_section_title))
    for step in steps:
        story.append(Paragraph(step, style_body))
    story.append(Spacer(1, 8 * mm))

    # ------------------------------------------------------------------
    # 11. Footer
    # ------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ACCENT,
                            spaceAfter=4 * mm))
    story.append(Paragraph(
        "Dokumen ini digenerate secara otomatis oleh Sistem AI-Umroh  •  "
        "Mohon simpan invoice ini sebagai bukti pemesanan Anda.",
        style_footer,
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "Jika ada pertanyaan, balas pesan WhatsApp Anda atau hubungi tim kami.",
        style_footer,
    ))

    # ------------------------------------------------------------------
    # 12. Build PDF
    # ------------------------------------------------------------------
    doc.build(story)

    return str(output_path.resolve())


# ---------------------------------------------------------------------------
# __main__  — quick test with dummy data
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    dummy = {
        "invoice_id": "INV-UMROH-9999",
        "date": "2026-05-21",
        "fullname": "Budi Santoso",
        "domicile": "Surabaya, Jawa Timur",
        "pax_count": 2,
        "package_name": "Paket Economy 9 Hari (Ramadhan)",
        "total_tagihan": 10_000_412,   # 2 pax × 5_000_000 + kode_unik 412
        "kode_unik": 412,
        "bank_name": "Bank Syariah Indonesia (BSI)",
        "account_number": "7123456789",
        "account_name": "PT Berkah Perjalanan Suci",
    }

    path = generate_invoice_pdf(dummy)
    print(f"[OK] Invoice berhasil dibuat: {path}")
