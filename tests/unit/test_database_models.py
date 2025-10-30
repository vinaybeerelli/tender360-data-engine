"""
Unit tests for database models
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Tender, TenderDetail, Document, ExtractedField, ScrapeLog
from src.database.connection import Base


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestTenderModel:
    """Test Tender model."""
    
    def test_create_tender(self, db_session):
        """Test creating a tender record."""
        tender = Tender(
            tender_id="TN001",
            department="Test Department",
            notice_number="NOT001",
            category="Construction",
            work_name="Test Project",
            tender_value="1000000",
            published_date="2024-01-01",
            bid_start_date="2024-01-05",
            bid_close_date="2024-01-15",
            detail_url="https://example.com/tender/1"
        )
        db_session.add(tender)
        db_session.commit()
        
        assert tender.id is not None
        assert tender.tender_id == "TN001"
        assert tender.scraped_at is not None
        assert tender.last_updated is not None
    
    def test_tender_unique_constraint(self, db_session):
        """Test that tender_id must be unique."""
        tender1 = Tender(tender_id="TN001", work_name="Project 1")
        db_session.add(tender1)
        db_session.commit()
        
        tender2 = Tender(tender_id="TN001", work_name="Project 2")
        db_session.add(tender2)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()
    
    def test_tender_relationships(self, db_session):
        """Test tender relationships."""
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        # Test details relationship
        details = TenderDetail(tender_id="TN001", eligibility="Test eligibility")
        db_session.add(details)
        db_session.commit()
        
        assert tender.details is not None
        assert tender.details.eligibility == "Test eligibility"
        
        # Test documents relationship
        doc = Document(tender_id="TN001", filename="test.pdf")
        db_session.add(doc)
        db_session.commit()
        
        assert len(tender.documents) == 1
        assert tender.documents[0].filename == "test.pdf"


class TestTenderDetailModel:
    """Test TenderDetail model."""
    
    def test_create_tender_detail(self, db_session):
        """Test creating a tender detail record."""
        # First create a tender
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        # Create details
        details = TenderDetail(
            tender_id="TN001",
            eligibility="Must have 5 years experience",
            general_terms="Standard terms apply",
            legal_terms="Legal terms",
            technical_terms="Technical specifications",
            submission_procedure="Online submission only"
        )
        db_session.add(details)
        db_session.commit()
        
        assert details.id is not None
        assert details.tender_id == "TN001"
        assert details.scraped_at is not None
    
    def test_tender_detail_unique_constraint(self, db_session):
        """Test that tender_id in details must be unique."""
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        details1 = TenderDetail(tender_id="TN001", eligibility="Test 1")
        db_session.add(details1)
        db_session.commit()
        
        details2 = TenderDetail(tender_id="TN001", eligibility="Test 2")
        db_session.add(details2)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestDocumentModel:
    """Test Document model."""
    
    def test_create_document(self, db_session):
        """Test creating a document record."""
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        document = Document(
            tender_id="TN001",
            filename="tender_doc.pdf",
            file_path="/data/downloads/tender_doc.pdf",
            file_type="PDF",
            file_size=1024000,
            download_url="https://example.com/doc.pdf",
            download_status="DOWNLOADED",
            downloaded_at=datetime.utcnow()
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.id is not None
        assert document.tender_id == "TN001"
        assert document.download_status == "DOWNLOADED"
    
    def test_document_default_status(self, db_session):
        """Test that document has default status."""
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        document = Document(tender_id="TN001", filename="test.pdf")
        db_session.add(document)
        db_session.commit()
        
        assert document.download_status == "PENDING"
    
    def test_multiple_documents_per_tender(self, db_session):
        """Test that a tender can have multiple documents."""
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        doc1 = Document(tender_id="TN001", filename="doc1.pdf")
        doc2 = Document(tender_id="TN001", filename="doc2.pdf")
        doc3 = Document(tender_id="TN001", filename="doc3.pdf")
        
        db_session.add_all([doc1, doc2, doc3])
        db_session.commit()
        
        assert len(tender.documents) == 3


class TestExtractedFieldModel:
    """Test ExtractedField model."""
    
    def test_create_extracted_field(self, db_session):
        """Test creating an extracted field record."""
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        document = Document(tender_id="TN001", filename="test.pdf")
        db_session.add(document)
        db_session.commit()
        
        field = ExtractedField(
            tender_id="TN001",
            document_id=document.id,
            field_name="emd",
            field_value="50000",
            field_type="currency",
            extraction_method="regex"
        )
        db_session.add(field)
        db_session.commit()
        
        assert field.id is not None
        assert field.tender_id == "TN001"
        assert field.document_id == document.id
        assert field.extracted_at is not None
    
    def test_multiple_fields_per_document(self, db_session):
        """Test that a document can have multiple extracted fields."""
        tender = Tender(tender_id="TN001", work_name="Test Project")
        db_session.add(tender)
        db_session.commit()
        
        document = Document(tender_id="TN001", filename="test.pdf")
        db_session.add(document)
        db_session.commit()
        
        fields = [
            ExtractedField(
                tender_id="TN001",
                document_id=document.id,
                field_name="emd",
                field_value="50000",
                field_type="currency"
            ),
            ExtractedField(
                tender_id="TN001",
                document_id=document.id,
                field_name="tender_fee",
                field_value="1000",
                field_type="currency"
            ),
            ExtractedField(
                tender_id="TN001",
                document_id=document.id,
                field_name="deadline",
                field_value="2024-01-15",
                field_type="date"
            )
        ]
        
        db_session.add_all(fields)
        db_session.commit()
        
        assert len(document.extracted_fields) == 3
        assert len(tender.extracted_fields) == 3


class TestScrapeLogModel:
    """Test ScrapeLog model."""
    
    def test_create_scrape_log(self, db_session):
        """Test creating a scrape log record."""
        log = ScrapeLog(
            run_date=datetime.utcnow(),
            method="api",
            tenders_found=100,
            tenders_scraped=95,
            errors=5,
            status="SUCCESS",
            notes="Scraping completed successfully"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.id is not None
        assert log.method == "api"
        assert log.tenders_found == 100
        assert log.tenders_scraped == 95
    
    def test_multiple_scrape_logs(self, db_session):
        """Test creating multiple scrape log records."""
        logs = [
            ScrapeLog(method="api", tenders_found=100, tenders_scraped=100, status="SUCCESS"),
            ScrapeLog(method="selenium", tenders_found=50, tenders_scraped=45, status="PARTIAL"),
            ScrapeLog(method="hybrid", tenders_found=75, tenders_scraped=0, status="FAILED")
        ]
        
        db_session.add_all(logs)
        db_session.commit()
        
        all_logs = db_session.query(ScrapeLog).all()
        assert len(all_logs) == 3


class TestDatabaseIndexes:
    """Test database indexes."""
    
    def test_tender_id_index(self, db_session):
        """Test that tender_id has an index."""
        # Create multiple tenders
        for i in range(100):
            tender = Tender(tender_id=f"TN{i:03d}", work_name=f"Project {i}")
            db_session.add(tender)
        db_session.commit()
        
        # Query by tender_id should be fast
        result = db_session.query(Tender).filter(Tender.tender_id == "TN050").first()
        assert result is not None
        assert result.tender_id == "TN050"
    
    def test_published_date_index(self, db_session):
        """Test that published_date has an index."""
        for i in range(50):
            tender = Tender(
                tender_id=f"TN{i:03d}",
                work_name=f"Project {i}",
                published_date=f"2024-01-{(i % 30) + 1:02d}"
            )
            db_session.add(tender)
        db_session.commit()
        
        # Query by published_date
        results = db_session.query(Tender).filter(Tender.published_date == "2024-01-15").all()
        assert len(results) > 0
    
    def test_bid_close_date_index(self, db_session):
        """Test that bid_close_date has an index."""
        for i in range(50):
            tender = Tender(
                tender_id=f"TN{i:03d}",
                work_name=f"Project {i}",
                bid_close_date=f"2024-02-{(i % 28) + 1:02d}"
            )
            db_session.add(tender)
        db_session.commit()
        
        # Query by bid_close_date
        results = db_session.query(Tender).filter(Tender.bid_close_date == "2024-02-15").all()
        assert len(results) > 0
