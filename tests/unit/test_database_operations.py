"""
Unit tests for database CRUD operations.

Tests for database operations defined in src/database/operations.py.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import (
    Tender, TenderDetail, Document, ExtractedField, ScrapeLog
)
from src.database.connection import Base
from src.database.operations import (
    create_tender, get_tender, update_tender,
    save_tender_details, save_document, get_pending_downloads,
    save_extracted_field, log_scrape_run
)
from src.utils.exceptions import DatabaseException


@pytest.fixture
def db_session():
    """Create in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestTenderOperations:
    """Tests for tender CRUD operations."""
    
    def test_create_tender_success(self, db_session):
        """Test successful tender creation."""
        tender_data = {
            "tender_id": "TEST001",
            "department": "Test Department",
            "work_name": "Test Work",
            "tender_value": "100000",
            "published_date": "2024-01-01"
        }
        
        tender = create_tender(db_session, tender_data)
        
        assert tender is not None
        assert tender.id is not None
        assert tender.tender_id == "TEST001"
        assert tender.department == "Test Department"
    
    def test_create_tender_duplicate(self, db_session):
        """Test creating duplicate tender raises exception."""
        tender_data = {
            "tender_id": "TEST001",
            "work_name": "Test Work"
        }
        
        create_tender(db_session, tender_data)
        
        with pytest.raises(DatabaseException):
            create_tender(db_session, tender_data)
    
    def test_get_tender_exists(self, db_session):
        """Test getting an existing tender."""
        tender_data = {
            "tender_id": "TEST001",
            "work_name": "Test Work"
        }
        create_tender(db_session, tender_data)
        
        tender = get_tender(db_session, "TEST001")
        
        assert tender is not None
        assert tender.tender_id == "TEST001"
    
    def test_get_tender_not_exists(self, db_session):
        """Test getting a non-existent tender returns None."""
        tender = get_tender(db_session, "NONEXISTENT")
        assert tender is None
    
    def test_update_tender_success(self, db_session):
        """Test successful tender update."""
        tender_data = {
            "tender_id": "TEST001",
            "work_name": "Original Work",
            "tender_value": "100000"
        }
        create_tender(db_session, tender_data)
        
        update_data = {
            "work_name": "Updated Work",
            "tender_value": "150000"
        }
        updated_tender = update_tender(db_session, "TEST001", update_data)
        
        assert updated_tender.work_name == "Updated Work"
        assert updated_tender.tender_value == "150000"
    
    def test_update_tender_not_exists(self, db_session):
        """Test updating non-existent tender raises exception."""
        update_data = {"work_name": "Updated Work"}
        
        with pytest.raises(DatabaseException):
            update_tender(db_session, "NONEXISTENT", update_data)


class TestTenderDetailOperations:
    """Tests for tender detail operations."""
    
    def test_save_tender_details_success(self, db_session):
        """Test successful tender detail creation."""
        # Create parent tender first
        tender_data = {"tender_id": "TEST001", "work_name": "Test Work"}
        create_tender(db_session, tender_data)
        
        details_data = {
            "eligibility": "Test eligibility",
            "general_terms": "Test general terms",
            "legal_terms": "Test legal terms"
        }
        
        details = save_tender_details(db_session, "TEST001", details_data)
        
        assert details is not None
        assert details.tender_id == "TEST001"
        assert details.eligibility == "Test eligibility"
    
    def test_save_tender_details_without_parent(self, db_session):
        """Test saving details without parent tender succeeds but creates orphan record."""
        details_data = {"eligibility": "Test eligibility"}
        
        # SQLite doesn't enforce foreign keys by default, so this succeeds
        details = save_tender_details(db_session, "NONEXISTENT", details_data)
        
        assert details is not None
        assert details.tender_id == "NONEXISTENT"
        # This creates an orphan record, but doesn't fail


class TestDocumentOperations:
    """Tests for document operations."""
    
    def test_save_document_success(self, db_session):
        """Test successful document creation."""
        # Create parent tender first
        tender_data = {"tender_id": "TEST001", "work_name": "Test Work"}
        create_tender(db_session, tender_data)
        
        document_data = {
            "filename": "test.pdf",
            "file_path": "/data/downloads/test.pdf",
            "file_type": "pdf",
            "file_size": 12345,
            "download_url": "http://example.com/test.pdf",
            "download_status": "PENDING"
        }
        
        document = save_document(db_session, "TEST001", document_data)
        
        assert document is not None
        assert document.tender_id == "TEST001"
        assert document.filename == "test.pdf"
        assert document.download_status == "PENDING"
    
    def test_save_document_without_parent(self, db_session):
        """Test saving document without parent tender succeeds but creates orphan record."""
        document_data = {"filename": "test.pdf"}
        
        # SQLite doesn't enforce foreign keys by default, so this succeeds
        document = save_document(db_session, "NONEXISTENT", document_data)
        
        assert document is not None
        assert document.tender_id == "NONEXISTENT"
        # This creates an orphan record, but doesn't fail
    
    def test_get_pending_downloads(self, db_session):
        """Test getting documents with pending status."""
        # Create parent tender
        tender_data = {"tender_id": "TEST001", "work_name": "Test Work"}
        create_tender(db_session, tender_data)
        
        # Create documents with different statuses
        doc1_data = {"filename": "doc1.pdf", "download_status": "PENDING"}
        doc2_data = {"filename": "doc2.pdf", "download_status": "DOWNLOADED"}
        doc3_data = {"filename": "doc3.pdf", "download_status": "PENDING"}
        
        save_document(db_session, "TEST001", doc1_data)
        save_document(db_session, "TEST001", doc2_data)
        save_document(db_session, "TEST001", doc3_data)
        
        pending = get_pending_downloads(db_session)
        
        assert len(pending) == 2
        assert all(doc.download_status == "PENDING" for doc in pending)


class TestExtractedFieldOperations:
    """Tests for extracted field operations."""
    
    def test_save_extracted_field_success(self, db_session):
        """Test successful extracted field creation."""
        # Create parent tender and document
        tender_data = {"tender_id": "TEST001", "work_name": "Test Work"}
        tender = create_tender(db_session, tender_data)
        
        document_data = {"filename": "test.pdf"}
        document = save_document(db_session, "TEST001", document_data)
        
        field_data = {
            "field_name": "emd",
            "field_value": "50000",
            "field_type": "currency",
            "extraction_method": "regex"
        }
        
        field = save_extracted_field(
            db_session, "TEST001", document.id, field_data
        )
        
        assert field is not None
        assert field.tender_id == "TEST001"
        assert field.document_id == document.id
        assert field.field_name == "emd"
        assert field.field_value == "50000"
    
    def test_save_extracted_field_without_parent(self, db_session):
        """Test saving field without parent succeeds but creates orphan record."""
        field_data = {"field_name": "emd", "field_value": "50000"}
        
        # SQLite doesn't enforce foreign keys by default, so this succeeds
        field = save_extracted_field(db_session, "NONEXISTENT", 999, field_data)
        
        assert field is not None
        assert field.tender_id == "NONEXISTENT"
        # This creates an orphan record, but doesn't fail


class TestScrapeLogOperations:
    """Tests for scrape log operations."""
    
    def test_log_scrape_run_success(self, db_session):
        """Test successful scrape log creation."""
        log_data = {
            "method": "api",
            "tenders_found": 100,
            "tenders_scraped": 95,
            "errors": 5,
            "status": "SUCCESS",
            "notes": "Test scraping session"
        }
        
        log = log_scrape_run(db_session, log_data)
        
        assert log is not None
        assert log.method == "api"
        assert log.tenders_found == 100
        assert log.tenders_scraped == 95
        assert log.status == "SUCCESS"
    
    def test_log_scrape_run_with_defaults(self, db_session):
        """Test scrape log creation with minimal data."""
        log_data = {
            "method": "selenium",
            "tenders_found": 50,
            "tenders_scraped": 48
        }
        
        log = log_scrape_run(db_session, log_data)
        
        assert log is not None
        assert log.method == "selenium"
        assert log.run_date is not None


class TestOperationsIntegration:
    """Integration tests for database operations."""
    
    def test_complete_workflow(self, db_session):
        """Test complete workflow from tender creation to field extraction."""
        # Step 1: Create tender
        tender_data = {
            "tender_id": "INTG001",
            "department": "Integration Test Dept",
            "work_name": "Integration Test Work",
            "tender_value": "500000",
            "published_date": "2024-01-01",
            "bid_close_date": "2024-01-31"
        }
        tender = create_tender(db_session, tender_data)
        assert tender.tender_id == "INTG001"
        
        # Step 2: Save tender details
        details_data = {
            "eligibility": "Integration test eligibility",
            "general_terms": "Integration test general terms"
        }
        details = save_tender_details(db_session, "INTG001", details_data)
        assert details.tender_id == "INTG001"
        
        # Step 3: Save documents
        doc1_data = {
            "filename": "intg_doc1.pdf",
            "file_type": "pdf",
            "download_status": "PENDING"
        }
        doc2_data = {
            "filename": "intg_doc2.xlsx",
            "file_type": "xlsx",
            "download_status": "DOWNLOADED"
        }
        doc1 = save_document(db_session, "INTG001", doc1_data)
        doc2 = save_document(db_session, "INTG001", doc2_data)
        assert doc1.tender_id == "INTG001"
        assert doc2.tender_id == "INTG001"
        
        # Step 4: Save extracted fields
        field1_data = {
            "field_name": "emd",
            "field_value": "50000",
            "field_type": "currency"
        }
        field2_data = {
            "field_name": "tender_fee",
            "field_value": "1000",
            "field_type": "currency"
        }
        field1 = save_extracted_field(db_session, "INTG001", doc1.id, field1_data)
        field2 = save_extracted_field(db_session, "INTG001", doc2.id, field2_data)
        assert field1.tender_id == "INTG001"
        assert field2.tender_id == "INTG001"
        
        # Step 5: Log scraping session
        log_data = {
            "method": "hybrid",
            "tenders_found": 1,
            "tenders_scraped": 1,
            "errors": 0,
            "status": "SUCCESS"
        }
        log = log_scrape_run(db_session, log_data)
        assert log.status == "SUCCESS"
        
        # Step 6: Verify relationships
        retrieved_tender = get_tender(db_session, "INTG001")
        assert retrieved_tender is not None
        assert retrieved_tender.details is not None
        assert len(retrieved_tender.documents) == 2
        assert len(retrieved_tender.extracted_fields) == 2
        
        # Step 7: Update tender
        update_data = {"tender_value": "600000"}
        updated_tender = update_tender(db_session, "INTG001", update_data)
        assert updated_tender.tender_value == "600000"
        
        # Step 8: Get pending downloads
        pending = get_pending_downloads(db_session)
        assert len(pending) == 1
        assert pending[0].filename == "intg_doc1.pdf"
