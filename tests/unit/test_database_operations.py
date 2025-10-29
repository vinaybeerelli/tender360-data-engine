"""
Unit tests for database CRUD operations
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Tender, TenderDetail, Document, ExtractedField, ScrapeLog
from src.database.connection import Base
from src.database.operations import (
    create_tender,
    get_tender,
    update_tender,
    save_tender_details,
    save_document,
    get_pending_downloads,
    save_extracted_field,
    log_scrape_run
)
from src.utils.exceptions import DatabaseException


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestTenderOperations:
    """Test tender CRUD operations."""
    
    def test_create_tender(self, db_session):
        """Test creating a tender."""
        tender_data = {
            "tender_id": "TN001",
            "department": "Public Works",
            "notice_number": "NOT001",
            "category": "Construction",
            "work_name": "Road Construction Project",
            "tender_value": "5000000",
            "published_date": "2024-01-01",
            "bid_start_date": "2024-01-05",
            "bid_close_date": "2024-01-15",
            "detail_url": "https://example.com/tender/1"
        }
        
        tender = create_tender(db_session, tender_data)
        
        assert tender.id is not None
        assert tender.tender_id == "TN001"
        assert tender.work_name == "Road Construction Project"
        assert tender.scraped_at is not None
    
    def test_create_duplicate_tender_fails(self, db_session):
        """Test that creating duplicate tender fails."""
        tender_data = {"tender_id": "TN001", "work_name": "Project 1"}
        create_tender(db_session, tender_data)
        
        with pytest.raises(DatabaseException):
            create_tender(db_session, tender_data)
    
    def test_get_tender(self, db_session):
        """Test retrieving a tender."""
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        tender = get_tender(db_session, "TN001")
        
        assert tender is not None
        assert tender.tender_id == "TN001"
        assert tender.work_name == "Test Project"
    
    def test_get_nonexistent_tender(self, db_session):
        """Test retrieving a non-existent tender."""
        tender = get_tender(db_session, "NONEXISTENT")
        assert tender is None
    
    def test_update_tender(self, db_session):
        """Test updating a tender."""
        tender_data = {"tender_id": "TN001", "work_name": "Original Name"}
        create_tender(db_session, tender_data)
        
        update_data = {"work_name": "Updated Name", "tender_value": "1000000"}
        updated_tender = update_tender(db_session, "TN001", update_data)
        
        assert updated_tender.work_name == "Updated Name"
        assert updated_tender.tender_value == "1000000"
        assert updated_tender.tender_id == "TN001"
    
    def test_update_nonexistent_tender_fails(self, db_session):
        """Test that updating non-existent tender fails."""
        with pytest.raises(DatabaseException):
            update_tender(db_session, "NONEXISTENT", {"work_name": "Test"})


class TestTenderDetailsOperations:
    """Test tender details operations."""
    
    def test_save_tender_details(self, db_session):
        """Test saving tender details."""
        # Create tender first
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        # Save details
        details_data = {
            "eligibility": "Must have 5 years experience",
            "general_terms": "Standard terms apply",
            "legal_terms": "Legal compliance required",
            "technical_terms": "Technical specifications provided",
            "submission_procedure": "Online submission only"
        }
        
        details = save_tender_details(db_session, "TN001", details_data)
        
        assert details.id is not None
        assert details.tender_id == "TN001"
        assert details.eligibility == "Must have 5 years experience"
        assert details.scraped_at is not None
    
    def test_save_duplicate_details_fails(self, db_session):
        """Test that saving duplicate details fails."""
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        details_data = {"eligibility": "Test eligibility"}
        save_tender_details(db_session, "TN001", details_data)
        
        # Try to save again
        with pytest.raises(DatabaseException):
            save_tender_details(db_session, "TN001", details_data)


class TestDocumentOperations:
    """Test document operations."""
    
    def test_save_document(self, db_session):
        """Test saving a document."""
        # Create tender first
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        # Save document
        document_data = {
            "filename": "tender_document.pdf",
            "file_path": "/data/downloads/tender_document.pdf",
            "file_type": "PDF",
            "file_size": 2048000,
            "download_url": "https://example.com/doc.pdf",
            "download_status": "PENDING"
        }
        
        document = save_document(db_session, "TN001", document_data)
        
        assert document.id is not None
        assert document.tender_id == "TN001"
        assert document.filename == "tender_document.pdf"
        assert document.download_status == "PENDING"
    
    def test_save_multiple_documents(self, db_session):
        """Test saving multiple documents for a tender."""
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        doc1 = save_document(db_session, "TN001", {"filename": "doc1.pdf"})
        doc2 = save_document(db_session, "TN001", {"filename": "doc2.pdf"})
        doc3 = save_document(db_session, "TN001", {"filename": "doc3.pdf"})
        
        assert doc1.id != doc2.id != doc3.id
        
        # Verify all documents are linked to the tender
        tender = get_tender(db_session, "TN001")
        assert len(tender.documents) == 3
    
    def test_get_pending_downloads(self, db_session):
        """Test retrieving pending downloads."""
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        # Create documents with different statuses
        save_document(db_session, "TN001", {"filename": "doc1.pdf", "download_status": "PENDING"})
        save_document(db_session, "TN001", {"filename": "doc2.pdf", "download_status": "DOWNLOADED"})
        save_document(db_session, "TN001", {"filename": "doc3.pdf", "download_status": "PENDING"})
        save_document(db_session, "TN001", {"filename": "doc4.pdf", "download_status": "FAILED"})
        
        pending = get_pending_downloads(db_session)
        
        assert len(pending) == 2
        assert all(doc.download_status == "PENDING" for doc in pending)


class TestExtractedFieldOperations:
    """Test extracted field operations."""
    
    def test_save_extracted_field(self, db_session):
        """Test saving an extracted field."""
        # Create tender and document
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        document = save_document(db_session, "TN001", {"filename": "test.pdf"})
        
        # Save extracted field
        field_data = {
            "field_name": "emd",
            "field_value": "50000",
            "field_type": "currency",
            "extraction_method": "regex"
        }
        
        field = save_extracted_field(db_session, "TN001", document.id, field_data)
        
        assert field.id is not None
        assert field.tender_id == "TN001"
        assert field.document_id == document.id
        assert field.field_name == "emd"
        assert field.field_value == "50000"
        assert field.extracted_at is not None
    
    def test_save_multiple_fields(self, db_session):
        """Test saving multiple extracted fields."""
        tender_data = {"tender_id": "TN001", "work_name": "Test Project"}
        create_tender(db_session, tender_data)
        
        document = save_document(db_session, "TN001", {"filename": "test.pdf"})
        
        fields = [
            {"field_name": "emd", "field_value": "50000", "field_type": "currency"},
            {"field_name": "tender_fee", "field_value": "1000", "field_type": "currency"},
            {"field_name": "deadline", "field_value": "2024-01-15", "field_type": "date"}
        ]
        
        saved_fields = []
        for field_data in fields:
            field = save_extracted_field(db_session, "TN001", document.id, field_data)
            saved_fields.append(field)
        
        assert len(saved_fields) == 3
        
        # Verify all fields are linked to document
        db_session.refresh(document)
        assert len(document.extracted_fields) == 3


class TestScrapeLogOperations:
    """Test scrape log operations."""
    
    def test_log_scrape_run(self, db_session):
        """Test logging a scrape run."""
        log_data = {
            "run_date": datetime.utcnow(),
            "method": "api",
            "tenders_found": 100,
            "tenders_scraped": 95,
            "errors": 5,
            "status": "SUCCESS",
            "notes": "Scraping completed with minor errors"
        }
        
        log = log_scrape_run(db_session, log_data)
        
        assert log.id is not None
        assert log.method == "api"
        assert log.tenders_found == 100
        assert log.tenders_scraped == 95
        assert log.status == "SUCCESS"
    
    def test_log_multiple_runs(self, db_session):
        """Test logging multiple scrape runs."""
        runs = [
            {
                "method": "api",
                "tenders_found": 100,
                "tenders_scraped": 100,
                "errors": 0,
                "status": "SUCCESS"
            },
            {
                "method": "selenium",
                "tenders_found": 50,
                "tenders_scraped": 45,
                "errors": 5,
                "status": "PARTIAL"
            },
            {
                "method": "hybrid",
                "tenders_found": 75,
                "tenders_scraped": 0,
                "errors": 75,
                "status": "FAILED"
            }
        ]
        
        for run_data in runs:
            log_scrape_run(db_session, run_data)
        
        all_logs = db_session.query(ScrapeLog).all()
        assert len(all_logs) == 3


class TestCompleteWorkflow:
    """Test complete workflow from tender to extracted fields."""
    
    def test_complete_tender_workflow(self, db_session):
        """Test the complete workflow of creating and linking all entities."""
        # 1. Create tender
        tender_data = {
            "tender_id": "TN001",
            "department": "Public Works",
            "work_name": "Highway Construction",
            "tender_value": "10000000",
            "published_date": "2024-01-01",
            "bid_close_date": "2024-01-31"
        }
        tender = create_tender(db_session, tender_data)
        
        # 2. Add tender details
        details_data = {
            "eligibility": "Class A contractor with 10 years experience",
            "general_terms": "Standard government terms",
            "technical_terms": "Highway specifications"
        }
        details = save_tender_details(db_session, "TN001", details_data)
        
        # 3. Add documents
        doc1 = save_document(db_session, "TN001", {
            "filename": "tender_notice.pdf",
            "download_status": "DOWNLOADED"
        })
        doc2 = save_document(db_session, "TN001", {
            "filename": "technical_specs.pdf",
            "download_status": "DOWNLOADED"
        })
        
        # 4. Add extracted fields
        field1 = save_extracted_field(db_session, "TN001", doc1.id, {
            "field_name": "emd",
            "field_value": "200000",
            "field_type": "currency"
        })
        field2 = save_extracted_field(db_session, "TN001", doc1.id, {
            "field_name": "tender_fee",
            "field_value": "5000",
            "field_type": "currency"
        })
        
        # 5. Log the scrape run
        log = log_scrape_run(db_session, {
            "method": "api",
            "tenders_found": 1,
            "tenders_scraped": 1,
            "errors": 0,
            "status": "SUCCESS"
        })
        
        # Verify everything is linked correctly
        db_session.refresh(tender)
        assert tender.details is not None
        assert len(tender.documents) == 2
        assert len(tender.extracted_fields) == 2
        
        # Verify relationships
        assert tender.details.eligibility == "Class A contractor with 10 years experience"
        assert tender.documents[0].filename in ["tender_notice.pdf", "technical_specs.pdf"]
        assert doc1.extracted_fields[0].field_name in ["emd", "tender_fee"]
