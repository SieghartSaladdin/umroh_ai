"""
PDF Invoice Generator — public entry point.

Delegates layout and styling to:
  - pdf_styles.py   : colour palette, constants, paragraph styles
  - pdf_sections.py : individual section builders

This file stays lean: only document setup and section assembly.
"""

from pathlib import Path
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4

from ai_umroh.utils.pdf_styles import INVOICE_DIR, MARGIN
from ai_umroh.utils.pdf_sections import (
    build_footer,
    build_header,
    build_meta_row,
    build_package_table,
    build_payment_section,
    build_pilgrim_section,
    build_total_box,
)


def generate_invoice_pdf(data: dict) -> str:
    """
    Generate a professional Umroh booking invoice PDF.

    Parameters
    ----------
    data : dict
        invoice_id, date, fullname, domicile, pax_count,
        package_name, total_tagihan, kode_unik,
        bank_name, account_number, account_name

    Returns
    -------
    str  — absolute path of the saved PDF file.
    """
    INVOICE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = INVOICE_DIR / f"{data['invoice_id']}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=MARGIN, leftMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"Invoice {data['invoice_id']}",
        author="AI-Umroh System",
    )

    total     = int(data["total_tagihan"])
    kode_unik = int(data["kode_unik"])

    story = [
        *build_header(data),
        *build_meta_row(data),
        *build_pilgrim_section(data),
        *build_package_table(data),
        *build_total_box(total),
        *build_payment_section(data, total, kode_unik),
        *build_footer(),
    ]

    doc.build(story)
    return str(output_path.resolve())


# ---------------------------------------------------------------------------
# Quick test — run: python -m ai_umroh.utils.pdf_generator
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    dummy = {
        "invoice_id":     "INV-UMROH-9999",
        "date":           "2026-05-21",
        "fullname":       "Budi Santoso",
        "domicile":       "Surabaya, Jawa Timur",
        "pax_count":      2,
        "package_name":   "Paket Economy 9 Hari (Ramadhan)",
        "total_tagihan":  10_000_412,
        "kode_unik":      412,
        "bank_name":      "Bank Syariah Indonesia (BSI)",
        "account_number": "7123456789",
        "account_name":   "PT Berkah Perjalanan Suci",
    }
    path = generate_invoice_pdf(dummy)
    print(f"[OK] Invoice berhasil dibuat: {path}")
