"""
Unit tests for database CRUD operations.

Tests for database operations defined in src/database/operations.py.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import (
    Tender,
    TenderDetail,
    Document,
    ExtractedField,
    ScrapeLog,
)
from src.database.connection import Base
from src.database.operations import (
    create_tender, get_tender, update_tender, delete_tender, list_tenders,
    save_tender_details, get_tender_details, update_tender_details, delete_tender_details,
    save_document, get_document, update_document, delete_document, 
    get_pending_downloads, list_documents,
    save_extracted_field, get_extracted_field, update_extracted_field, 
    delete_extracted_field, list_extracted_fields,
    log_scrape_run, get_scrape_log, update_scrape_log, 
    delete_scrape_log, list_scrape_logs
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
            "published_date": "2024-01-01",
        }

        tender = create_tender(db_session, tender_data)

        assert tender is not None
        assert tender.id is not None
        assert tender.tender_id == "TEST001"
        assert tender.department == "Test Department"

    def test_create_tender_duplicate(self, db_session):
        """Test creating duplicate tender raises exception."""
        tender_data = {"tender_id": "TEST001", "work_name": "Test Work"}

        create_tender(db_session, tender_data)

        with pytest.raises(DatabaseException):
            create_tender(db_session, tender_data)

    def test_get_tender_exists(self, db_session):
        """Test getting an existing tender."""
        tender_data = {"tender_id": "TEST001", "work_name": "Test Work"}
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
            "tender_value": "100000",
        }
        create_tender(db_session, tender_data)

        update_data = {"work_name": "Updated Work", "tender_value": "150000"}
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
            "legal_terms": "Test legal terms",
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
            "download_status": "PENDING",
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
            "extraction_method": "regex",
        }

        field = save_extracted_field(db_session, "TEST001", document.id, field_data)

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
            "notes": "Test scraping session",
        }

        log = log_scrape_run(db_session, log_data)

        assert log is not None
        assert log.method == "api"
        assert log.tenders_found == 100
        assert log.tenders_scraped == 95
        assert log.status == "SUCCESS"

    def test_log_scrape_run_with_defaults(self, db_session):
        """Test scrape log creation with minimal data."""
        log_data = {"method": "selenium", "tenders_found": 50, "tenders_scraped": 48}

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
            "bid_close_date": "2024-01-31",
        }
        tender = create_tender(db_session, tender_data)
        assert tender.tender_id == "INTG001"

        # Step 2: Save tender details
        details_data = {
            "eligibility": "Integration test eligibility",
            "general_terms": "Integration test general terms",
        }
        details = save_tender_details(db_session, "INTG001", details_data)
        assert details.tender_id == "INTG001"

        # Step 3: Save documents
        doc1_data = {
            "filename": "intg_doc1.pdf",
            "file_type": "pdf",
            "download_status": "PENDING",
        }
        doc2_data = {
            "filename": "intg_doc2.xlsx",
            "file_type": "xlsx",
            "download_status": "DOWNLOADED",
        }
        doc1 = save_document(db_session, "INTG001", doc1_data)
        doc2 = save_document(db_session, "INTG001", doc2_data)
        assert doc1.tender_id == "INTG001"
        assert doc2.tender_id == "INTG001"

        # Step 4: Save extracted fields
        field1_data = {
            "field_name": "emd",
            "field_value": "50000",
            "field_type": "currency",
        }
        field2_data = {
            "field_name": "tender_fee",
            "field_value": "1000",
            "field_type": "currency",
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
            "status": "SUCCESS",
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


class TestAdditionalReadOperations:
    """Tests for additional READ operations."""
    
    def test_list_tenders(self, db_session):
        """Test listing tenders with pagination."""
        # Create multiple tenders
        for i in range(5):
            tender_data = {
                "tender_id": f"LIST{i:03d}",
                "department": "Test Department",
                "work_name": f"Test Work {i}"
            }
            create_tender(db_session, tender_data)
        
        # Test without filters
        all_tenders = list_tenders(db_session)
        assert len(all_tenders) == 5
        
        # Test with pagination
        page1 = list_tenders(db_session, skip=0, limit=2)
        assert len(page1) == 2
        
        page2 = list_tenders(db_session, skip=2, limit=2)
        assert len(page2) == 2
    
    def test_list_tenders_with_filters(self, db_session):
        """Test listing tenders with filters."""
        # Create tenders with different departments
        create_tender(db_session, {
            "tender_id": "DEPT001",
            "department": "Engineering",
            "category": "Civil",
            "work_name": "Work 1"
        })
        create_tender(db_session, {
            "tender_id": "DEPT002",
            "department": "Health",
            "category": "Medical",
            "work_name": "Work 2"
        })
        create_tender(db_session, {
            "tender_id": "DEPT003",
            "department": "Engineering",
            "category": "Electrical",
            "work_name": "Work 3"
        })
        
        # Filter by department
        eng_tenders = list_tenders(db_session, department="Engineering")
        assert len(eng_tenders) == 2
        
        # Filter by category
        civil_tenders = list_tenders(db_session, category="Civil")
        assert len(civil_tenders) == 1
    
    def test_get_tender_details(self, db_session):
        """Test getting tender details."""
        # Create tender and details
        create_tender(db_session, {"tender_id": "TD001", "work_name": "Test"})
        save_tender_details(db_session, "TD001", {"eligibility": "Test eligibility"})
        
        # Get details
        details = get_tender_details(db_session, "TD001")
        assert details is not None
        assert details.tender_id == "TD001"
        assert details.eligibility == "Test eligibility"
        
        # Non-existent details
        none_details = get_tender_details(db_session, "NONEXISTENT")
        assert none_details is None
    
    def test_get_document(self, db_session):
        """Test getting document by ID."""
        create_tender(db_session, {"tender_id": "DOC001", "work_name": "Test"})
        document = save_document(db_session, "DOC001", {"filename": "test.pdf"})
        
        # Get document
        retrieved = get_document(db_session, document.id)
        assert retrieved is not None
        assert retrieved.filename == "test.pdf"
        
        # Non-existent document
        none_doc = get_document(db_session, 99999)
        assert none_doc is None
    
    def test_list_documents(self, db_session):
        """Test listing documents with filters."""
        # Create tenders and documents
        create_tender(db_session, {"tender_id": "T001", "work_name": "Test 1"})
        create_tender(db_session, {"tender_id": "T002", "work_name": "Test 2"})
        
        save_document(db_session, "T001", {"filename": "doc1.pdf", "download_status": "PENDING"})
        save_document(db_session, "T001", {"filename": "doc2.pdf", "download_status": "DOWNLOADED"})
        save_document(db_session, "T002", {"filename": "doc3.pdf", "download_status": "PENDING"})
        
        # List all documents
        all_docs = list_documents(db_session)
        assert len(all_docs) == 3
        
        # Filter by tender_id
        t001_docs = list_documents(db_session, tender_id="T001")
        assert len(t001_docs) == 2
        
        # Filter by status
        pending_docs = list_documents(db_session, status="PENDING")
        assert len(pending_docs) == 2
        
        # Filter by both
        t001_pending = list_documents(db_session, tender_id="T001", status="PENDING")
        assert len(t001_pending) == 1
    
    def test_get_extracted_field(self, db_session):
        """Test getting extracted field by ID."""
        create_tender(db_session, {"tender_id": "EF001", "work_name": "Test"})
        doc = save_document(db_session, "EF001", {"filename": "test.pdf"})
        field = save_extracted_field(db_session, "EF001", doc.id, {
            "field_name": "emd",
            "field_value": "50000"
        })
        
        # Get field
        retrieved = get_extracted_field(db_session, field.id)
        assert retrieved is not None
        assert retrieved.field_name == "emd"
        
        # Non-existent field
        none_field = get_extracted_field(db_session, 99999)
        assert none_field is None
    
    def test_list_extracted_fields(self, db_session):
        """Test listing extracted fields with filters."""
        # Create tender and documents
        create_tender(db_session, {"tender_id": "LEF001", "work_name": "Test"})
        doc1 = save_document(db_session, "LEF001", {"filename": "doc1.pdf"})
        doc2 = save_document(db_session, "LEF001", {"filename": "doc2.pdf"})
        
        # Create extracted fields
        save_extracted_field(db_session, "LEF001", doc1.id, {
            "field_name": "emd", "field_value": "50000"
        })
        save_extracted_field(db_session, "LEF001", doc1.id, {
            "field_name": "tender_fee", "field_value": "1000"
        })
        save_extracted_field(db_session, "LEF001", doc2.id, {
            "field_name": "emd", "field_value": "60000"
        })
        
        # List all fields
        all_fields = list_extracted_fields(db_session)
        assert len(all_fields) == 3
        
        # Filter by tender_id
        tender_fields = list_extracted_fields(db_session, tender_id="LEF001")
        assert len(tender_fields) == 3
        
        # Filter by document_id
        doc1_fields = list_extracted_fields(db_session, document_id=doc1.id)
        assert len(doc1_fields) == 2
        
        # Filter by field_name
        emd_fields = list_extracted_fields(db_session, field_name="emd")
        assert len(emd_fields) == 2
    
    def test_get_scrape_log(self, db_session):
        """Test getting scrape log by ID."""
        log = log_scrape_run(db_session, {
            "method": "api",
            "tenders_found": 100,
            "tenders_scraped": 95
        })
        
        # Get log
        retrieved = get_scrape_log(db_session, log.id)
        assert retrieved is not None
        assert retrieved.method == "api"
        
        # Non-existent log
        none_log = get_scrape_log(db_session, 99999)
        assert none_log is None
    
    def test_list_scrape_logs(self, db_session):
        """Test listing scrape logs with filters."""
        # Create logs with different methods and statuses
        log_scrape_run(db_session, {
            "method": "api",
            "tenders_found": 100,
            "tenders_scraped": 95,
            "status": "SUCCESS"
        })
        log_scrape_run(db_session, {
            "method": "selenium",
            "tenders_found": 50,
            "tenders_scraped": 48,
            "status": "SUCCESS"
        })
        log_scrape_run(db_session, {
            "method": "api",
            "tenders_found": 75,
            "tenders_scraped": 60,
            "status": "PARTIAL"
        })
        
        # List all logs
        all_logs = list_scrape_logs(db_session)
        assert len(all_logs) == 3
        
        # Filter by method
        api_logs = list_scrape_logs(db_session, method="api")
        assert len(api_logs) == 2
        
        # Filter by status
        success_logs = list_scrape_logs(db_session, status="SUCCESS")
        assert len(success_logs) == 2


class TestAdditionalUpdateOperations:
    """Tests for additional UPDATE operations."""
    
    def test_update_tender_details(self, db_session):
        """Test updating tender details."""
        create_tender(db_session, {"tender_id": "UTD001", "work_name": "Test"})
        save_tender_details(db_session, "UTD001", {
            "eligibility": "Original eligibility",
            "general_terms": "Original terms"
        })
        
        # Update details
        updated = update_tender_details(db_session, "UTD001", {
            "eligibility": "Updated eligibility",
            "legal_terms": "New legal terms"
        })
        
        assert updated.eligibility == "Updated eligibility"
        assert updated.general_terms == "Original terms"
        assert updated.legal_terms == "New legal terms"
    
    def test_update_tender_details_not_found(self, db_session):
        """Test updating non-existent tender details."""
        with pytest.raises(DatabaseException):
            update_tender_details(db_session, "NONEXISTENT", {"eligibility": "Test"})
    
    def test_update_document(self, db_session):
        """Test updating document."""
        create_tender(db_session, {"tender_id": "UD001", "work_name": "Test"})
        doc = save_document(db_session, "UD001", {
            "filename": "test.pdf",
            "download_status": "PENDING"
        })
        
        # Update document
        updated = update_document(db_session, doc.id, {
            "download_status": "DOWNLOADED",
            "downloaded_at": datetime.utcnow()
        })
        
        assert updated.download_status == "DOWNLOADED"
        assert updated.downloaded_at is not None
    
    def test_update_document_not_found(self, db_session):
        """Test updating non-existent document."""
        with pytest.raises(DatabaseException):
            update_document(db_session, 99999, {"download_status": "DOWNLOADED"})
    
    def test_update_extracted_field(self, db_session):
        """Test updating extracted field."""
        create_tender(db_session, {"tender_id": "UEF001", "work_name": "Test"})
        doc = save_document(db_session, "UEF001", {"filename": "test.pdf"})
        field = save_extracted_field(db_session, "UEF001", doc.id, {
            "field_name": "emd",
            "field_value": "50000",
            "field_type": "currency"
        })
        
        # Update field
        updated = update_extracted_field(db_session, field.id, {
            "field_value": "55000",
            "extraction_method": "manual"
        })
        
        assert updated.field_value == "55000"
        assert updated.extraction_method == "manual"
        assert updated.field_type == "currency"
    
    def test_update_extracted_field_not_found(self, db_session):
        """Test updating non-existent extracted field."""
        with pytest.raises(DatabaseException):
            update_extracted_field(db_session, 99999, {"field_value": "60000"})
    
    def test_update_scrape_log(self, db_session):
        """Test updating scrape log."""
        log = log_scrape_run(db_session, {
            "method": "api",
            "tenders_found": 100,
            "tenders_scraped": 95,
            "status": "PARTIAL"
        })
        
        # Update log
        updated = update_scrape_log(db_session, log.id, {
            "status": "SUCCESS",
            "notes": "Completed successfully"
        })
        
        assert updated.status == "SUCCESS"
        assert updated.notes == "Completed successfully"
    
    def test_update_scrape_log_not_found(self, db_session):
        """Test updating non-existent scrape log."""
        with pytest.raises(DatabaseException):
            update_scrape_log(db_session, 99999, {"status": "SUCCESS"})


class TestDeleteOperations:
    """Tests for DELETE operations."""
    
    def test_delete_tender(self, db_session):
        """Test deleting tender with cascade."""
        # Create tender with related data
        create_tender(db_session, {"tender_id": "DEL001", "work_name": "Test"})
        save_tender_details(db_session, "DEL001", {"eligibility": "Test"})
        doc = save_document(db_session, "DEL001", {"filename": "test.pdf"})
        save_extracted_field(db_session, "DEL001", doc.id, {
            "field_name": "emd", "field_value": "50000"
        })
        
        # Verify data exists
        assert get_tender(db_session, "DEL001") is not None
        assert get_tender_details(db_session, "DEL001") is not None
        
        # Delete tender
        result = delete_tender(db_session, "DEL001")
        assert result is True
        
        # Verify data is deleted
        assert get_tender(db_session, "DEL001") is None
        assert get_tender_details(db_session, "DEL001") is None
        assert list_documents(db_session, tender_id="DEL001") == []
        assert list_extracted_fields(db_session, tender_id="DEL001") == []
    
    def test_delete_tender_not_found(self, db_session):
        """Test deleting non-existent tender."""
        result = delete_tender(db_session, "NONEXISTENT")
        assert result is False
    
    def test_delete_tender_details(self, db_session):
        """Test deleting tender details."""
        create_tender(db_session, {"tender_id": "DELD001", "work_name": "Test"})
        save_tender_details(db_session, "DELD001", {"eligibility": "Test"})
        
        # Delete details
        result = delete_tender_details(db_session, "DELD001")
        assert result is True
        
        # Verify deletion
        assert get_tender_details(db_session, "DELD001") is None
        # Tender should still exist
        assert get_tender(db_session, "DELD001") is not None
    
    def test_delete_tender_details_not_found(self, db_session):
        """Test deleting non-existent tender details."""
        result = delete_tender_details(db_session, "NONEXISTENT")
        assert result is False
    
    def test_delete_document(self, db_session):
        """Test deleting document with cascade."""
        create_tender(db_session, {"tender_id": "DDOC001", "work_name": "Test"})
        doc = save_document(db_session, "DDOC001", {"filename": "test.pdf"})
        save_extracted_field(db_session, "DDOC001", doc.id, {
            "field_name": "emd", "field_value": "50000"
        })
        
        # Delete document
        result = delete_document(db_session, doc.id)
        assert result is True
        
        # Verify deletion
        assert get_document(db_session, doc.id) is None
        assert list_extracted_fields(db_session, document_id=doc.id) == []
    
    def test_delete_document_not_found(self, db_session):
        """Test deleting non-existent document."""
        result = delete_document(db_session, 99999)
        assert result is False
    
    def test_delete_extracted_field(self, db_session):
        """Test deleting extracted field."""
        create_tender(db_session, {"tender_id": "DEF001", "work_name": "Test"})
        doc = save_document(db_session, "DEF001", {"filename": "test.pdf"})
        field = save_extracted_field(db_session, "DEF001", doc.id, {
            "field_name": "emd", "field_value": "50000"
        })
        
        # Delete field
        result = delete_extracted_field(db_session, field.id)
        assert result is True
        
        # Verify deletion
        assert get_extracted_field(db_session, field.id) is None
    
    def test_delete_extracted_field_not_found(self, db_session):
        """Test deleting non-existent extracted field."""
        result = delete_extracted_field(db_session, 99999)
        assert result is False
    
    def test_delete_scrape_log(self, db_session):
        """Test deleting scrape log."""
        log = log_scrape_run(db_session, {
            "method": "api",
            "tenders_found": 100,
            "tenders_scraped": 95
        })
        
        # Delete log
        result = delete_scrape_log(db_session, log.id)
        assert result is True
        
        # Verify deletion
        assert get_scrape_log(db_session, log.id) is None
    
    def test_delete_scrape_log_not_found(self, db_session):
        """Test deleting non-existent scrape log."""
        result = delete_scrape_log(db_session, 99999)
        assert result is False
