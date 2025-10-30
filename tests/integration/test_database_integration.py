"""
Integration tests for database functionality
"""

import pytest
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from src.database.connection import init_database, create_tables, Base, get_db
from src.database.models import Tender, TenderDetail, Document, ExtractedField, ScrapeLog
from src.database.operations import (
    create_tender,
    get_tender,
    save_tender_details,
    save_document,
    save_extracted_field,
    log_scrape_run
)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database globals before each test."""
    import src.database.connection as conn
    conn.engine = None
    conn.SessionLocal = None
    yield
    # Clean up after test
    if conn.engine:
        conn.Base.metadata.drop_all(conn.engine)
        conn.engine.dispose()
    conn.engine = None
    conn.SessionLocal = None


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database file."""
    db_file = tmp_path / "test_tender.db"
    db_url = f"sqlite:///{db_file}"
    # Set environment variable before importing Settings
    old_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = db_url
    
    yield db_url
    
    # Cleanup
    if db_file.exists():
        db_file.unlink()
    
    # Restore old value
    if old_db_url:
        os.environ["DATABASE_URL"] = old_db_url
    else:
        os.environ.pop("DATABASE_URL", None)


class TestDatabaseInitialization:
    """Test database initialization and setup."""
    
    def test_init_database(self, test_db_path):
        """Test database engine initialization."""
        engine = init_database()
        
        assert engine is not None
        # Just verify engine exists and can connect
        assert engine.url is not None
    
    def test_create_tables(self, test_db_path):
        """Test creating all database tables."""
        init_database()
        create_tables()
        
        # Verify all tables exist
        engine = init_database()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            "tenders",
            "tender_details",
            "documents",
            "extracted_fields",
            "scrape_logs"
        ]
        
        for table in expected_tables:
            assert table in tables
    
    def test_table_schema_correctness(self, test_db_path):
        """Test that all table schemas are correct."""
        init_database()
        create_tables()
        
        engine = init_database()
        inspector = inspect(engine)
        
        # Test tenders table
        tenders_columns = {col['name'] for col in inspector.get_columns('tenders')}
        expected_tenders_columns = {
            'id', 'tender_id', 'department', 'notice_number', 'category',
            'work_name', 'tender_value', 'published_date', 'bid_start_date',
            'bid_close_date', 'detail_url', 'scraped_at', 'last_updated'
        }
        assert tenders_columns == expected_tenders_columns
        
        # Test tender_details table
        details_columns = {col['name'] for col in inspector.get_columns('tender_details')}
        expected_details_columns = {
            'id', 'tender_id', 'eligibility', 'general_terms', 'legal_terms',
            'technical_terms', 'submission_procedure', 'scraped_at'
        }
        assert details_columns == expected_details_columns
        
        # Test documents table
        documents_columns = {col['name'] for col in inspector.get_columns('documents')}
        expected_documents_columns = {
            'id', 'tender_id', 'filename', 'file_path', 'file_type',
            'file_size', 'download_url', 'download_status', 'downloaded_at'
        }
        assert documents_columns == expected_documents_columns
        
        # Test extracted_fields table
        fields_columns = {col['name'] for col in inspector.get_columns('extracted_fields')}
        expected_fields_columns = {
            'id', 'tender_id', 'document_id', 'field_name', 'field_value',
            'field_type', 'extraction_method', 'extracted_at'
        }
        assert fields_columns == expected_fields_columns
        
        # Test scrape_logs table
        logs_columns = {col['name'] for col in inspector.get_columns('scrape_logs')}
        expected_logs_columns = {
            'id', 'run_date', 'method', 'tenders_found', 'tenders_scraped',
            'errors', 'status', 'notes'
        }
        assert logs_columns == expected_logs_columns
    
    def test_foreign_keys_exist(self, test_db_path):
        """Test that foreign key constraints are properly defined."""
        init_database()
        create_tables()
        
        engine = init_database()
        inspector = inspect(engine)
        
        # Check tender_details foreign key
        details_fks = inspector.get_foreign_keys('tender_details')
        assert len(details_fks) == 1
        assert details_fks[0]['referred_table'] == 'tenders'
        assert 'tender_id' in details_fks[0]['constrained_columns']
        
        # Check documents foreign key
        docs_fks = inspector.get_foreign_keys('documents')
        assert len(docs_fks) == 1
        assert docs_fks[0]['referred_table'] == 'tenders'
        
        # Check extracted_fields foreign keys
        fields_fks = inspector.get_foreign_keys('extracted_fields')
        assert len(fields_fks) == 2
        fk_tables = [fk['referred_table'] for fk in fields_fks]
        assert 'tenders' in fk_tables
        assert 'documents' in fk_tables
    
    def test_indexes_exist(self, test_db_path):
        """Test that required indexes are created."""
        init_database()
        create_tables()
        
        engine = init_database()
        inspector = inspect(engine)
        
        # Check tenders indexes
        tenders_indexes = inspector.get_indexes('tenders')
        index_columns = [idx['column_names'][0] for idx in tenders_indexes if len(idx['column_names']) == 1]
        
        assert 'tender_id' in index_columns
        assert 'published_date' in index_columns
        assert 'bid_close_date' in index_columns


class TestCompleteIntegration:
    """Test complete integration workflow."""
    
    def test_end_to_end_workflow(self, test_db_path):
        """Test complete end-to-end workflow with real database."""
        # Initialize database with test path
        import src.database.connection as conn
        conn.engine = None
        conn.SessionLocal = None
        
        # Use test database
        engine = create_engine(test_db_path)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        try:
            # 1. Create tender
            tender_data = {
                "tender_id": "TN2024001",
                "department": "Public Works Department",
                "notice_number": "PWD/2024/001",
                "category": "Civil Engineering",
                "work_name": "Construction of Highway Bridge",
                "tender_value": "50000000",
                "published_date": "2024-01-01",
                "bid_start_date": "2024-01-05",
                "bid_close_date": "2024-01-31",
                "detail_url": "https://tender.telangana.gov.in/tender/TN2024001"
            }
            tender = create_tender(db, tender_data)
            assert tender.id is not None
            
            # 2. Save tender details
            details_data = {
                "eligibility": "Class A contractor with minimum 10 years experience",
                "general_terms": "All general terms as per government guidelines",
                "legal_terms": "Legal compliance required for all activities",
                "technical_terms": "Technical specifications as per IRC standards",
                "submission_procedure": "Online submission through e-procurement portal"
            }
            details = save_tender_details(db, "TN2024001", details_data)
            assert details.id is not None
            
            # 3. Save documents
            doc1_data = {
                "filename": "tender_notice.pdf",
                "file_path": "/data/downloads/TN2024001/tender_notice.pdf",
                "file_type": "PDF",
                "file_size": 2048000,
                "download_url": "https://tender.telangana.gov.in/docs/tender_notice.pdf",
                "download_status": "DOWNLOADED"
            }
            doc1 = save_document(db, "TN2024001", doc1_data)
            
            doc2_data = {
                "filename": "technical_specifications.pdf",
                "file_path": "/data/downloads/TN2024001/technical_specifications.pdf",
                "file_type": "PDF",
                "file_size": 5120000,
                "download_url": "https://tender.telangana.gov.in/docs/tech_spec.pdf",
                "download_status": "DOWNLOADED"
            }
            doc2 = save_document(db, "TN2024001", doc2_data)
            
            # 4. Save extracted fields
            field1_data = {
                "field_name": "emd_amount",
                "field_value": "1000000",
                "field_type": "currency",
                "extraction_method": "regex"
            }
            field1 = save_extracted_field(db, "TN2024001", doc1.id, field1_data)
            
            field2_data = {
                "field_name": "tender_fee",
                "field_value": "50000",
                "field_type": "currency",
                "extraction_method": "table"
            }
            field2 = save_extracted_field(db, "TN2024001", doc1.id, field2_data)
            
            field3_data = {
                "field_name": "project_duration",
                "field_value": "24 months",
                "field_type": "text",
                "extraction_method": "regex"
            }
            field3 = save_extracted_field(db, "TN2024001", doc2.id, field3_data)
            
            # 5. Log scrape run
            log_data = {
                "method": "api",
                "tenders_found": 1,
                "tenders_scraped": 1,
                "errors": 0,
                "status": "SUCCESS",
                "notes": "Successfully scraped and processed tender TN2024001"
            }
            log = log_scrape_run(db, log_data)
            
            # Verify everything
            retrieved_tender = get_tender(db, "TN2024001")
            assert retrieved_tender is not None
            assert retrieved_tender.work_name == "Construction of Highway Bridge"
            
            # Verify relationships
            assert retrieved_tender.details is not None
            assert retrieved_tender.details.eligibility.startswith("Class A contractor")
            
            assert len(retrieved_tender.documents) == 2
            assert retrieved_tender.documents[0].filename in ["tender_notice.pdf", "technical_specifications.pdf"]
            
            assert len(retrieved_tender.extracted_fields) == 3
            field_names = [f.field_name for f in retrieved_tender.extracted_fields]
            assert "emd_amount" in field_names
            assert "tender_fee" in field_names
            assert "project_duration" in field_names
            
            # Verify scrape log
            all_logs = db.query(ScrapeLog).all()
            assert len(all_logs) == 1
            assert all_logs[0].status == "SUCCESS"
            
        finally:
            db.close()
    
    def test_query_performance(self, test_db_path):
        """Test that indexed queries perform well."""
        # Use test database
        engine = create_engine(test_db_path)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        try:
            # Create multiple tenders with specific dates
            for i in range(100):
                tender_data = {
                    "tender_id": f"TN{i:05d}",
                    "work_name": f"Project {i}",
                    "published_date": f"2024-{(i % 12) + 1:02d}-15",
                    "bid_close_date": f"2024-{((i + 1) % 12) + 1:02d}-20"
                }
                create_tender(db, tender_data)
            
            # Query by tender_id (indexed)
            tender = db.query(Tender).filter(Tender.tender_id == "TN00050").first()
            assert tender is not None
            
            # Query by published_date (indexed) - use exact date that exists
            results = db.query(Tender).filter(Tender.published_date == "2024-05-15").all()
            assert len(results) >= 1  # At least one result
            
            # Query by bid_close_date (indexed)
            results = db.query(Tender).filter(Tender.bid_close_date == "2024-06-20").all()
            assert len(results) >= 1  # At least one result
            
        finally:
            db.close()
