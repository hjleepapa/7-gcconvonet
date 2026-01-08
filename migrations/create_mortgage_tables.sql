-- Mortgage Application Database Schema
-- PostgreSQL SQL Script
-- 
-- This script creates the necessary tables for the mortgage application system.
-- Tables include: mortgage_applications, mortgage_documents, mortgage_debts, mortgage_application_notes
--
-- Usage:
--   psql -U username -d database_name -f create_mortgage_tables.sql

-- Drop existing tables (in reverse order of dependencies)
DROP TABLE IF EXISTS mortgage_application_notes CASCADE;
DROP TABLE IF EXISTS mortgage_debts CASCADE;
DROP TABLE IF EXISTS mortgage_documents CASCADE;
DROP TABLE IF EXISTS mortgage_applications CASCADE;

-- Create enum types
CREATE TYPE application_status AS ENUM (
    'draft',
    'financial_review',
    'document_collection',
    'document_verification',
    'under_review',
    'pre_approved',
    'approved',
    'rejected',
    'cancelled'
);

CREATE TYPE document_type AS ENUM (
    'identification',
    'income_paystub',
    'income_w2',
    'income_tax_return',
    'income_pnl',
    'income_1099',
    'asset_bank_statement',
    'asset_investment',
    'asset_retirement',
    'debt_credit_card',
    'debt_student_loan',
    'debt_auto_loan',
    'down_payment_source',
    'down_payment_gift_letter'
);

CREATE TYPE document_status AS ENUM (
    'pending',
    'uploaded',
    'verified',
    'rejected'
);

-- Create mortgage_applications table
CREATE TABLE mortgage_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users_anthropic(id) ON DELETE CASCADE,
    
    -- Application status
    status application_status NOT NULL DEFAULT 'draft',
    
    -- Financial Information (Step 1: Review Finances)
    credit_score INTEGER,
    credit_history_years INTEGER,
    dti_ratio NUMERIC(5, 2),  -- Debt-to-income ratio (percentage)
    monthly_income NUMERIC(12, 2),
    monthly_debt NUMERIC(12, 2),
    down_payment_amount NUMERIC(12, 2),
    closing_costs_estimate NUMERIC(12, 2),
    total_savings NUMERIC(12, 2),
    
    -- Loan preferences
    loan_type VARCHAR(50),  -- conventional, FHA, VA, etc.
    loan_amount NUMERIC(12, 2),
    property_value NUMERIC(12, 2),
    
    -- Progress tracking
    financial_review_completed BOOLEAN NOT NULL DEFAULT FALSE,
    document_collection_completed BOOLEAN NOT NULL DEFAULT FALSE,
    document_verification_completed BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Additional metadata
    app_metadata JSONB,  -- Renamed from 'metadata' (SQLAlchemy reserved)
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create mortgage_documents table
CREATE TABLE mortgage_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES mortgage_applications(id) ON DELETE CASCADE,
    
    -- Document information
    document_type document_type NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_url VARCHAR(500),
    file_size INTEGER,  -- Size in bytes
    mime_type VARCHAR(100),
    
    -- Document status
    status document_status NOT NULL DEFAULT 'pending',
    
    -- Verification details
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID,  -- User ID of verifier
    verification_notes TEXT,
    rejection_reason TEXT,
    
    -- Document metadata
    doc_metadata JSONB,  -- Renamed from 'metadata' (SQLAlchemy reserved)
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    uploaded_at TIMESTAMP WITH TIME ZONE
);

-- Create mortgage_debts table
CREATE TABLE mortgage_debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES mortgage_applications(id) ON DELETE CASCADE,
    
    -- Debt information
    debt_type VARCHAR(50) NOT NULL,  -- credit_card, student_loan, auto_loan, mortgage, other
    creditor_name VARCHAR(255),
    account_number VARCHAR(100),  -- Last 4 digits or masked
    monthly_payment NUMERIC(10, 2) NOT NULL,
    outstanding_balance NUMERIC(12, 2),
    interest_rate NUMERIC(5, 2),  -- Annual percentage rate
    
    -- Additional details
    description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create mortgage_application_notes table
CREATE TABLE mortgage_application_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES mortgage_applications(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users_anthropic(id) ON DELETE CASCADE,
    
    -- Note content
    note_text TEXT NOT NULL,
    note_type VARCHAR(50),  -- system, user, agent, verification
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_mortgage_applications_user_id ON mortgage_applications(user_id);
CREATE INDEX idx_mortgage_applications_status ON mortgage_applications(status);
CREATE INDEX idx_mortgage_applications_created_at ON mortgage_applications(created_at);

CREATE INDEX idx_mortgage_documents_application_id ON mortgage_documents(application_id);
CREATE INDEX idx_mortgage_documents_type ON mortgage_documents(document_type);
CREATE INDEX idx_mortgage_documents_status ON mortgage_documents(status);

CREATE INDEX idx_mortgage_debts_application_id ON mortgage_debts(application_id);
CREATE INDEX idx_mortgage_debts_type ON mortgage_debts(debt_type);

CREATE INDEX idx_mortgage_notes_application_id ON mortgage_application_notes(application_id);
CREATE INDEX idx_mortgage_notes_user_id ON mortgage_application_notes(user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_mortgage_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER mortgage_applications_updated_at
    BEFORE UPDATE ON mortgage_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_mortgage_updated_at();

CREATE TRIGGER mortgage_documents_updated_at
    BEFORE UPDATE ON mortgage_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_mortgage_updated_at();

CREATE TRIGGER mortgage_debts_updated_at
    BEFORE UPDATE ON mortgage_debts
    FOR EACH ROW
    EXECUTE FUNCTION update_mortgage_updated_at();

-- Add comments for documentation
COMMENT ON TABLE mortgage_applications IS 'Main mortgage application table storing financial information and application status';
COMMENT ON TABLE mortgage_documents IS 'Documents uploaded for mortgage applications';
COMMENT ON TABLE mortgage_debts IS 'Debt information for mortgage applications';
COMMENT ON TABLE mortgage_application_notes IS 'Notes and comments on mortgage applications';

COMMENT ON COLUMN mortgage_applications.dti_ratio IS 'Debt-to-income ratio as percentage (e.g., 43.50 for 43.5%)';
COMMENT ON COLUMN mortgage_applications.financial_review_completed IS 'True when credit score, income, and debt information are collected';
COMMENT ON COLUMN mortgage_applications.document_collection_completed IS 'True when all required documents are uploaded';
COMMENT ON COLUMN mortgage_applications.document_verification_completed IS 'True when all documents are verified';
