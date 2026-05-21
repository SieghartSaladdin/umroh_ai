import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from ai_umroh.database.models import Jemaah, Booking
from ai_umroh.utils.logger import get_logger

logger = get_logger("database.repository")

# Configuration constants
DP_PER_PAX = 5000000.0  # IDR 5,000,000

def get_or_create_jemaah(db: Session, whatsapp_number: str) -> Jemaah:
    """
    Fetches an existing pilgrim profile by WhatsApp number or creates a new prospect pilgrim.
    """
    try:
        jemaah = db.query(Jemaah).filter(Jemaah.whatsapp_number == whatsapp_number).first()
        if not jemaah:
            logger.info(f"Creating new pilgrim record for WhatsApp number: {whatsapp_number}")
            jemaah = Jemaah(whatsapp_number=whatsapp_number, status_pembayaran="POTENTIAL")
            db.add(jemaah)
            db.commit()
            db.refresh(jemaah)
        return jemaah
    except Exception as e:
        db.rollback()
        logger.error(f"Error in get_or_create_jemaah for {whatsapp_number}: {str(e)}")
        raise e

def update_jemaah_manifest(db: Session, whatsapp_number: str, fullname: str, domicile: str) -> Jemaah:
    """
    Updates the manifest details of a pilgrim.
    """
    try:
        jemaah = get_or_create_jemaah(db, whatsapp_number)
        logger.info(f"Updating manifest for {whatsapp_number}: name={fullname}, domicile={domicile}")
        jemaah.nama_lengkap = fullname
        jemaah.domisili = domicile
        db.commit()
        db.refresh(jemaah)
        return jemaah
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating manifest for {whatsapp_number}: {str(e)}")
        raise e

def generate_invoice_id(db: Session) -> str:
    """
    Generates a unique incremental Invoice ID, starting from INV-UMROH-1001.
    """
    try:
        # Get total number of bookings or max digit to calculate sequence
        last_booking = db.query(Booking).order_by(Booking.id.desc()).first()
        if not last_booking:
            next_num = 1001
        else:
            try:
                # Extract numerical suffix from INV-UMROH-XXXX
                parts = last_booking.id.split("-")
                last_num = int(parts[-1])
                next_num = last_num + 1
            except ValueError:
                # Fallback if ID structure is modified
                count = db.query(Booking).count()
                next_num = 1001 + count
        
        return f"INV-UMROH-{next_num}"
    except Exception as e:
        logger.error(f"Error generating Invoice ID: {str(e)}")
        return f"INV-UMROH-{random.randint(10000, 99999)}"

def create_booking(db: Session, whatsapp_number: str, package_name: str, pax_count: int, unique_code: int = None) -> Booking:
    """
    Registers a new booking transaction, calculates total DP including unique code,
    and updates pilgrim payment status to PENDING_DP.
    """
    try:
        jemaah = get_or_create_jemaah(db, whatsapp_number)
        
        # Calculate booking charges
        if unique_code is None:
            unique_code = random.randint(1, 999)  # 3-digit random unique code
            
        total_dp = (DP_PER_PAX * pax_count) + unique_code
        invoice_id = generate_invoice_id(db)
        
        logger.info(f"Creating booking {invoice_id} for {whatsapp_number}: Total DP={total_dp} (code={unique_code})")
        
        booking = Booking(
            id=invoice_id,
            jemaah_id=jemaah.id,
            paket_nama=package_name,
            jumlah_pax=pax_count,
            total_tagihan=total_dp,
            kode_unik=unique_code
        )
        
        jemaah.status_pembayaran = "PENDING_DP"
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating booking for {whatsapp_number}: {str(e)}")
        raise e

def save_transfer_proof(db: Session, booking_id: str, file_path: str) -> Booking:
    """
    Saves the transfer proof media location and sets both booking and pilgrim statuses to WAITING_VERIFY.
    """
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found.")
            
        logger.info(f"Saving transfer proof for booking {booking_id}: path={file_path}")
        booking.bukti_transfer_url = file_path
        
        # Update Jemaah payment status to WAITING_VERIFY
        booking.jemaah.status_pembayaran = "WAITING_VERIFY"
        
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving transfer proof for booking {booking_id}: {str(e)}")
        raise e

def verify_payment(db: Session, booking_id: str) -> Booking:
    """
    Confirms receipt of funds, updating pilgrim status to PAID (Mute release trigger).
    """
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found.")
            
        logger.info(f"Verifying payment success for booking {booking_id}")
        booking.jemaah.status_pembayaran = "PAID"
        
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        logger.error(f"Error verifying payment for booking {booking_id}: {str(e)}")
        raise e
