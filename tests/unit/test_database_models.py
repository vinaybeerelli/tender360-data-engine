"""
Unit tests for database models.

Tests for SQLAlchemy models, relationships, and database operations.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.database.models import (
    Tender, TenderDetail, Document, ExtractedField, ScrapeLog
)
from src.database.connection import Base


@pytest.fixture
def db_session():
    """Create in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestTenderModel:
    """Tests for Tender model."""
    
    def test_create_tender(self, db_session):
        """Test creating a tender record."""
        tender = Tender(
            tender_id="TEST001",
            department="Test Department",
            notice_number="NOTICE001",
            category="Works",
            work_name="Test Work",
            tender_value="100000",
            published_date="2024-01-01",
            bid_start_date="2024-01-05",
            bid_close_date="2024-01-15",
            detail_url="http://example.com/tender/TEST001"
        )
        db_session.add(tender)
        db_session.commit()
        
        assert tender.id is not None
        assert tender.tender_id == "TEST001"
        assert tender.work_name == "Test Work"
        assert tender.scraped_at is not None
        assert tender.last_updated is not None
    
    def test_tender_id_unique_constraint(self, db_session):
        """Test that tender_id must be unique."""
        tender1 = Tender(tender_id="TEST001", work_name="Work 1")
        tender2 = Tender(tender_id="TEST001", work_name="Work 2")
        
        db_session.add(tender1)
        db_session.commit()
        
        db_session.add(tender2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_tender_repr(self, db_session):
        """Test tender string representation."""
        tender = Tender(tender_id="TEST001", work_name="Test Work Name")
        assert "TEST001" in repr(tender)
        assert "Test Work" in repr(tender)
    
    def test_tender_indexes(self):
        """Test that required indexes exist on Tender table."""
        inspector = inspect(Tender)
        indexed_columns = set()
        for idx in inspector.mapper.columns:
            if idx.index or idx.unique:
                indexed_columns.add(idx.name)
        
        assert "tender_id" in indexed_columns
        assert "published_date" in indexed_columns
        assert "bid_close_date" in indexed_columns


class TestTenderDetailModel:
    """Tests for TenderDetail model."""
    
    def test_create_tender_detail(self, db_session):
        """Test creating a tender detail record."""
        # Create parent tender first
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        db_session.add(tender)
        db_session.commit()
        
        # Create tender detail
        detail = TenderDetail(
            tender_id="TEST001",
            eligibility="Test eligibility",
            general_terms="Test general terms",
            legal_terms="Test legal terms",
            technical_terms="Test technical terms",
            submission_procedure="Test submission procedure"
        )
        db_session.add(detail)
        db_session.commit()
        
        assert detail.id is not None
        assert detail.tender_id == "TEST001"
        assert detail.eligibility == "Test eligibility"
        assert detail.scraped_at is not None
    
    def test_tender_detail_relationship(self, db_session):
        """Test relationship between Tender and TenderDetail."""
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        detail = TenderDetail(
            tender_id="TEST001",
            eligibility="Test eligibility"
        )
        
        db_session.add(tender)
        db_session.add(detail)
        db_session.commit()
        
        # Test forward relationship
        assert tender.details is not None
        assert tender.details.tender_id == "TEST001"
        
        # Test backward relationship
        assert detail.tender is not None
        assert detail.tender.tender_id == "TEST001"
    
    def test_tender_detail_unique_constraint(self, db_session):
        """Test that tender_id is unique in tender_details."""
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        db_session.add(tender)
        db_session.commit()
        
        detail1 = TenderDetail(tender_id="TEST001", eligibility="Detail 1")
        detail2 = TenderDetail(tender_id="TEST001", eligibility="Detail 2")
        
        db_session.add(detail1)
        db_session.commit()
        
        db_session.add(detail2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_tender_detail_indexes(self):
        """Test that required indexes exist on TenderDetail table."""
        inspector = inspect(TenderDetail)
        indexed_columns = set()
        for idx in inspector.mapper.columns:
            if idx.index or idx.unique:
                indexed_columns.add(idx.name)
        
        assert "tender_id" in indexed_columns


class TestDocumentModel:
    """Tests for Document model."""
    
    def test_create_document(self, db_session):
        """Test creating a document record."""
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        db_session.add(tender)
        db_session.commit()
        
        document = Document(
            tender_id="TEST001",
            filename="test.pdf",
            file_path="/data/downloads/test.pdf",
            file_type="pdf",
            file_size=12345,
            download_url="http://example.com/test.pdf",
            download_status="PENDING"
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.id is not None
        assert document.tender_id == "TEST001"
        assert document.filename == "test.pdf"
        assert document.download_status == "PENDING"
    
    def test_document_relationship(self, db_session):
        """Test relationship between Tender and Documents."""
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        doc1 = Document(tender_id="TEST001", filename="doc1.pdf")
        doc2 = Document(tender_id="TEST001", filename="doc2.pdf")
        
        db_session.add(tender)
        db_session.add(doc1)
        db_session.add(doc2)
        db_session.commit()
        
        # Test forward relationship (one-to-many)
        assert len(tender.documents) == 2
        assert doc1 in tender.documents
        assert doc2 in tender.documents
        
        # Test backward relationship
        assert doc1.tender.tender_id == "TEST001"
        assert doc2.tender.tender_id == "TEST001"
    
    def test_document_default_status(self, db_session):
        """Test that document has default PENDING status."""
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        document = Document(tender_id="TEST001", filename="test.pdf")
        
        db_session.add(tender)
        db_session.add(document)
        db_session.commit()
        
        assert document.download_status == "PENDING"
    
    def test_document_indexes(self):
        """Test that required indexes exist on Document table."""
        inspector = inspect(Document)
        indexed_columns = set()
        for idx in inspector.mapper.columns:
            if idx.index or idx.unique:
                indexed_columns.add(idx.name)
        
        assert "tender_id" in indexed_columns


class TestExtractedFieldModel:
    """Tests for ExtractedField model."""
    
    def test_create_extracted_field(self, db_session):
        """Test creating an extracted field record."""
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        document = Document(tender_id="TEST001", filename="test.pdf")
        
        db_session.add(tender)
        db_session.add(document)
        db_session.commit()
        
        field = ExtractedField(
            tender_id="TEST001",
            document_id=document.id,
            field_name="emd",
            field_value="50000",
            field_type="currency",
            extraction_method="regex"
        )
        db_session.add(field)
        db_session.commit()
        
        assert field.id is not None
        assert field.tender_id == "TEST001"
        assert field.document_id == document.id
        assert field.field_name == "emd"
        assert field.extracted_at is not None
    
    def test_extracted_field_relationships(self, db_session):
        """Test relationships between ExtractedField, Tender, and Document."""
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        document = Document(tender_id="TEST001", filename="test.pdf")
        field = ExtractedField(
            tender_id="TEST001",
            document_id=None,  # Will be set after document is saved
            field_name="emd",
            field_value="50000"
        )
        
        db_session.add(tender)
        db_session.add(document)
        db_session.commit()
        
        field.document_id = document.id
        db_session.add(field)
        db_session.commit()
        
        # Test tender relationship
        assert field.tender.tender_id == "TEST001"
        assert field in tender.extracted_fields
        
        # Test document relationship
        assert field.document.filename == "test.pdf"
        assert field in document.extracted_fields
    
    def test_extracted_field_indexes(self):
        """Test that required indexes exist on ExtractedField table."""
        inspector = inspect(ExtractedField)
        indexed_columns = set()
        for idx in inspector.mapper.columns:
            if idx.index or idx.unique:
                indexed_columns.add(idx.name)
        
        assert "tender_id" in indexed_columns
        assert "document_id" in indexed_columns


class TestScrapeLogModel:
    """Tests for ScrapeLog model."""
    
    def test_create_scrape_log(self, db_session):
        """Test creating a scrape log record."""
        log = ScrapeLog(
            method="api",
            tenders_found=100,
            tenders_scraped=95,
            errors=5,
            status="SUCCESS",
            notes="Test scraping session"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.id is not None
        assert log.method == "api"
        assert log.tenders_found == 100
        assert log.tenders_scraped == 95
        assert log.run_date is not None
    
    def test_scrape_log_repr(self, db_session):
        """Test scrape log string representation."""
        log = ScrapeLog(
            method="api",
            tenders_found=100,
            tenders_scraped=95
        )
        db_session.add(log)
        db_session.commit()
        
        repr_str = repr(log)
        assert "95" in repr_str
        assert "100" in repr_str


class TestModelIntegration:
    """Integration tests for multiple models."""
    
    def test_complete_data_flow(self, db_session):
        """Test complete data flow from tender to extracted fields."""
        # Create tender
        tender = Tender(
            tender_id="TEST001",
            department="Test Dept",
            work_name="Test Work"
        )
        db_session.add(tender)
        db_session.commit()
        
        # Create tender details
        detail = TenderDetail(
            tender_id="TEST001",
            eligibility="Test eligibility"
        )
        db_session.add(detail)
        db_session.commit()
        
        # Create documents
        doc1 = Document(
            tender_id="TEST001",
            filename="doc1.pdf",
            download_status="DOWNLOADED"
        )
        doc2 = Document(
            tender_id="TEST001",
            filename="doc2.pdf",
            download_status="DOWNLOADED"
        )
        db_session.add_all([doc1, doc2])
        db_session.commit()
        
        # Create extracted fields
        field1 = ExtractedField(
            tender_id="TEST001",
            document_id=doc1.id,
            field_name="emd",
            field_value="50000"
        )
        field2 = ExtractedField(
            tender_id="TEST001",
            document_id=doc2.id,
            field_name="tender_fee",
            field_value="1000"
        )
        db_session.add_all([field1, field2])
        db_session.commit()
        
        # Create scrape log
        log = ScrapeLog(
            method="api",
            tenders_found=1,
            tenders_scraped=1,
            errors=0,
            status="SUCCESS"
        )
        db_session.add(log)
        db_session.commit()
        
        # Verify all relationships
        assert tender.details.eligibility == "Test eligibility"
        assert len(tender.documents) == 2
        assert len(tender.extracted_fields) == 2
        
        # Verify cascading
        assert doc1.tender.tender_id == "TEST001"
        assert field1.tender.tender_id == "TEST001"
        assert field1.document.filename == "doc1.pdf"
