"""
PDF color palette, constants, and paragraph styles.
All visual design tokens live here — import from this module only.
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from pathlib import Path

# ---------------------------------------------------------------------------
# Color palette (Islamic green / gold theme)
# ---------------------------------------------------------------------------
COLOR_PRIMARY      = colors.HexColor("#1B4332")   # deep Islamic green
COLOR_ACCENT       = colors.HexColor("#D4A017")   # warm gold
COLOR_LIGHT_GREEN  = colors.HexColor("#D8F3DC")   # pale mint for row fill
COLOR_HEADER_BG    = colors.HexColor("#1B4332")
COLOR_FOOTER       = colors.HexColor("#6C757D")
COLOR_TEXT         = colors.HexColor("#212529")
COLOR_WHITE        = colors.white

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
INVOICE_DIR = Path(__file__).resolve().parent.parent / "static" / "invoices"
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------
STYLE_COMPANY = ParagraphStyle(
    "company", fontSize=20, leading=24,
    textColor=COLOR_WHITE, fontName="Helvetica-Bold", alignment=TA_LEFT,
)
STYLE_TAGLINE = ParagraphStyle(
    "tagline", fontSize=9, leading=12,
    textColor=colors.HexColor("#A8D8A8"), fontName="Helvetica", alignment=TA_LEFT,
)
STYLE_INV_LABEL = ParagraphStyle(
    "inv_label", fontSize=9,
    textColor=COLOR_ACCENT, fontName="Helvetica-Bold", alignment=TA_RIGHT,
)
STYLE_INV_NUMBER = ParagraphStyle(
    "inv_number", fontSize=18, leading=22,
    textColor=COLOR_WHITE, fontName="Helvetica-Bold", alignment=TA_RIGHT,
)
STYLE_SECTION_TITLE = ParagraphStyle(
    "section_title", fontSize=9,
    textColor=COLOR_PRIMARY, fontName="Helvetica-Bold", spaceAfter=4,
)
STYLE_BODY = ParagraphStyle(
    "body", fontSize=9, textColor=COLOR_TEXT, fontName="Helvetica", leading=14,
)
STYLE_BOLD = ParagraphStyle(
    "bold", fontSize=9, textColor=COLOR_TEXT, fontName="Helvetica-Bold", leading=14,
)
STYLE_FOOTER = ParagraphStyle(
    "footer", fontSize=8, textColor=COLOR_FOOTER,
    fontName="Helvetica", alignment=TA_CENTER, leading=12,
)
STYLE_AMOUNT_LABEL = ParagraphStyle(
    "amount_label", fontSize=11,
    textColor=COLOR_TEXT, fontName="Helvetica-Bold", alignment=TA_RIGHT,
)
STYLE_AMOUNT_VALUE = ParagraphStyle(
    "amount_value", fontSize=14,
    textColor=COLOR_PRIMARY, fontName="Helvetica-Bold", alignment=TA_RIGHT,
)
STYLE_NOTE = ParagraphStyle(
    "note", fontSize=8, textColor=COLOR_FOOTER,
    fontName="Helvetica-Oblique", leading=11,
)
STYLE_TABLE_HEADER = ParagraphStyle(
    "th", fontSize=9, fontName="Helvetica-Bold",
    textColor=COLOR_WHITE, alignment=TA_RIGHT,
)


# ---------------------------------------------------------------------------
# Utility: IDR formatter
# ---------------------------------------------------------------------------
def fmt_idr(amount) -> str:
    """Return a human-readable IDR string e.g. 'Rp 5.000.000'."""
    try:
        return "Rp {:,.0f}".format(int(amount)).replace(",", ".")
    except (TypeError, ValueError):
        return str(amount)
