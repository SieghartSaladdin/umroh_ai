import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from ai_umroh.database.connection import Base

class Jemaah(Base):
    __tablename__ = "jemaah"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    whatsapp_number = Column(String, unique=True, index=True, nullable=False)
    nama_lengkap = Column(String, nullable=True)
    domisili = Column(String, nullable=True)
    status_pembayaran = Column(String, default="POTENTIAL", nullable=False)  # 'POTENTIAL', 'PENDING_DP', 'WAITING_VERIFY', 'PAID'

    # Relationships
    bookings = relationship("Booking", back_populates="jemaah", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Jemaah(whatsapp={self.whatsapp_number}, nama={self.nama_lengkap}, status={self.status_pembayaran})>"

class Booking(Base):
    __tablename__ = "booking"

    id = Column(String, primary_key=True)  # Custom formatted Invoice ID (e.g. INV-UMROH-1002)
    jemaah_id = Column(String, ForeignKey("jemaah.id", ondelete="CASCADE"), nullable=False)
    paket_nama = Column(String, nullable=False)  # 'Economy' or 'Premium'
    jumlah_pax = Column(Integer, nullable=False, default=1)
    total_tagihan = Column(Float, nullable=False)  # DP per pax * pax count + unique code
    kode_unik = Column(Integer, nullable=False)  # 3-digit random transaction code (001-999)
    bukti_transfer_url = Column(String, nullable=True)  # Path to stored screenshot proof

    # Relationships
    jemaah = relationship("Jemaah", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, total={self.total_tagihan}, code={self.kode_unik})>"
