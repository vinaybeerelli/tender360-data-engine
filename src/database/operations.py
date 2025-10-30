"""
Database CRUD operations
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from .models import Tender, TenderDetail, Document, ExtractedField, ScrapeLog
from src.utils.logger import log
from src.utils.exceptions import DatabaseException


def create_tender(db: Session, tender_data: dict) -> Tender:
    """
    Create a new tender record.

    Args:
        db: Database session
        tender_data: Dictionary with tender information

    Returns:
        Created Tender object
    """
    try:
        tender = Tender(**tender_data)
        db.add(tender)
        db.commit()
        db.refresh(tender)
        log.info(f"Created tender: {tender.tender_id}")
        return tender
    except Exception as e:
        db.rollback()
        log.error(f"Failed to create tender: {e}")
        raise DatabaseException(f"Failed to create tender: {e}")


def get_tender(db: Session, tender_id: str) -> Optional[Tender]:
    """
    Get tender by ID.

    Args:
        db: Database session
        tender_id: Tender ID

    Returns:
        Tender object or None
    """
    return db.query(Tender).filter(Tender.tender_id == tender_id).first()


def update_tender(db: Session, tender_id: str, update_data: dict) -> Tender:
    """
    Update tender record.

    Args:
        db: Database session
        tender_id: Tender ID
        update_data: Dictionary with fields to update

    Returns:
        Updated Tender object
    """
    tender = get_tender(db, tender_id)
    if not tender:
        raise DatabaseException(f"Tender not found: {tender_id}")

    for key, value in update_data.items():
        setattr(tender, key, value)

    db.commit()
    db.refresh(tender)
    log.info(f"Updated tender: {tender_id}")
    return tender


def save_tender_details(
    db: Session, tender_id: str, details_data: dict
) -> TenderDetail:
    """
    Save tender detail information.

    Args:
        db: Database session
        tender_id: Tender ID
        details_data: Dictionary with detail information

    Returns:
        Created TenderDetail object
    """
    try:
        details_data["tender_id"] = tender_id
        details = TenderDetail(**details_data)
        db.add(details)
        db.commit()
        db.refresh(details)
        log.info(f"Saved details for tender: {tender_id}")
        return details
    except Exception as e:
        db.rollback()
        log.error(f"Failed to save tender details: {e}")
        raise DatabaseException(f"Failed to save tender details: {e}")


def save_document(db: Session, tender_id: str, document_data: dict) -> Document:
    """
    Save document metadata.

    Args:
        db: Database session
        tender_id: Tender ID
        document_data: Dictionary with document information

    Returns:
        Created Document object
    """
    try:
        document_data["tender_id"] = tender_id
        document = Document(**document_data)
        db.add(document)
        db.commit()
        db.refresh(document)
        log.info(f"Saved document: {document.filename}")
        return document
    except Exception as e:
        db.rollback()
        log.error(f"Failed to save document: {e}")
        raise DatabaseException(f"Failed to save document: {e}")


def get_pending_downloads(db: Session) -> List[Document]:
    """
    Get documents pending download.

    Args:
        db: Database session

    Returns:
        List of Document objects with status PENDING
    """
    return db.query(Document).filter(Document.download_status == "PENDING").all()


def save_extracted_field(
    db: Session, tender_id: str, document_id: int, field_data: dict
) -> ExtractedField:
    """
    Save extracted field from document.

    Args:
        db: Database session
        tender_id: Tender ID
        document_id: Document ID
        field_data: Dictionary with field information

    Returns:
        Created ExtractedField object
    """
    try:
        field_data["tender_id"] = tender_id
        field_data["document_id"] = document_id
        field = ExtractedField(**field_data)
        db.add(field)
        db.commit()
        db.refresh(field)
        return field
    except Exception as e:
        db.rollback()
        log.error(f"Failed to save extracted field: {e}")
        raise DatabaseException(f"Failed to save extracted field: {e}")


def log_scrape_run(db: Session, log_data: dict) -> ScrapeLog:
    """
    Log scraping session.

    Args:
        db: Database session
        log_data: Dictionary with log information

    Returns:
        Created ScrapeLog object
    """
    try:
        scrape_log = ScrapeLog(**log_data)
        db.add(scrape_log)
        db.commit()
        db.refresh(scrape_log)
        return scrape_log
    except Exception as e:
        db.rollback()
        log.error(f"Failed to log scrape run: {e}")
        raise DatabaseException(f"Failed to log scrape run: {e}")


def get_tenders_by_department(db: Session, department: str) -> List[Tender]:
    """
    Get all tenders for a specific department.

    Args:
        db: Database session
        department: Department name

    Returns:
        List of Tender objects
    """
    return db.query(Tender).filter(Tender.department == department).all()


def get_tenders_by_date_range(
    db: Session, start_date: str, end_date: str
) -> List[Tender]:
    """
    Get tenders published within a date range.

    Args:
        db: Database session
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)

    Returns:
        List of Tender objects
    """
    return (
        db.query(Tender)
        .filter(Tender.published_date >= start_date, Tender.published_date <= end_date)
        .all()
    )


def get_documents_by_status(db: Session, status: str) -> List[Document]:
    """
    Get documents by download status.

    Args:
        db: Database session
        status: Download status (PENDING, DOWNLOADING, DOWNLOADED, FAILED)

    Returns:
        List of Document objects
    """
    return db.query(Document).filter(Document.download_status == status).all()


def get_extracted_fields_by_tender(db: Session, tender_id: str) -> List[ExtractedField]:
    """
    Get all extracted fields for a specific tender.

    Args:
        db: Database session
        tender_id: Tender ID

    Returns:
        List of ExtractedField objects
    """
    return db.query(ExtractedField).filter(ExtractedField.tender_id == tender_id).all()


def get_scrape_logs_by_status(db: Session, status: str) -> List[ScrapeLog]:
    """
    Get scrape logs by status.

    Args:
        db: Database session
        status: Scrape status (SUCCESS, PARTIAL, FAILED)

    Returns:
        List of ScrapeLog objects
    """
    return db.query(ScrapeLog).filter(ScrapeLog.status == status).all()
