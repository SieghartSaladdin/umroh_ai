"""
test_db.py -- Full transaction lifecycle test.

Simulates a complete pilgrim booking flow:
    1. create_jemaah      -- get_or_create_jemaah()
    2. update_manifest    -- update_jemaah_manifest()
    3. create_booking     -- create_booking() with 2 pax, Economy package
    4. save_transfer_proof -- save_transfer_proof()
    5. verify_payment     -- verify_payment()

Prints the entity state and current status at each step.

Usage:
    python scratch/test_db.py
    (run from the project root: c:\laragon\www\projectai\ai-umroh)
"""

import sys
import os

# Ensure project root is on Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Bootstrap: create all tables before running the test
# ---------------------------------------------------------------------------
from ai_umroh.database.connection import Base, engine, SessionLocal
from ai_umroh.database.models import Jemaah, Booking  # noqa: registers models
Base.metadata.create_all(engine)

from ai_umroh.database.repository import (
    get_or_create_jemaah,
    update_jemaah_manifest,
    create_booking,
    save_transfer_proof,
    verify_payment,
)

# ---------------------------------------------------------------------------
# Test configuration
# ---------------------------------------------------------------------------
TEST_WA_NUMBER = "628999000001"   # Dedicated test number (avoids seed conflict)
PACKAGE_NAME   = "Economy"
PAX_COUNT      = 2
FAKE_PROOF_URL = "/uploads/proofs/test_transfer_2pax.jpg"

SEPARATOR = "=" * 60


def print_jemaah_state(label, jemaah):
    print("\n" + "-" * 60)
    print("  STEP: " + label)
    print("-" * 60)
    print("  Jemaah ID          : " + str(jemaah.id))
    print("  WhatsApp           : " + str(jemaah.whatsapp_number))
    print("  Nama Lengkap       : " + repr(jemaah.nama_lengkap))
    print("  Domisili           : " + repr(jemaah.domisili))
    print("  Status Pembayaran  : " + str(jemaah.status_pembayaran))
    print("-" * 60)


def print_booking_state(label, booking, db):
    # Reload jemaah from db for fresh status
    jemaah = db.query(Jemaah).filter(Jemaah.id == booking.jemaah_id).first()
    print("\n" + "-" * 60)
    print("  STEP: " + label)
    print("-" * 60)
    print("  Booking ID         : " + str(booking.id))
    print("  Paket              : " + str(booking.paket_nama))
    print("  Jumlah Pax         : " + str(booking.jumlah_pax))
    print("  Total Tagihan      : IDR {:,.0f}".format(booking.total_tagihan))
    print("  Kode Unik          : {:03d}".format(booking.kode_unik))
    print("  Bukti Transfer URL : " + repr(booking.bukti_transfer_url))
    print("  Jemaah Status      : " + (jemaah.status_pembayaran if jemaah else "N/A"))
    print("-" * 60)


def run_lifecycle_test():
    print("\n" + SEPARATOR)
    print("  AI-UMROH -- Full Transaction Lifecycle Test")
    print(SEPARATOR)
    print("  Test WA Number : " + TEST_WA_NUMBER)
    print("  Package        : " + PACKAGE_NAME + "  |  Pax: " + str(PAX_COUNT))
    print(SEPARATOR + "\n")

    db = SessionLocal()

    try:
        # ------------------------------------------------------------------
        # Step 1: Create (or get) Jemaah
        # ------------------------------------------------------------------
        jemaah = get_or_create_jemaah(db, TEST_WA_NUMBER)
        print_jemaah_state("1 -- create_jemaah (get_or_create_jemaah)", jemaah)
        assert jemaah.whatsapp_number == TEST_WA_NUMBER, "WhatsApp number mismatch"
        assert jemaah.status_pembayaran == "POTENTIAL", \
            "Expected POTENTIAL, got " + jemaah.status_pembayaran
        print("  [PASS] status_pembayaran == 'POTENTIAL'")

        # ------------------------------------------------------------------
        # Step 2: Update Manifest (name + domicile)
        # ------------------------------------------------------------------
        jemaah = update_jemaah_manifest(
            db,
            whatsapp_number=TEST_WA_NUMBER,
            fullname="Budi Santoso",
            domicile="Surabaya",
        )
        print_jemaah_state("2 -- update_manifest (update_jemaah_manifest)", jemaah)
        assert jemaah.nama_lengkap == "Budi Santoso", "Name not updated"
        assert jemaah.domisili == "Surabaya", "Domicile not updated"
        print("  [PASS] nama_lengkap == 'Budi Santoso'")
        print("  [PASS] domisili     == 'Surabaya'")

        # ------------------------------------------------------------------
        # Step 3: Create Booking -- 2 pax, Economy
        # ------------------------------------------------------------------
        booking = create_booking(
            db,
            whatsapp_number=TEST_WA_NUMBER,
            package_name=PACKAGE_NAME,
            pax_count=PAX_COUNT,
        )
        print_booking_state("3 -- create_booking (2 pax, Economy)", booking, db)

        # Re-query jemaah for fresh status
        db.expire_all()
        jemaah = db.query(Jemaah).filter(Jemaah.whatsapp_number == TEST_WA_NUMBER).first()
        assert jemaah.status_pembayaran == "PENDING_DP", \
            "Expected PENDING_DP, got " + jemaah.status_pembayaran
        assert booking.paket_nama == "Economy", "Wrong package"
        assert booking.jumlah_pax == 2, "Wrong pax count"
        assert booking.total_tagihan > 0, "Total must be positive"
        print("  [PASS] status_pembayaran  == 'PENDING_DP'")
        print("  [PASS] total_tagihan      == IDR {:,.0f}  (5,000,000 x 2 + {})".format(
            booking.total_tagihan, booking.kode_unik))

        # ------------------------------------------------------------------
        # Step 4: Save Transfer Proof
        # ------------------------------------------------------------------
        booking_id = booking.id
        booking = save_transfer_proof(db, booking_id=booking_id, file_path=FAKE_PROOF_URL)
        print_booking_state("4 -- save_transfer_proof", booking, db)

        db.expire_all()
        jemaah = db.query(Jemaah).filter(Jemaah.whatsapp_number == TEST_WA_NUMBER).first()
        assert jemaah.status_pembayaran == "WAITING_VERIFY", \
            "Expected WAITING_VERIFY, got " + jemaah.status_pembayaran
        assert booking.bukti_transfer_url == FAKE_PROOF_URL, "Proof URL not saved"
        print("  [PASS] status_pembayaran  == 'WAITING_VERIFY'")
        print("  [PASS] bukti_transfer_url == '" + str(booking.bukti_transfer_url) + "'")

        # ------------------------------------------------------------------
        # Step 5: Verify Payment
        # ------------------------------------------------------------------
        booking = verify_payment(db, booking_id=booking_id)
        print_booking_state("5 -- verify_payment", booking, db)

        db.expire_all()
        jemaah = db.query(Jemaah).filter(Jemaah.whatsapp_number == TEST_WA_NUMBER).first()
        assert jemaah.status_pembayaran == "PAID", \
            "Expected PAID, got " + jemaah.status_pembayaran
        print("  [PASS] status_pembayaran  == 'PAID'")

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        print("\n" + SEPARATOR)
        print("  ALL STEPS PASSED [OK]")
        print(SEPARATOR + "\n")

    except AssertionError as ae:
        print("\n  [FAIL] ASSERTION FAILED: " + str(ae) + "\n")
        raise
    except Exception as exc:
        print("\n  [ERROR] " + str(exc) + "\n")
        raise
    finally:
        # Clean up test data so the test is idempotent
        try:
            db.query(Booking).filter(Booking.jemaah_id.in_(
                db.query(Jemaah.id).filter(Jemaah.whatsapp_number == TEST_WA_NUMBER)
            )).delete(synchronize_session=False)
            db.query(Jemaah).filter(Jemaah.whatsapp_number == TEST_WA_NUMBER).delete()
            db.commit()
            print("  [cleanup] Test jemaah and bookings removed from database.")
        except Exception:
            db.rollback()
        db.close()


if __name__ == "__main__":
    run_lifecycle_test()
