"""
PDF section builders — one function per invoice section.
Each function accepts data and returns ReportLab flowable elements.
"""

from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, Spacer, Table, TableStyle

from ai_umroh.utils.pdf_styles import (
    COLOR_ACCENT, COLOR_HEADER_BG, COLOR_LIGHT_GREEN, COLOR_PRIMARY,
    COLOR_TEXT, COLOR_WHITE, MARGIN, PAGE_W,
    STYLE_AMOUNT_LABEL, STYLE_AMOUNT_VALUE, STYLE_BODY, STYLE_COMPANY,
    STYLE_FOOTER, STYLE_INV_LABEL, STYLE_INV_NUMBER, STYLE_NOTE,
    STYLE_SECTION_TITLE, STYLE_TABLE_HEADER, STYLE_TAGLINE,
    fmt_idr,
)

_AVAIL_W = PAGE_W - 2 * MARGIN


def build_header(data: dict) -> list:
    """Returns the dark-green header banner with company name and invoice ID."""
    left = Table(
        [[Paragraph("🕌  AI-Umroh", STYLE_COMPANY)],
         [Paragraph("Sistem Pemesanan Umroh Berbasis AI", STYLE_TAGLINE)]],
        colWidths=[None],
    )
    right = Table(
        [[Paragraph("INVOICE", STYLE_INV_LABEL)],
         [Paragraph(str(data["invoice_id"]), STYLE_INV_NUMBER)]],
        colWidths=[None],
    )
    tbl = Table([[left, right]], colWidths=[_AVAIL_W * 0.55, _AVAIL_W * 0.45])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_HEADER_BG),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (0, -1), 14),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return [tbl, Spacer(1, 8 * mm)]


def build_meta_row(data: dict) -> list:
    """Returns invoice date + status row with gold divider."""
    try:
        date_str = datetime.strptime(str(data["date"]), "%Y-%m-%d").strftime("%d %B %Y")
    except ValueError:
        date_str = str(data["date"])

    tbl = Table(
        [[Paragraph(f"<b>Tanggal Invoice:</b>  {date_str}", STYLE_BODY),
          Paragraph("<b>Status:</b>  <font color='#1B4332'><b>PENDING DP</b></font>", STYLE_BODY)]],
        colWidths=[_AVAIL_W * 0.5, _AVAIL_W * 0.5],
    )
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN",         (1, 0), (1, 0),  "RIGHT"),
    ]))
    return [tbl, Spacer(1, 4 * mm),
            HRFlowable(width="100%", thickness=1, color=COLOR_ACCENT, spaceAfter=5 * mm)]


def build_pilgrim_section(data: dict) -> list:
    """Returns pilgrim manifest table (name, domicile, pax count)."""
    rows = [
        ["Nama Lengkap", ":", data["fullname"]],
        ["Domisili",     ":", data["domicile"]],
        ["Jumlah Pax",   ":", f"{data['pax_count']} orang"],
    ]
    tbl = Table(rows, colWidths=[45 * mm, 5 * mm, None])
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (2, 0), (2, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 0), (-1, -1), COLOR_TEXT),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return [Paragraph("DATA JEMAAH", STYLE_SECTION_TITLE), tbl, Spacer(1, 6 * mm)]


def build_package_table(data: dict) -> list:
    """Returns itemized fee breakdown table with unique code row."""
    total    = int(data["total_tagihan"])
    kode     = int(data["kode_unik"])
    pax      = int(data["pax_count"])
    base     = total - kode
    per_pax  = base // pax if pax else 0

    th = lambda txt: Paragraph(txt, STYLE_TABLE_HEADER)   # noqa: E731
    header = [th("Deskripsi"), th("Qty"), th("Harga / Pax"), th("Subtotal")]
    rows = [
        header,
        [data["package_name"], str(pax), fmt_idr(per_pax), fmt_idr(base)],
        ["Kode Unik Pembayaran", "1", fmt_idr(kode), fmt_idr(kode)],
    ]
    tbl = Table(rows, colWidths=[_AVAIL_W * 0.42, _AVAIL_W * 0.10,
                                  _AVAIL_W * 0.24, _AVAIL_W * 0.24])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_PRIMARY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), COLOR_WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND",    (0, 1), (-1, 1), COLOR_LIGHT_GREEN),
        ("BACKGROUND",    (0, 2), (-1, 2), COLOR_WHITE),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 1), (-1, -1), COLOR_TEXT),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN",         (1, 0), (1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#CED4DA")),
        ("BOX",           (0, 0), (-1, -1), 1, COLOR_PRIMARY),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return [Paragraph("DETAIL PAKET", STYLE_SECTION_TITLE), tbl, Spacer(1, 4 * mm)]


def build_total_box(total_tagihan: int) -> list:
    """Returns highlighted grand-total box."""
    tbl = Table(
        [[Paragraph("TOTAL YANG HARUS DIBAYAR", STYLE_AMOUNT_LABEL),
          Paragraph(fmt_idr(total_tagihan), STYLE_AMOUNT_VALUE)]],
        colWidths=[_AVAIL_W * 0.55, _AVAIL_W * 0.45],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), COLOR_LIGHT_GREEN),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (0, -1), 12),
        ("RIGHTPADDING",  (-1, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 1.5, COLOR_PRIMARY),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return [tbl, Spacer(1, 6 * mm)]


def build_payment_section(data: dict, total_tagihan: int, kode: int) -> list:
    """Returns gold-bordered bank transfer details card."""
    rows = [
        ["Bank",             ":", data["bank_name"]],
        ["Nomor Rekening",   ":", data["account_number"]],
        ["Atas Nama",        ":", data["account_name"]],
        ["Nominal Transfer", ":",
         f"{fmt_idr(total_tagihan)}  "
         f"<font color='#1B4332'><b>(termasuk kode unik {kode})</b></font>"],
    ]
    inner = Table(rows, colWidths=[45 * mm, 5 * mm, None])
    inner.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",      (2, 0), (2, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",     (0, 0), (-1, -1), COLOR_TEXT),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    wrapper = Table([[inner]], colWidths=[_AVAIL_W])
    wrapper.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FFF8E7")),
        ("BOX",           (0, 0), (-1, -1), 1, COLOR_ACCENT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    note = Paragraph(
        "⚠️  Mohon transfer sesuai nominal di atas <b>termasuk kode unik</b> agar "
        "verifikasi pembayaran dapat dilakukan secara otomatis.",
        STYLE_NOTE,
    )
    return [Paragraph("INFORMASI PEMBAYARAN", STYLE_SECTION_TITLE),
            wrapper, Spacer(1, 4 * mm), note, Spacer(1, 8 * mm)]


def build_footer() -> list:
    """Returns gold rule + legal footer block."""
    steps_title = Paragraph("<b>LANGKAH SELANJUTNYA</b>", STYLE_SECTION_TITLE)
    steps = [
        "1.  Lakukan transfer sesuai nominal di atas ke rekening yang tertera.",
        "2.  Foto / screenshot bukti transfer Anda.",
        "3.  Kirimkan foto bukti transfer melalui WhatsApp ke nomor yang sama.",
        "4.  Tim kami akan memverifikasi pembayaran dalam 1×24 jam kerja.",
    ]
    flowables = [
        HRFlowable(width="100%", thickness=0.5,
                   color=colors.HexColor("#CED4DA"), spaceAfter=4 * mm),
        steps_title,
        *[Paragraph(s, STYLE_BODY) for s in steps],
        Spacer(1, 8 * mm),
        HRFlowable(width="100%", thickness=1, color=COLOR_ACCENT, spaceAfter=4 * mm),
        Paragraph(
            "Dokumen ini digenerate secara otomatis oleh Sistem AI-Umroh  •  "
            "Mohon simpan invoice ini sebagai bukti pemesanan Anda.",
            STYLE_FOOTER,
        ),
        Spacer(1, 2 * mm),
        Paragraph(
            "Jika ada pertanyaan, balas pesan WhatsApp Anda atau hubungi tim kami.",
            STYLE_FOOTER,
        ),
    ]
    return flowables
