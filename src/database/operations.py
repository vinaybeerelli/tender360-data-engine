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


def save_tender_details(db: Session, tender_id: str, details_data: dict) -> TenderDetail:
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
        details_data['tender_id'] = tender_id
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
        document_data['tender_id'] = tender_id
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


def save_extracted_field(db: Session, tender_id: str, document_id: int, field_data: dict) -> ExtractedField:
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
        field_data['tender_id'] = tender_id
        field_data['document_id'] = document_id
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


# ===== Additional READ operations =====

def list_tenders(db: Session, skip: int = 0, limit: int = 100, 
                 department: Optional[str] = None,
                 category: Optional[str] = None) -> List[Tender]:
    """
    List tenders with optional filters.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        department: Optional filter by department
        category: Optional filter by category
        
    Returns:
        List of Tender objects
    """
    query = db.query(Tender)
    
    if department:
        query = query.filter(Tender.department == department)
    if category:
        query = query.filter(Tender.category == category)
    
    return query.offset(skip).limit(limit).all()


def get_tender_details(db: Session, tender_id: str) -> Optional[TenderDetail]:
    """
    Get tender details by tender ID.
    
    Args:
        db: Database session
        tender_id: Tender ID
        
    Returns:
        TenderDetail object or None
    """
    return db.query(TenderDetail).filter(TenderDetail.tender_id == tender_id).first()


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """
    Get document by ID.
    
    Args:
        db: Database session
        document_id: Document ID
        
    Returns:
        Document object or None
    """
    return db.query(Document).filter(Document.id == document_id).first()


def list_documents(db: Session, tender_id: Optional[str] = None, 
                   status: Optional[str] = None,
                   skip: int = 0, limit: int = 100) -> List[Document]:
    """
    List documents with optional filters.
    
    Args:
        db: Database session
        tender_id: Optional filter by tender ID
        status: Optional filter by download status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of Document objects
    """
    query = db.query(Document)
    
    if tender_id:
        query = query.filter(Document.tender_id == tender_id)
    if status:
        query = query.filter(Document.download_status == status)
    
    return query.offset(skip).limit(limit).all()


def get_extracted_field(db: Session, field_id: int) -> Optional[ExtractedField]:
    """
    Get extracted field by ID.
    
    Args:
        db: Database session
        field_id: Field ID
        
    Returns:
        ExtractedField object or None
    """
    return db.query(ExtractedField).filter(ExtractedField.id == field_id).first()


def list_extracted_fields(db: Session, tender_id: Optional[str] = None,
                          document_id: Optional[int] = None,
                          field_name: Optional[str] = None,
                          skip: int = 0, limit: int = 100) -> List[ExtractedField]:
    """
    List extracted fields with optional filters.
    
    Args:
        db: Database session
        tender_id: Optional filter by tender ID
        document_id: Optional filter by document ID
        field_name: Optional filter by field name
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ExtractedField objects
    """
    query = db.query(ExtractedField)
    
    if tender_id:
        query = query.filter(ExtractedField.tender_id == tender_id)
    if document_id:
        query = query.filter(ExtractedField.document_id == document_id)
    if field_name:
        query = query.filter(ExtractedField.field_name == field_name)
    
    return query.offset(skip).limit(limit).all()


def get_scrape_log(db: Session, log_id: int) -> Optional[ScrapeLog]:
    """
    Get scrape log by ID.
    
    Args:
        db: Database session
        log_id: Log ID
        
    Returns:
        ScrapeLog object or None
    """
    return db.query(ScrapeLog).filter(ScrapeLog.id == log_id).first()


def list_scrape_logs(db: Session, method: Optional[str] = None,
                     status: Optional[str] = None,
                     skip: int = 0, limit: int = 100) -> List[ScrapeLog]:
    """
    List scrape logs with optional filters.
    
    Args:
        db: Database session
        method: Optional filter by scraping method
        status: Optional filter by status
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of ScrapeLog objects
    """
    query = db.query(ScrapeLog)
    
    if method:
        query = query.filter(ScrapeLog.method == method)
    if status:
        query = query.filter(ScrapeLog.status == status)
    
    return query.order_by(ScrapeLog.run_date.desc()).offset(skip).limit(limit).all()


# ===== Additional UPDATE operations =====

def update_tender_details(db: Session, tender_id: str, update_data: dict) -> TenderDetail:
    """
    Update tender details.
    
    Args:
        db: Database session
        tender_id: Tender ID
        update_data: Dictionary with fields to update
        
    Returns:
        Updated TenderDetail object
    """
    details = get_tender_details(db, tender_id)
    if not details:
        raise DatabaseException(f"Tender details not found: {tender_id}")
    
    for key, value in update_data.items():
        setattr(details, key, value)
    
    db.commit()
    db.refresh(details)
    log.info(f"Updated tender details: {tender_id}")
    return details


def update_document(db: Session, document_id: int, update_data: dict) -> Document:
    """
    Update document record.
    
    Args:
        db: Database session
        document_id: Document ID
        update_data: Dictionary with fields to update
        
    Returns:
        Updated Document object
    """
    document = get_document(db, document_id)
    if not document:
        raise DatabaseException(f"Document not found: {document_id}")
    
    for key, value in update_data.items():
        setattr(document, key, value)
    
    db.commit()
    db.refresh(document)
    log.info(f"Updated document: {document_id}")
    return document


def update_extracted_field(db: Session, field_id: int, update_data: dict) -> ExtractedField:
    """
    Update extracted field.
    
    Args:
        db: Database session
        field_id: Field ID
        update_data: Dictionary with fields to update
        
    Returns:
        Updated ExtractedField object
    """
    field = get_extracted_field(db, field_id)
    if not field:
        raise DatabaseException(f"Extracted field not found: {field_id}")
    
    for key, value in update_data.items():
        setattr(field, key, value)
    
    db.commit()
    db.refresh(field)
    log.info(f"Updated extracted field: {field_id}")
    return field


def update_scrape_log(db: Session, log_id: int, update_data: dict) -> ScrapeLog:
    """
    Update scrape log.
    
    Args:
        db: Database session
        log_id: Log ID
        update_data: Dictionary with fields to update
        
    Returns:
        Updated ScrapeLog object
    """
    scrape_log = get_scrape_log(db, log_id)
    if not scrape_log:
        raise DatabaseException(f"Scrape log not found: {log_id}")
    
    for key, value in update_data.items():
        setattr(scrape_log, key, value)
    
    db.commit()
    db.refresh(scrape_log)
    log.info(f"Updated scrape log: {log_id}")
    return scrape_log


# ===== DELETE operations =====

def delete_tender(db: Session, tender_id: str) -> bool:
    """
    Delete tender and related records.
    
    Args:
        db: Database session
        tender_id: Tender ID
        
    Returns:
        True if deleted, False if not found
    """
    tender = get_tender(db, tender_id)
    if not tender:
        return False
    
    try:
        # Delete related records first (if not using cascade)
        db.query(ExtractedField).filter(ExtractedField.tender_id == tender_id).delete()
        db.query(Document).filter(Document.tender_id == tender_id).delete()
        db.query(TenderDetail).filter(TenderDetail.tender_id == tender_id).delete()
        
        # Delete tender
        db.delete(tender)
        db.commit()
        log.info(f"Deleted tender: {tender_id}")
        return True
    except Exception as e:
        db.rollback()
        log.error(f"Failed to delete tender: {e}")
        raise DatabaseException(f"Failed to delete tender: {e}")


def delete_tender_details(db: Session, tender_id: str) -> bool:
    """
    Delete tender details.
    
    Args:
        db: Database session
        tender_id: Tender ID
        
    Returns:
        True if deleted, False if not found
    """
    details = get_tender_details(db, tender_id)
    if not details:
        return False
    
    try:
        db.delete(details)
        db.commit()
        log.info(f"Deleted tender details: {tender_id}")
        return True
    except Exception as e:
        db.rollback()
        log.error(f"Failed to delete tender details: {e}")
        raise DatabaseException(f"Failed to delete tender details: {e}")


def delete_document(db: Session, document_id: int) -> bool:
    """
    Delete document and related extracted fields.
    
    Args:
        db: Database session
        document_id: Document ID
        
    Returns:
        True if deleted, False if not found
    """
    document = get_document(db, document_id)
    if not document:
        return False
    
    try:
        # Delete related extracted fields
        db.query(ExtractedField).filter(ExtractedField.document_id == document_id).delete()
        
        # Delete document
        db.delete(document)
        db.commit()
        log.info(f"Deleted document: {document_id}")
        return True
    except Exception as e:
        db.rollback()
        log.error(f"Failed to delete document: {e}")
        raise DatabaseException(f"Failed to delete document: {e}")


def delete_extracted_field(db: Session, field_id: int) -> bool:
    """
    Delete extracted field.
    
    Args:
        db: Database session
        field_id: Field ID
        
    Returns:
        True if deleted, False if not found
    """
    field = get_extracted_field(db, field_id)
    if not field:
        return False
    
    try:
        db.delete(field)
        db.commit()
        log.info(f"Deleted extracted field: {field_id}")
        return True
    except Exception as e:
        db.rollback()
        log.error(f"Failed to delete extracted field: {e}")
        raise DatabaseException(f"Failed to delete extracted field: {e}")


def delete_scrape_log(db: Session, log_id: int) -> bool:
    """
    Delete scrape log.
    
    Args:
        db: Database session
        log_id: Log ID
        
    Returns:
        True if deleted, False if not found
    """
    scrape_log = get_scrape_log(db, log_id)
    if not scrape_log:
        return False
    
    try:
        db.delete(scrape_log)
        db.commit()
        log.info(f"Deleted scrape log: {log_id}")
        return True
    except Exception as e:
        db.rollback()
        log.error(f"Failed to delete scrape log: {e}")
        raise DatabaseException(f"Failed to delete scrape log: {e}")

