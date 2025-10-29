"""
Database models for Tender Scraper Engine
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from .connection import Base


class Tender(Base):
    """Basic tender information."""
    __tablename__ = "tenders"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), unique=True, nullable=False, index=True)
    department = Column(String(200))
    notice_number = Column(String(100))
    category = Column(String(100))
    work_name = Column(Text)
    tender_value = Column(String(50))
    published_date = Column(String(50), index=True)
    bid_start_date = Column(String(50))
    bid_close_date = Column(String(50), index=True)
    detail_url = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    details = relationship("TenderDetail", back_populates="tender", uselist=False)
    documents = relationship("Document", back_populates="tender")
    extracted_fields = relationship("ExtractedField", back_populates="tender")
    
    def __repr__(self):
        return f"<Tender(id={self.tender_id}, work={self.work_name[:50]})>"


class TenderDetail(Base):
    """Extended tender information."""
    __tablename__ = "tender_details"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), ForeignKey("tenders.tender_id"), unique=True)
    eligibility = Column(Text)
    general_terms = Column(Text)
    legal_terms = Column(Text)
    technical_terms = Column(Text)
    submission_procedure = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tender = relationship("Tender", back_populates="details")
    
    def __repr__(self):
        return f"<TenderDetail(tender_id={self.tender_id})>"


class Document(Base):
    """Document metadata."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), ForeignKey("tenders.tender_id"))
    filename = Column(String(255))
    file_path = Column(Text)
    file_type = Column(String(50))
    file_size = Column(Integer)
    download_url = Column(Text)
    download_status = Column(String(50), default="PENDING")  # PENDING, DOWNLOADING, DOWNLOADED, FAILED
    downloaded_at = Column(DateTime)
    
    # Relationships
    tender = relationship("Tender", back_populates="documents")
    extracted_fields = relationship("ExtractedField", back_populates="document")
    
    def __repr__(self):
        return f"<Document(filename={self.filename}, status={self.download_status})>"


class ExtractedField(Base):
    """Parsed data from documents."""
    __tablename__ = "extracted_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), ForeignKey("tenders.tender_id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    field_name = Column(String(100))  # e.g., "emd", "tender_fee", "deadline"
    field_value = Column(Text)
    field_type = Column(String(50))  # e.g., "currency", "date", "text"
    extraction_method = Column(String(50))  # e.g., "regex", "table", "manual"
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tender = relationship("Tender", back_populates="extracted_fields")
    document = relationship("Document", back_populates="extracted_fields")
    
    def __repr__(self):
        return f"<ExtractedField(name={self.field_name}, value={self.field_value})>"


class ScrapeLog(Base):
    """Audit trail for scraping sessions."""
    __tablename__ = "scrape_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_date = Column(DateTime, default=datetime.utcnow, index=True)
    method = Column(String(50))  # api, selenium, hybrid
    tenders_found = Column(Integer)
    tenders_scraped = Column(Integer)
    errors = Column(Integer)
    status = Column(String(50))  # SUCCESS, PARTIAL, FAILED
    notes = Column(Text)
    
    def __repr__(self):
        return f"<ScrapeLog(date={self.run_date}, scraped={self.tenders_scraped}/{self.tenders_found})>"

