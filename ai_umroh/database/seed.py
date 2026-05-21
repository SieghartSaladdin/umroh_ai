"""
seed.py — Database initializer and seed data script.

Usage:
    python -m ai_umroh.database.seed
    (or)
    python ai_umroh/database/seed.py

This script:
1. Calls Base.metadata.create_all(engine) to create all SQLite tables.
2. Inserts one dummy Jemaah record with whatsapp_number='6281234567890'
   if it does not already exist.
"""

import sys
import os

# Ensure the project root is on the Python path when run directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai_umroh.database.connection import Base, engine, SessionLocal
from ai_umroh.database.models import Jemaah  # noqa: F401 — registers model with Base
from ai_umroh.database.models import Booking  # noqa: F401 — registers model with Base
from ai_umroh.utils.logger import get_logger

logger = get_logger("database.seed")

DUMMY_WHATSAPP = "6281234567890"


def create_tables() -> None:
    """Create all tables defined in Base metadata."""
    logger.info("Creating all database tables via Base.metadata.create_all(engine) …")
    Base.metadata.create_all(engine)
    logger.info("All tables created successfully.")


def seed_dummy_jemaah() -> None:
    """Insert a dummy Jemaah record if it does not already exist."""
    db = SessionLocal()
    try:
        existing = db.query(Jemaah).filter(
            Jemaah.whatsapp_number == DUMMY_WHATSAPP
        ).first()

        if existing:
            logger.info(
                f"Dummy Jemaah with whatsapp_number='{DUMMY_WHATSAPP}' already exists "
                f"(id={existing.id}). Skipping insert."
            )
            print(f"[SEED] Dummy Jemaah already exists: {existing}")
            return

        dummy = Jemaah(
            whatsapp_number=DUMMY_WHATSAPP,
            nama_lengkap="Dummy Jemaah",
            domisili="Jakarta",
            status_pembayaran="POTENTIAL",
        )
        db.add(dummy)
        db.commit()
        db.refresh(dummy)
        logger.info(
            f"Inserted dummy Jemaah: id={dummy.id}, whatsapp={dummy.whatsapp_number}"
        )
        print(f"[SEED] Inserted dummy Jemaah: {dummy}")
    except Exception as exc:
        db.rollback()
        logger.error(f"Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed_dummy_jemaah()
    print("[SEED] Database seeding completed.")
