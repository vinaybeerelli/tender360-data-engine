"""
Unit tests for cascade delete relationships.

Tests to verify that cascade delete operations work correctly for the relationships.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import (
    Tender, TenderDetail, Document, ExtractedField
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


class TestCascadeDeletes:
    """Tests for cascade delete operations."""
    
    def test_tender_delete_cascades_to_details(self, db_session):
        """Test that deleting a tender also deletes its detail record."""
        # Create tender with details
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        detail = TenderDetail(tender_id="TEST001", eligibility="Test eligibility")
        
        db_session.add(tender)
        db_session.add(detail)
        db_session.commit()
        
        # Verify both exist
        assert db_session.query(Tender).count() == 1
        assert db_session.query(TenderDetail).count() == 1
        
        # Delete tender
        db_session.delete(tender)
        db_session.commit()
        
        # Verify cascade delete worked
        assert db_session.query(Tender).count() == 0
        assert db_session.query(TenderDetail).count() == 0
    
    def test_tender_delete_cascades_to_documents(self, db_session):
        """Test that deleting a tender also deletes all its documents."""
        # Create tender with multiple documents
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        doc1 = Document(tender_id="TEST001", filename="doc1.pdf")
        doc2 = Document(tender_id="TEST001", filename="doc2.pdf")
        doc3 = Document(tender_id="TEST001", filename="doc3.xlsx")
        
        db_session.add(tender)
        db_session.add_all([doc1, doc2, doc3])
        db_session.commit()
        
        # Verify all exist
        assert db_session.query(Tender).count() == 1
        assert db_session.query(Document).count() == 3
        
        # Delete tender
        db_session.delete(tender)
        db_session.commit()
        
        # Verify cascade delete worked
        assert db_session.query(Tender).count() == 0
        assert db_session.query(Document).count() == 0
    
    def test_tender_delete_cascades_to_extracted_fields(self, db_session):
        """Test that deleting a tender also deletes all its extracted fields."""
        # Create tender with documents and extracted fields
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        document = Document(tender_id="TEST001", filename="test.pdf")
        
        db_session.add(tender)
        db_session.add(document)
        db_session.commit()
        
        # Create extracted fields
        field1 = ExtractedField(
            tender_id="TEST001",
            document_id=document.id,
            field_name="emd",
            field_value="50000"
        )
        field2 = ExtractedField(
            tender_id="TEST001",
            document_id=document.id,
            field_name="tender_fee",
            field_value="1000"
        )
        
        db_session.add_all([field1, field2])
        db_session.commit()
        
        # Verify all exist
        assert db_session.query(Tender).count() == 1
        assert db_session.query(Document).count() == 1
        assert db_session.query(ExtractedField).count() == 2
        
        # Delete tender
        db_session.delete(tender)
        db_session.commit()
        
        # Verify cascade delete worked for all related records
        assert db_session.query(Tender).count() == 0
        assert db_session.query(Document).count() == 0
        assert db_session.query(ExtractedField).count() == 0
    
    def test_document_delete_cascades_to_extracted_fields(self, db_session):
        """Test that deleting a document also deletes its extracted fields."""
        # Create tender with document and extracted fields
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        document = Document(tender_id="TEST001", filename="test.pdf")
        
        db_session.add(tender)
        db_session.add(document)
        db_session.commit()
        
        # Create extracted fields
        field1 = ExtractedField(
            tender_id="TEST001",
            document_id=document.id,
            field_name="emd",
            field_value="50000"
        )
        field2 = ExtractedField(
            tender_id="TEST001",
            document_id=document.id,
            field_name="tender_fee",
            field_value="1000"
        )
        
        db_session.add_all([field1, field2])
        db_session.commit()
        
        # Verify all exist
        assert db_session.query(Document).count() == 1
        assert db_session.query(ExtractedField).count() == 2
        
        # Delete document only
        db_session.delete(document)
        db_session.commit()
        
        # Verify cascade delete worked for extracted fields but tender remains
        assert db_session.query(Tender).count() == 1
        assert db_session.query(Document).count() == 0
        assert db_session.query(ExtractedField).count() == 0
    
    def test_complete_cascade_delete_chain(self, db_session):
        """Test complete cascade delete chain from tender to all children."""
        # Create a complete data structure
        tender = Tender(
            tender_id="TEST001",
            department="Test Dept",
            work_name="Test Work"
        )
        
        # Add tender details
        detail = TenderDetail(
            tender_id="TEST001",
            eligibility="Test eligibility",
            general_terms="Test terms"
        )
        
        # Add multiple documents
        doc1 = Document(tender_id="TEST001", filename="doc1.pdf")
        doc2 = Document(tender_id="TEST001", filename="doc2.xlsx")
        
        db_session.add(tender)
        db_session.add(detail)
        db_session.add_all([doc1, doc2])
        db_session.commit()
        
        # Add extracted fields for each document
        field1 = ExtractedField(
            tender_id="TEST001",
            document_id=doc1.id,
            field_name="emd",
            field_value="50000"
        )
        field2 = ExtractedField(
            tender_id="TEST001",
            document_id=doc1.id,
            field_name="tender_fee",
            field_value="1000"
        )
        field3 = ExtractedField(
            tender_id="TEST001",
            document_id=doc2.id,
            field_name="deadline",
            field_value="2024-12-31"
        )
        
        db_session.add_all([field1, field2, field3])
        db_session.commit()
        
        # Verify all records exist
        assert db_session.query(Tender).count() == 1
        assert db_session.query(TenderDetail).count() == 1
        assert db_session.query(Document).count() == 2
        assert db_session.query(ExtractedField).count() == 3
        
        # Delete the root tender
        db_session.delete(tender)
        db_session.commit()
        
        # Verify entire tree was deleted
        assert db_session.query(Tender).count() == 0
        assert db_session.query(TenderDetail).count() == 0
        assert db_session.query(Document).count() == 0
        assert db_session.query(ExtractedField).count() == 0
    
    def test_selective_document_deletion(self, db_session):
        """Test that deleting one document doesn't affect others."""
        # Create tender with multiple documents
        tender = Tender(tender_id="TEST001", work_name="Test Work")
        doc1 = Document(tender_id="TEST001", filename="doc1.pdf")
        doc2 = Document(tender_id="TEST001", filename="doc2.pdf")
        
        db_session.add(tender)
        db_session.add_all([doc1, doc2])
        db_session.commit()
        
        # Add fields to both documents
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
        
        # Verify all exist
        assert db_session.query(Document).count() == 2
        assert db_session.query(ExtractedField).count() == 2
        
        # Delete only doc1
        db_session.delete(doc1)
        db_session.commit()
        
        # Verify selective deletion
        assert db_session.query(Tender).count() == 1
        assert db_session.query(Document).count() == 1
        assert db_session.query(ExtractedField).count() == 1
        
        # Verify the remaining document is doc2
        remaining_doc = db_session.query(Document).first()
        assert remaining_doc.filename == "doc2.pdf"
        
        # Verify the remaining field belongs to doc2
        remaining_field = db_session.query(ExtractedField).first()
        assert remaining_field.document_id == doc2.id
        assert remaining_field.field_name == "tender_fee"
