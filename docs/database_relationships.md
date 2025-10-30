# Database Relationships Documentation

## Overview

The Tender360 Data Engine uses SQLAlchemy ORM to define relationships between database tables. This document explains the relationship structure and cascade behaviors.

## Entity Relationship Diagram

```
┌──────────────┐
│   Tender     │◄──────────────┐
│  (Parent)    │                │
└──────┬───────┘                │
       │                        │
       │ 1:1                    │
       ▼                        │
┌──────────────┐                │
│TenderDetail  │                │
│   (Child)    │                │
└──────────────┘                │
                                │ Many-to-One
       ┌────────────────────────┘
       │
       │ 1:Many
       ▼
┌──────────────┐
│  Document    │◄──────────────┐
│   (Child)    │                │
└──────┬───────┘                │
       │                        │
       │ 1:Many                 │
       ▼                        │ Many-to-One
┌──────────────┐                │
│ExtractedField│                │
│   (Child)    │────────────────┘
└──────────────┘

┌──────────────┐
│  ScrapeLog   │  (Standalone - No relationships)
└──────────────┘
```

## Relationship Types

### 1. Tender ←→ TenderDetail (One-to-One)

**Description**: Each tender can have exactly one detail record containing extended information.

**Implementation**:
```python
# In Tender model
details = relationship(
    "TenderDetail", 
    back_populates="tender", 
    uselist=False,  # Ensures one-to-one
    cascade="all, delete-orphan"
)

# In TenderDetail model
tender = relationship("Tender", back_populates="details")
```

**Cascade Behavior**:
- When a `Tender` is deleted, its associated `TenderDetail` is automatically deleted
- Orphaned `TenderDetail` records (without a parent tender) are automatically deleted

**Use Case**:
- Store extended tender information separately for better query performance
- Basic tender info in main table, detailed terms/conditions in detail table

### 2. Tender → Document (One-to-Many)

**Description**: Each tender can have multiple associated documents (PDFs, Excel files, etc.).

**Implementation**:
```python
# In Tender model
documents = relationship(
    "Document", 
    back_populates="tender",
    cascade="all, delete-orphan"
)

# In Document model
tender = relationship("Tender", back_populates="documents")
```

**Cascade Behavior**:
- When a `Tender` is deleted, all its associated `Document` records are automatically deleted
- This ensures no orphaned document metadata remains in the database

**Use Case**:
- Track all documents attached to a tender notice
- Maintain download status and file metadata

### 3. Tender → ExtractedField (One-to-Many)

**Description**: Each tender can have multiple extracted fields parsed from its documents.

**Implementation**:
```python
# In Tender model
extracted_fields = relationship(
    "ExtractedField", 
    back_populates="tender",
    cascade="all, delete-orphan"
)

# In ExtractedField model
tender = relationship("Tender", back_populates="extracted_fields")
```

**Cascade Behavior**:
- When a `Tender` is deleted, all its associated `ExtractedField` records are automatically deleted
- Ensures data integrity when removing tender records

**Use Case**:
- Store parsed data like EMD amount, tender fee, deadlines, etc.
- Link extracted data back to the source tender

### 4. Document → ExtractedField (One-to-Many)

**Description**: Each document can have multiple fields extracted from it.

**Implementation**:
```python
# In Document model
extracted_fields = relationship(
    "ExtractedField", 
    back_populates="document",
    cascade="all, delete-orphan"
)

# In ExtractedField model
document = relationship("Document", back_populates="extracted_fields")
```

**Cascade Behavior**:
- When a `Document` is deleted, all fields extracted from it are automatically deleted
- Maintains referential integrity between documents and extracted data

**Use Case**:
- Track which document each field was extracted from
- Enable document-specific field queries

### 5. ExtractedField (Dual Parent Relationship)

**Special Note**: `ExtractedField` has a unique characteristic - it belongs to both a `Tender` and a `Document`.

**Why Both?**:
- **Tender relationship**: Enables queries like "get all extracted fields for a tender"
- **Document relationship**: Enables queries like "get all fields from this specific document"

**Foreign Keys**:
```python
tender_id = Column(String(100), ForeignKey("tenders.tender_id"))
document_id = Column(Integer, ForeignKey("documents.id"))
```

### 6. ScrapeLog (No Relationships)

**Description**: Standalone audit log table with no relationships to other entities.

**Why No Relationships?**:
- Pure audit trail for monitoring scraping sessions
- Should persist even if tender data is deleted
- Independent lifecycle from business data

## Cascade Delete Chains

### Complete Cascade Chain

When a `Tender` is deleted, the following cascade occurs:

```
DELETE Tender
    ↓
    ├─→ DELETE TenderDetail (via cascade)
    ├─→ DELETE Documents (via cascade)
    │       ↓
    │       └─→ DELETE ExtractedFields from Documents (via cascade)
    └─→ DELETE ExtractedFields directly linked (via cascade)
```

**Result**: All related data is cleaned up automatically, maintaining database integrity.

### Partial Delete

When a single `Document` is deleted:

```
DELETE Document
    ↓
    └─→ DELETE ExtractedFields from that Document (via cascade)
```

**Result**: Only fields extracted from that document are deleted. The tender and other documents remain intact.

## Best Practices

### 1. Always Use Session Context
```python
from src.database.operations import create_tender, save_document

# Create tender first
tender = create_tender(db, tender_data)

# Then create related records
document = save_document(db, tender.tender_id, doc_data)
```

### 2. Let Cascade Handle Deletions
```python
# Delete tender - related records deleted automatically
db.delete(tender)
db.commit()
```

### 3. Query Using Relationships
```python
# Get all documents for a tender
tender = db.query(Tender).filter_by(tender_id="T001").first()
documents = tender.documents  # Uses relationship

# Get tender from a document
document = db.query(Document).filter_by(id=123).first()
parent_tender = document.tender  # Uses relationship
```

### 4. Avoid Manual Foreign Key Management
```python
# ✅ Good - Let the relationship handle it
tender.documents.append(document)

# ❌ Bad - Manual FK management
document.tender_id = tender.tender_id
```

## Testing Relationships

All relationships are thoroughly tested:
- **test_database_models.py**: Tests basic relationship functionality
- **test_database_operations.py**: Tests CRUD operations using relationships
- **test_cascade_relationships.py**: Tests cascade delete behavior

Run tests:
```bash
pytest tests/unit/test_database_models.py -v
pytest tests/unit/test_cascade_relationships.py -v
```

## Foreign Key Constraints

### SQLite Note
The test suite uses SQLite which doesn't enforce foreign key constraints by default. In production with PostgreSQL/MySQL:
- Foreign keys are enforced
- Orphaned records cannot be created
- Cascade deletes work automatically

### Production Considerations
When using PostgreSQL or MySQL in production:
```python
# Enable foreign key constraints
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)
```

## Migration Considerations

When modifying relationships:
1. Always create a database migration
2. Test cascade behavior in staging first
3. Backup production data before applying
4. Consider adding indexes on foreign key columns for performance

## Summary

The database schema implements a hierarchical relationship structure:
- **Tender** is the root entity
- **TenderDetail**, **Document**, and **ExtractedField** are children
- **ExtractedField** has dual parentage (Tender and Document)
- **ScrapeLog** is independent

All parent-child relationships use `cascade="all, delete-orphan"` to maintain data integrity and automatically clean up related records when parents are deleted.
