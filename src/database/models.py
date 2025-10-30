"""
Database models for Tender Scraper Engine

This module defines the SQLAlchemy ORM models for the tender scraping system.

Relationships:
    - Tender ←→ TenderDetail: One-to-One (one tender has one detail record)
    - Tender → Document: One-to-Many (one tender has many documents)
    - Tender → ExtractedField: One-to-Many (one tender has many extracted fields)
    - Document → ExtractedField: One-to-Many (one document has many extracted fields)
    - ScrapeLog: Standalone audit log table with no relationships
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from .connection import Base


class Tender(Base):
    """
    Basic tender information.
    
    Represents the core tender data scraped from the tender portal.
    
    Relationships:
        - details (TenderDetail): One-to-One relationship with extended tender information
        - documents (List[Document]): One-to-Many relationship with associated documents
        - extracted_fields (List[ExtractedField]): One-to-Many relationship with parsed data
    """
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
    
    # Relationships with cascade options for data integrity
    # One-to-One: When a tender is deleted, its detail should also be deleted
    details = relationship(
        "TenderDetail", 
        back_populates="tender", 
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # One-to-Many: When a tender is deleted, all its documents should also be deleted
    documents = relationship(
        "Document", 
        back_populates="tender",
        cascade="all, delete-orphan"
    )
    
    # One-to-Many: When a tender is deleted, all its extracted fields should also be deleted
    extracted_fields = relationship(
        "ExtractedField", 
        back_populates="tender",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Tender(id={self.tender_id}, work={self.work_name[:50]})>"


class TenderDetail(Base):
    """
    Extended tender information.
    
    Stores detailed information about a tender that is optional or fetched separately.
    Has a one-to-one relationship with the Tender model.
    
    Relationships:
        - tender (Tender): Many-to-One relationship back to the parent tender
    """
    __tablename__ = "tender_details"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), ForeignKey("tenders.tender_id"), unique=True, index=True)
    eligibility = Column(Text)
    general_terms = Column(Text)
    legal_terms = Column(Text)
    technical_terms = Column(Text)
    submission_procedure = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Many-to-One: Each detail belongs to exactly one tender
    tender = relationship("Tender", back_populates="details")
    
    def __repr__(self):
        return f"<TenderDetail(tender_id={self.tender_id})>"


class Document(Base):
    """
    Document metadata.
    
    Stores information about documents associated with tenders.
    Each document belongs to one tender and can have multiple extracted fields.
    
    Relationships:
        - tender (Tender): Many-to-One relationship back to the parent tender
        - extracted_fields (List[ExtractedField]): One-to-Many relationship with parsed data
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), ForeignKey("tenders.tender_id"), index=True)
    filename = Column(String(255))
    file_path = Column(Text)
    file_type = Column(String(50))
    file_size = Column(Integer)
    download_url = Column(Text)
    download_status = Column(String(50), default="PENDING")  # PENDING, DOWNLOADING, DOWNLOADED, FAILED
    downloaded_at = Column(DateTime)
    
    # Many-to-One: Each document belongs to exactly one tender
    tender = relationship("Tender", back_populates="documents")
    
    # One-to-Many: When a document is deleted, all its extracted fields should also be deleted
    extracted_fields = relationship(
        "ExtractedField", 
        back_populates="document",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Document(filename={self.filename}, status={self.download_status})>"


class ExtractedField(Base):
    """
    Parsed data from documents.
    
    Stores individual fields extracted from tender documents using various extraction methods.
    Each field belongs to both a tender and a document.
    
    Relationships:
        - tender (Tender): Many-to-One relationship back to the parent tender
        - document (Document): Many-to-One relationship back to the source document
    """
    __tablename__ = "extracted_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(100), ForeignKey("tenders.tender_id"), index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    field_name = Column(String(100))  # e.g., "emd", "tender_fee", "deadline"
    field_value = Column(Text)
    field_type = Column(String(50))  # e.g., "currency", "date", "text"
    extraction_method = Column(String(50))  # e.g., "regex", "table", "manual"
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    # Many-to-One: Each extracted field belongs to exactly one tender
    tender = relationship("Tender", back_populates="extracted_fields")
    
    # Many-to-One: Each extracted field belongs to exactly one document
    document = relationship("Document", back_populates="extracted_fields")
    
    def __repr__(self):
        return f"<ExtractedField(name={self.field_name}, value={self.field_value})>"


class ScrapeLog(Base):
    """
    Audit trail for scraping sessions.
    
    Standalone table that logs each scraping run for monitoring and debugging.
    Has no relationships with other tables as it's purely an audit log.
    """
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

