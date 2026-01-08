-- Migration script to rename 'metadata' columns to avoid SQLAlchemy reserved name conflict
-- Run this if you already have the mortgage tables created with 'metadata' columns
-- 
-- Usage:
--   psql -U username -d database_name -f rename_metadata_columns.sql

-- Rename metadata column in mortgage_applications table
ALTER TABLE mortgage_applications 
    RENAME COLUMN metadata TO app_metadata;

-- Rename metadata column in mortgage_documents table
ALTER TABLE mortgage_documents 
    RENAME COLUMN metadata TO doc_metadata;

-- Add comments
COMMENT ON COLUMN mortgage_applications.app_metadata IS 'Additional flexible data (renamed from metadata - SQLAlchemy reserved)';
COMMENT ON COLUMN mortgage_documents.doc_metadata IS 'Document-specific metadata (renamed from metadata - SQLAlchemy reserved)';
