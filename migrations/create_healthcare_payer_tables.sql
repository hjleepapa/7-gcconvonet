-- Healthcare Payer Tables Migration
-- Creates all tables required for healthcare payer member services

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Claim status enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'claim_status') THEN
        CREATE TYPE claim_status AS ENUM (
            'submitted',
            'processing',
            'pending_info',
            'approved',
            'partially_approved',
            'denied',
            'paid',
            'appealed',
            'appeal_approved',
            'appeal_denied'
        );
    END IF;
END$$;

-- Denial reason enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'denial_reason') THEN
        CREATE TYPE denial_reason AS ENUM (
            'not_covered',
            'out_of_network',
            'no_prior_auth',
            'not_medically_necessary',
            'duplicate_claim',
            'timely_filing',
            'coordination_of_benefits',
            'max_benefit_reached',
            'incomplete_info',
            'experimental',
            'pre_existing_condition'
        );
    END IF;
END$$;

-- Prior authorization status enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'prior_auth_status') THEN
        CREATE TYPE prior_auth_status AS ENUM (
            'pending',
            'approved',
            'denied',
            'expired',
            'cancelled',
            'additional_info_needed'
        );
    END IF;
END$$;

-- Eligibility status enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'eligibility_status') THEN
        CREATE TYPE eligibility_status AS ENUM (
            'active',
            'inactive',
            'pending',
            'terminated',
            'cobra',
            'suspended'
        );
    END IF;
END$$;

-- Network tier enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'network_tier') THEN
        CREATE TYPE network_tier AS ENUM (
            'tier_1',
            'tier_2',
            'tier_3'
        );
    END IF;
END$$;

-- Service category enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'service_category') THEN
        CREATE TYPE service_category AS ENUM (
            'office_visit',
            'specialist_visit',
            'emergency',
            'urgent_care',
            'hospital_inpatient',
            'hospital_outpatient',
            'surgery',
            'diagnostic_lab',
            'diagnostic_imaging',
            'preventive',
            'mental_health',
            'physical_therapy',
            'durable_medical_equipment',
            'prescription'
        );
    END IF;
END$$;

-- ============================================================================
-- HEALTHCARE PLANS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS healthcare_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(255) NOT NULL,
    plan_type VARCHAR(50) NOT NULL,
    
    -- Plan year
    plan_year_start TIMESTAMP WITH TIME ZONE NOT NULL,
    plan_year_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Deductibles - Individual
    individual_deductible_in_network NUMERIC(10, 2) NOT NULL,
    individual_deductible_out_of_network NUMERIC(10, 2),
    
    -- Deductibles - Family
    family_deductible_in_network NUMERIC(10, 2),
    family_deductible_out_of_network NUMERIC(10, 2),
    
    -- Out-of-Pocket Maximum - Individual
    individual_oop_max_in_network NUMERIC(10, 2) NOT NULL,
    individual_oop_max_out_of_network NUMERIC(10, 2),
    
    -- Out-of-Pocket Maximum - Family
    family_oop_max_in_network NUMERIC(10, 2),
    family_oop_max_out_of_network NUMERIC(10, 2),
    
    -- Default cost-sharing
    default_copay NUMERIC(8, 2) DEFAULT 30,
    default_coinsurance NUMERIC(5, 2) DEFAULT 20,
    
    -- Plan features
    requires_referral BOOLEAN DEFAULT FALSE,
    has_pharmacy_benefit BOOLEAN DEFAULT TRUE,
    has_mental_health_parity BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    plan_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_healthcare_plans_plan_code ON healthcare_plans(plan_code);

-- ============================================================================
-- HEALTHCARE MEMBERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS healthcare_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users_anthropic(id) NOT NULL UNIQUE,
    
    -- Member identification
    member_number VARCHAR(50) UNIQUE NOT NULL,
    group_number VARCHAR(50),
    subscriber_id UUID,
    
    -- Plan information
    plan_id UUID REFERENCES healthcare_plans(id) NOT NULL,
    plan_name VARCHAR(255),
    
    -- Eligibility
    eligibility_status VARCHAR(50) DEFAULT 'active' NOT NULL,
    coverage_start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    coverage_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Demographics
    date_of_birth TIMESTAMP WITH TIME ZONE,
    relationship_to_subscriber VARCHAR(50) DEFAULT 'self',
    
    -- Contact preferences
    preferred_contact_method VARCHAR(50) DEFAULT 'email',
    preferred_language VARCHAR(10) DEFAULT 'en',
    
    -- Metadata
    member_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_healthcare_members_user_id ON healthcare_members(user_id);
CREATE INDEX IF NOT EXISTS ix_healthcare_members_member_number ON healthcare_members(member_number);
CREATE INDEX IF NOT EXISTS ix_healthcare_members_group_number ON healthcare_members(group_number);
CREATE INDEX IF NOT EXISTS ix_healthcare_members_eligibility_status ON healthcare_members(eligibility_status);

-- ============================================================================
-- PLAN BENEFITS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS plan_benefits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES healthcare_plans(id) NOT NULL,
    
    -- Benefit identification
    service_category VARCHAR(50) NOT NULL,
    
    -- Coverage details
    is_covered BOOLEAN DEFAULT TRUE NOT NULL,
    requires_prior_auth BOOLEAN DEFAULT FALSE,
    requires_referral BOOLEAN DEFAULT FALSE,
    
    -- Cost-sharing - In-Network
    copay_in_network NUMERIC(8, 2),
    coinsurance_in_network NUMERIC(5, 2),
    
    -- Cost-sharing - Out-of-Network
    copay_out_of_network NUMERIC(8, 2),
    coinsurance_out_of_network NUMERIC(5, 2),
    
    -- Limits
    annual_limit INTEGER,
    lifetime_limit NUMERIC(12, 2),
    
    -- Notes
    coverage_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_plan_benefits_plan_id ON plan_benefits(plan_id);
CREATE INDEX IF NOT EXISTS ix_plan_benefits_service_category ON plan_benefits(service_category);

-- ============================================================================
-- PRIOR AUTHORIZATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS prior_authorizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES healthcare_members(id) NOT NULL,
    
    -- Authorization identification
    auth_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Request details
    procedure_code VARCHAR(20) NOT NULL,
    procedure_description VARCHAR(500),
    diagnosis_codes JSONB,
    
    -- Provider information
    requesting_provider_npi VARCHAR(10),
    requesting_provider_name VARCHAR(255),
    servicing_provider_npi VARCHAR(10),
    servicing_provider_name VARCHAR(255),
    
    -- Clinical information
    clinical_notes TEXT,
    supporting_documents JSONB,
    
    -- Authorization status
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    
    -- Decision details
    decision_reason TEXT,
    reviewer_notes TEXT,
    
    -- Approved details
    approved_units INTEGER,
    approved_from_date TIMESTAMP WITH TIME ZONE,
    approved_to_date TIMESTAMP WITH TIME ZONE,
    
    -- Dates
    requested_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    decision_date TIMESTAMP WITH TIME ZONE,
    expiration_date TIMESTAMP WITH TIME ZONE,
    
    -- Urgency
    is_urgent BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    auth_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_prior_authorizations_member_id ON prior_authorizations(member_id);
CREATE INDEX IF NOT EXISTS ix_prior_authorizations_auth_number ON prior_authorizations(auth_number);
CREATE INDEX IF NOT EXISTS ix_prior_authorizations_status ON prior_authorizations(status);

-- ============================================================================
-- HEALTHCARE CLAIMS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS healthcare_claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES healthcare_members(id) NOT NULL,
    
    -- Claim identification
    claim_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Service information
    service_date TIMESTAMP WITH TIME ZONE NOT NULL,
    service_date_end TIMESTAMP WITH TIME ZONE,
    place_of_service VARCHAR(100),
    
    -- Provider information
    provider_npi VARCHAR(10),
    provider_name VARCHAR(255),
    provider_network_tier VARCHAR(50),
    
    -- Diagnosis and procedure codes
    diagnosis_codes JSONB,
    procedure_codes JSONB,
    
    -- Financial - Billed
    billed_amount NUMERIC(12, 2) NOT NULL,
    
    -- Financial - Adjudicated
    allowed_amount NUMERIC(12, 2),
    paid_amount NUMERIC(12, 2),
    member_responsibility NUMERIC(12, 2),
    
    -- Member cost breakdown
    deductible_applied NUMERIC(10, 2) DEFAULT 0,
    copay_applied NUMERIC(10, 2) DEFAULT 0,
    coinsurance_applied NUMERIC(10, 2) DEFAULT 0,
    
    -- Claim status
    status VARCHAR(50) DEFAULT 'submitted' NOT NULL,
    
    -- Denial information
    denial_reason VARCHAR(50),
    denial_details TEXT,
    
    -- Prior authorization reference
    prior_auth_id UUID REFERENCES prior_authorizations(id),
    
    -- Processing dates
    received_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_date TIMESTAMP WITH TIME ZONE,
    paid_date TIMESTAMP WITH TIME ZONE,
    
    -- Appeal tracking
    is_appealed BOOLEAN DEFAULT FALSE,
    appeal_date TIMESTAMP WITH TIME ZONE,
    appeal_reason TEXT,
    appeal_decision VARCHAR(50),
    appeal_decision_date TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    claim_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_healthcare_claims_member_id ON healthcare_claims(member_id);
CREATE INDEX IF NOT EXISTS ix_healthcare_claims_claim_number ON healthcare_claims(claim_number);
CREATE INDEX IF NOT EXISTS ix_healthcare_claims_provider_npi ON healthcare_claims(provider_npi);
CREATE INDEX IF NOT EXISTS ix_healthcare_claims_status ON healthcare_claims(status);
CREATE INDEX IF NOT EXISTS ix_claims_member_date ON healthcare_claims(member_id, service_date);
CREATE INDEX IF NOT EXISTS ix_claims_member_status ON healthcare_claims(member_id, status);

-- ============================================================================
-- CLAIM LINE ITEMS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS claim_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID REFERENCES healthcare_claims(id) NOT NULL,
    
    -- Line item details
    line_number INTEGER NOT NULL,
    procedure_code VARCHAR(20) NOT NULL,
    procedure_description VARCHAR(500),
    modifier_codes JSONB,
    
    -- Diagnosis link
    diagnosis_pointer INTEGER,
    
    -- Quantity and amounts
    units INTEGER DEFAULT 1,
    billed_amount NUMERIC(10, 2) NOT NULL,
    allowed_amount NUMERIC(10, 2),
    paid_amount NUMERIC(10, 2),
    
    -- Adjudication
    is_covered BOOLEAN DEFAULT TRUE,
    denial_reason VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_claim_line_items_claim_id ON claim_line_items(claim_id);

-- ============================================================================
-- MEMBER ACCUMULATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS member_accumulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES healthcare_members(id) NOT NULL,
    
    -- Plan year
    plan_year INTEGER NOT NULL,
    
    -- Deductible accumulation
    individual_deductible_met_in_network NUMERIC(10, 2) DEFAULT 0,
    individual_deductible_met_out_of_network NUMERIC(10, 2) DEFAULT 0,
    family_deductible_met_in_network NUMERIC(10, 2) DEFAULT 0,
    family_deductible_met_out_of_network NUMERIC(10, 2) DEFAULT 0,
    
    -- Out-of-pocket accumulation
    individual_oop_met_in_network NUMERIC(10, 2) DEFAULT 0,
    individual_oop_met_out_of_network NUMERIC(10, 2) DEFAULT 0,
    family_oop_met_in_network NUMERIC(10, 2) DEFAULT 0,
    family_oop_met_out_of_network NUMERIC(10, 2) DEFAULT 0,
    
    -- Timestamps
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    UNIQUE (member_id, plan_year)
);

CREATE INDEX IF NOT EXISTS ix_accumulations_member_year ON member_accumulations(member_id, plan_year);

-- ============================================================================
-- HEALTHCARE PROVIDERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS healthcare_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Provider identification
    npi VARCHAR(10) UNIQUE NOT NULL,
    tax_id VARCHAR(20),
    
    -- Provider information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    organization_name VARCHAR(255),
    
    -- Specialty
    primary_specialty VARCHAR(100),
    secondary_specialties JSONB,
    
    -- Contact information
    phone VARCHAR(20),
    fax VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    
    -- Address
    address_line_1 VARCHAR(255),
    address_line_2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    
    -- Network status
    network_tier VARCHAR(50) DEFAULT 'tier_2' NOT NULL,
    is_accepting_patients BOOLEAN DEFAULT TRUE,
    
    -- Quality metrics
    quality_rating NUMERIC(3, 2),
    patient_reviews_count INTEGER DEFAULT 0,
    
    -- Languages spoken
    languages JSONB,
    
    -- Hospital affiliations
    hospital_affiliations JSONB,
    
    -- Metadata
    provider_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_healthcare_providers_npi ON healthcare_providers(npi);
CREATE INDEX IF NOT EXISTS ix_healthcare_providers_zip_code ON healthcare_providers(zip_code);
CREATE INDEX IF NOT EXISTS ix_healthcare_providers_network_tier ON healthcare_providers(network_tier);
CREATE INDEX IF NOT EXISTS ix_provider_specialty_zip ON healthcare_providers(primary_specialty, zip_code);
CREATE INDEX IF NOT EXISTS ix_provider_network_zip ON healthcare_providers(network_tier, zip_code);

-- ============================================================================
-- CARE PROGRAMS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS care_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Program identification
    program_code VARCHAR(50) UNIQUE NOT NULL,
    program_name VARCHAR(255) NOT NULL,
    program_type VARCHAR(100) NOT NULL,
    
    -- Program details
    description TEXT,
    eligibility_criteria TEXT,
    
    -- Target conditions
    target_conditions JSONB,
    
    -- Program features
    includes_coaching BOOLEAN DEFAULT FALSE,
    includes_monitoring BOOLEAN DEFAULT FALSE,
    includes_rewards BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_care_programs_program_code ON care_programs(program_code);

-- ============================================================================
-- MEMBER CARE PROGRAMS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS member_care_programs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES healthcare_members(id) NOT NULL,
    program_id UUID REFERENCES care_programs(id) NOT NULL,
    
    -- Enrollment status
    enrolled_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    disenrolled_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Progress tracking
    completion_percentage NUMERIC(5, 2) DEFAULT 0,
    last_activity_date TIMESTAMP WITH TIME ZONE,
    
    -- Notes
    enrollment_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    UNIQUE (member_id, program_id)
);

CREATE INDEX IF NOT EXISTS ix_member_care_programs_member_id ON member_care_programs(member_id);
CREATE INDEX IF NOT EXISTS ix_member_care_programs_program_id ON member_care_programs(program_id);
CREATE INDEX IF NOT EXISTS ix_member_program ON member_care_programs(member_id, program_id);

-- ============================================================================
-- INSERT SAMPLE DATA
-- ============================================================================

-- Insert sample plan
INSERT INTO healthcare_plans (
    plan_code, plan_name, plan_type,
    plan_year_start, plan_year_end,
    individual_deductible_in_network, individual_deductible_out_of_network,
    family_deductible_in_network, family_deductible_out_of_network,
    individual_oop_max_in_network, individual_oop_max_out_of_network,
    family_oop_max_in_network, family_oop_max_out_of_network
) VALUES (
    'PPO-GOLD-2025', 'Convonet Gold PPO', 'PPO',
    '2025-01-01', '2025-12-31',
    1500.00, 3000.00,
    3000.00, 6000.00,
    6500.00, 13000.00,
    13000.00, 26000.00
) ON CONFLICT (plan_code) DO NOTHING;

-- Insert sample benefits for the plan
INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'office_visit', true, 30.00, 20.00, 60.00, 40.00, false
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'specialist_visit', true, 50.00, 20.00, 100.00, 40.00, false
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'emergency', true, 250.00, 20.00, 250.00, 40.00, false
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'urgent_care', true, 75.00, 20.00, 150.00, 40.00, false
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'hospital_inpatient', true, NULL, 20.00, NULL, 40.00, true
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'surgery', true, NULL, 20.00, NULL, 40.00, true
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'diagnostic_lab', true, 0.00, 10.00, NULL, 40.00, false
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'diagnostic_imaging', true, 100.00, 20.00, NULL, 40.00, true
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'preventive', true, 0.00, 0.00, NULL, 40.00, false
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth)
SELECT p.id, 'mental_health', true, 30.00, 20.00, 60.00, 40.00, false
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

INSERT INTO plan_benefits (plan_id, service_category, is_covered, copay_in_network, coinsurance_in_network, copay_out_of_network, coinsurance_out_of_network, requires_prior_auth, annual_limit)
SELECT p.id, 'physical_therapy', true, 40.00, 20.00, 80.00, 40.00, true, 30
FROM healthcare_plans p WHERE p.plan_code = 'PPO-GOLD-2025'
ON CONFLICT DO NOTHING;

-- Insert sample care programs
INSERT INTO care_programs (program_code, program_name, program_type, description, includes_coaching, includes_monitoring, includes_rewards, target_conditions)
VALUES 
('DM-DIABETES', 'Diabetes Management Program', 'disease_management', 'Comprehensive diabetes management including coaching, monitoring, and supplies coordination.', true, true, true, '["diabetes", "prediabetes"]'),
('DM-HEART', 'Heart Health Program', 'disease_management', 'Cardiac care program for members with heart disease or high cardiovascular risk.', true, true, true, '["heart disease", "hypertension", "high cholesterol"]'),
('WELLNESS-360', 'Wellness 360', 'wellness', 'Complete wellness program with fitness tracking, nutrition coaching, and preventive care reminders.', true, false, true, NULL),
('MATERNITY', 'Maternity Care Program', 'chronic_care', 'Support throughout pregnancy including prenatal education and postpartum care.', true, true, false, '["pregnancy"]')
ON CONFLICT (program_code) DO NOTHING;

-- Insert sample providers
INSERT INTO healthcare_providers (npi, first_name, last_name, primary_specialty, phone, address_line_1, city, state, zip_code, network_tier, quality_rating, languages)
VALUES 
('1234567890', 'Sarah', 'Johnson', 'Family Medicine', '555-0101', '100 Medical Center Dr', 'San Francisco', 'CA', '94102', 'tier_1', 4.8, '["English", "Spanish"]'),
('2345678901', 'Michael', 'Chen', 'Cardiology', '555-0102', '200 Heart Health Blvd', 'San Francisco', 'CA', '94102', 'tier_1', 4.9, '["English", "Mandarin"]'),
('3456789012', 'Emily', 'Williams', 'Internal Medicine', '555-0103', '300 Wellness Way', 'Oakland', 'CA', '94612', 'tier_2', 4.6, '["English"]'),
('4567890123', 'David', 'Martinez', 'Orthopedic Surgery', '555-0104', '400 Bone & Joint Center', 'San Jose', 'CA', '95112', 'tier_1', 4.7, '["English", "Spanish"]'),
('5678901234', 'Jennifer', 'Lee', 'Dermatology', '555-0105', '500 Skin Care Clinic', 'San Francisco', 'CA', '94102', 'tier_2', 4.5, '["English", "Korean"]'),
('6789012345', 'Robert', 'Brown', 'Psychiatry', '555-0106', '600 Mental Health Center', 'Berkeley', 'CA', '94704', 'tier_1', 4.8, '["English"]'),
('7890123456', 'Lisa', 'Taylor', 'Obstetrics & Gynecology', '555-0107', '700 Women''s Health', 'San Francisco', 'CA', '94102', 'tier_1', 4.9, '["English", "French"]'),
('8901234567', 'James', 'Wilson', 'Gastroenterology', '555-0108', '800 Digestive Care', 'Palo Alto', 'CA', '94301', 'tier_2', 4.4, '["English"]'),
('9012345678', 'Amanda', 'Garcia', 'Pediatrics', '555-0109', '900 Children''s Care', 'San Francisco', 'CA', '94102', 'tier_1', 4.9, '["English", "Spanish"]'),
('0123456789', 'William', 'Anderson', 'Pulmonology', '555-0110', '1000 Lung & Breathing Center', 'Oakland', 'CA', '94612', 'tier_1', 4.6, '["English"]')
ON CONFLICT (npi) DO NOTHING;

-- Success message
SELECT 'Healthcare Payer tables created successfully!' AS result;
