-- EHS Electronic Journal - PostgreSQL Database Schema
-- Laboratory Management System for EHS Labs Environmental Hazards Services
-- Generated: 2025-01-01

-- Enable UUID extension if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- USERS AND DEPARTMENTS
-- =============================================================================

-- User roles enum
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'lab_tech', 'user', 'read_only');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    department VARCHAR(100),
    phone VARCHAR(20),
    extension VARCHAR(10)
);

-- Create indexes for users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    manager_name VARCHAR(255),
    manager_email VARCHAR(255),
    phone VARCHAR(20),
    location VARCHAR(255),
    budget_code VARCHAR(50),
    cost_center VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_departments_name ON departments(name);
CREATE INDEX idx_departments_code ON departments(code);

-- =============================================================================
-- CHEMICAL INVENTORY
-- =============================================================================

-- Chemical inventory main table
CREATE TABLE chemical_inventory_log (
    id SERIAL PRIMARY KEY,
    chemical_name VARCHAR(255) NOT NULL,
    cas_number VARCHAR(50),
    manufacturer VARCHAR(255),
    catalog_number VARCHAR(100),
    lot_number VARCHAR(100),
    container_size VARCHAR(50),
    current_quantity DECIMAL(10,3) NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL,
    storage_location VARCHAR(255),
    storage_temperature VARCHAR(50),
    storage_conditions TEXT,
    hazard_class VARCHAR(100),
    safety_notes TEXT,
    received_date TIMESTAMP WITH TIME ZONE,
    expiration_date TIMESTAMP WITH TIME ZONE,
    opened_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_hazardous BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_chemical_inventory_name ON chemical_inventory_log(chemical_name);
CREATE INDEX idx_chemical_inventory_cas ON chemical_inventory_log(cas_number);
CREATE INDEX idx_chemical_inventory_active ON chemical_inventory_log(is_active);
CREATE INDEX idx_chemical_inventory_hazardous ON chemical_inventory_log(is_hazardous);
CREATE INDEX idx_chemical_inventory_expiration ON chemical_inventory_log(expiration_date);

-- Chemical inventory history
CREATE TABLE chemical_inventory_history (
    id SERIAL PRIMARY KEY,
    chemical_id INTEGER NOT NULL REFERENCES chemical_inventory_log(id),
    action VARCHAR(50) NOT NULL,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    quantity_change DECIMAL(10,3),
    remaining_quantity DECIMAL(10,3),
    notes TEXT,
    reason VARCHAR(255),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_chemical_history_chemical_id ON chemical_inventory_history(chemical_id);
CREATE INDEX idx_chemical_history_action ON chemical_inventory_history(action);
CREATE INDEX idx_chemical_history_date ON chemical_inventory_history(changed_at);

-- =============================================================================
-- REAGENTS TABLES
-- =============================================================================

-- MM Reagents
CREATE TABLE mm_reagents (
    id SERIAL PRIMARY KEY,
    reagent_name VARCHAR(255) NOT NULL,
    batch_number VARCHAR(100) UNIQUE NOT NULL,
    preparation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expiration_date TIMESTAMP WITH TIME ZONE,
    total_volume DECIMAL(10,3) NOT NULL,
    concentration VARCHAR(100),
    preparation_method TEXT,
    chemicals_used TEXT,
    ph_value DECIMAL(4,2),
    conductivity DECIMAL(10,3),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    prepared_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_mm_reagents_name ON mm_reagents(reagent_name);
CREATE INDEX idx_mm_reagents_batch ON mm_reagents(batch_number);
CREATE INDEX idx_mm_reagents_active ON mm_reagents(is_active);

-- MM Reagents History
CREATE TABLE mm_reagents_history (
    id SERIAL PRIMARY KEY,
    reagent_id INTEGER NOT NULL REFERENCES mm_reagents(id),
    action VARCHAR(50) NOT NULL,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    notes TEXT,
    reason VARCHAR(255),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Pb Reagents
CREATE TABLE pb_reagents (
    id SERIAL PRIMARY KEY,
    reagent_name VARCHAR(255) NOT NULL,
    batch_number VARCHAR(100) UNIQUE NOT NULL,
    preparation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expiration_date TIMESTAMP WITH TIME ZONE,
    total_volume DECIMAL(10,3) NOT NULL,
    lead_concentration DECIMAL(10,6),
    preparation_method TEXT,
    source_standard VARCHAR(255),
    verified_concentration DECIMAL(10,6),
    verification_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    prepared_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_pb_reagents_name ON pb_reagents(reagent_name);
CREATE INDEX idx_pb_reagents_batch ON pb_reagents(batch_number);

-- Pb Reagents History
CREATE TABLE pb_reagents_history (
    id SERIAL PRIMARY KEY,
    reagent_id INTEGER NOT NULL REFERENCES pb_reagents(id),
    action VARCHAR(50) NOT NULL,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    notes TEXT,
    reason VARCHAR(255),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- TCLP Reagents
CREATE TABLE tclp_reagents (
    id SERIAL PRIMARY KEY,
    reagent_name VARCHAR(255) NOT NULL,
    batch_number VARCHAR(100) UNIQUE NOT NULL,
    reagent_type VARCHAR(100) NOT NULL,
    preparation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expiration_date TIMESTAMP WITH TIME ZONE,
    total_volume DECIMAL(10,3) NOT NULL,
    ph_target DECIMAL(4,2),
    final_ph DECIMAL(4,2),
    preparation_method TEXT,
    chemicals_used TEXT,
    conductivity DECIMAL(10,3),
    verification_passed BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    prepared_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_tclp_reagents_name ON tclp_reagents(reagent_name);
CREATE INDEX idx_tclp_reagents_batch ON tclp_reagents(batch_number);
CREATE INDEX idx_tclp_reagents_type ON tclp_reagents(reagent_type);

-- TCLP Reagents History
CREATE TABLE tclp_reagents_history (
    id SERIAL PRIMARY KEY,
    reagent_id INTEGER NOT NULL REFERENCES tclp_reagents(id),
    action VARCHAR(50) NOT NULL,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    notes TEXT,
    reason VARCHAR(255),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- STANDARDS TABLES
-- =============================================================================

-- MM Standards
CREATE TABLE mm_standards (
    id SERIAL PRIMARY KEY,
    standard_name VARCHAR(255) NOT NULL,
    batch_number VARCHAR(100) UNIQUE NOT NULL,
    standard_type VARCHAR(100) NOT NULL,
    preparation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expiration_date TIMESTAMP WITH TIME ZONE,
    target_concentration DECIMAL(12,6) NOT NULL,
    actual_concentration DECIMAL(12,6),
    matrix VARCHAR(100),
    source_material VARCHAR(255),
    dilution_factor DECIMAL(10,4),
    total_volume DECIMAL(10,3) NOT NULL,
    elements TEXT,
    verification_method VARCHAR(100),
    certified BOOLEAN DEFAULT FALSE,
    certificate_number VARCHAR(100),
    initial_volume DECIMAL(10,3) NOT NULL,
    current_volume DECIMAL(10,3) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    prepared_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_mm_standards_name ON mm_standards(standard_name);
CREATE INDEX idx_mm_standards_batch ON mm_standards(batch_number);
CREATE INDEX idx_mm_standards_type ON mm_standards(standard_type);

-- MM Standards History
CREATE TABLE mm_standards_history (
    id SERIAL PRIMARY KEY,
    standard_id INTEGER NOT NULL REFERENCES mm_standards(id),
    action VARCHAR(50) NOT NULL,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    analysis_type VARCHAR(100),
    instrument_used VARCHAR(255),
    notes TEXT,
    reason VARCHAR(255),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- FlameAA Standards
CREATE TABLE flameaa_standards (
    id SERIAL PRIMARY KEY,
    standard_name VARCHAR(255) NOT NULL,
    batch_number VARCHAR(100) UNIQUE NOT NULL,
    element VARCHAR(20) NOT NULL,
    preparation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expiration_date TIMESTAMP WITH TIME ZONE,
    target_concentration DECIMAL(10,4) NOT NULL,
    actual_concentration DECIMAL(10,4),
    matrix VARCHAR(100),
    source_standard VARCHAR(255),
    dilution_series TEXT,
    total_volume DECIMAL(10,3) NOT NULL,
    wavelength DECIMAL(6,2),
    slit_width DECIMAL(4,2),
    flame_type VARCHAR(50),
    absorbance_value DECIMAL(8,4),
    linearity_check BOOLEAN DEFAULT FALSE,
    correlation_coefficient DECIMAL(6,4),
    initial_volume DECIMAL(10,3) NOT NULL,
    current_volume DECIMAL(10,3) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    prepared_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_flameaa_standards_name ON flameaa_standards(standard_name);
CREATE INDEX idx_flameaa_standards_batch ON flameaa_standards(batch_number);
CREATE INDEX idx_flameaa_standards_element ON flameaa_standards(element);

-- FlameAA Standards History
CREATE TABLE flameaa_standards_history (
    id SERIAL PRIMARY KEY,
    standard_id INTEGER NOT NULL REFERENCES flameaa_standards(id),
    action VARCHAR(50) NOT NULL,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    analysis_date TIMESTAMP WITH TIME ZONE,
    instrument_used VARCHAR(255),
    method_used VARCHAR(100),
    notes TEXT,
    reason VARCHAR(255),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- EQUIPMENT TABLES
-- =============================================================================

-- Equipment main table
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    equipment_name VARCHAR(255) NOT NULL,
    model_number VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    manufacturer VARCHAR(255),
    equipment_type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    purchase_date TIMESTAMP WITH TIME ZONE,
    warranty_expiration TIMESTAMP WITH TIME ZONE,
    calibration_frequency INTEGER,
    last_calibration TIMESTAMP WITH TIME ZONE,
    next_calibration_due TIMESTAMP WITH TIME ZONE,
    calibration_status VARCHAR(50) DEFAULT 'unknown',
    service_provider VARCHAR(255),
    service_contact VARCHAR(255),
    last_service_date TIMESTAMP WITH TIME ZONE,
    next_service_due TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_in_service BOOLEAN DEFAULT TRUE,
    notes TEXT,
    responsible_user INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_equipment_name ON equipment(equipment_name);
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_serial ON equipment(serial_number);
CREATE INDEX idx_equipment_calibration_due ON equipment(next_calibration_due);

-- Pipette calibration log
CREATE TABLE pipette_log (
    id SERIAL PRIMARY KEY,
    pipette_id VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(255),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    volume_range_min DECIMAL(8,3),
    volume_range_max DECIMAL(8,3),
    pipette_type VARCHAR(50) NOT NULL,
    channels INTEGER DEFAULT 1,
    calibration_date TIMESTAMP WITH TIME ZONE NOT NULL,
    calibration_volume DECIMAL(8,3) NOT NULL,
    target_volume DECIMAL(8,3) NOT NULL,
    measured_volumes TEXT,
    mean_volume DECIMAL(8,3),
    accuracy_percent DECIMAL(6,3),
    precision_cv DECIMAL(6,3),
    accuracy_limit DECIMAL(6,3) DEFAULT 2.0,
    precision_limit DECIMAL(6,3) DEFAULT 1.0,
    calibration_passed BOOLEAN DEFAULT FALSE,
    service_required BOOLEAN DEFAULT FALSE,
    service_notes TEXT,
    next_calibration_due TIMESTAMP WITH TIME ZONE,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    barometric_pressure DECIMAL(7,2),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    calibrated_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_pipette_log_pipette_id ON pipette_log(pipette_id);
CREATE INDEX idx_pipette_log_calibration_date ON pipette_log(calibration_date);

-- Water conductivity tests
CREATE TABLE water_conductivity_tests (
    id SERIAL PRIMARY KEY,
    test_date TIMESTAMP WITH TIME ZONE NOT NULL,
    test_time VARCHAR(20) NOT NULL,
    sample_id VARCHAR(100),
    water_source VARCHAR(255) NOT NULL,
    source_location VARCHAR(255),
    water_temperature DECIMAL(5,2),
    ambient_temperature DECIMAL(5,2),
    conductivity_reading DECIMAL(8,3) NOT NULL,
    conductivity_units VARCHAR(20) DEFAULT 'µS/cm',
    meter_model VARCHAR(255),
    meter_serial VARCHAR(100),
    probe_id VARCHAR(100),
    last_calibration_date TIMESTAMP WITH TIME ZONE,
    specification_limit DECIMAL(8,3),
    meets_specification BOOLEAN DEFAULT TRUE,
    reading_1 DECIMAL(8,3),
    reading_2 DECIMAL(8,3),
    reading_3 DECIMAL(8,3),
    average_reading DECIMAL(8,3),
    standard_deviation DECIMAL(8,4),
    action_required BOOLEAN DEFAULT FALSE,
    action_taken TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    observations TEXT,
    tested_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_water_conductivity_test_date ON water_conductivity_tests(test_date);
CREATE INDEX idx_water_conductivity_source ON water_conductivity_tests(water_source);

-- =============================================================================
-- MAINTENANCE TABLES
-- =============================================================================

-- Maintenance type and status enums
CREATE TYPE maintenance_type AS ENUM ('daily', 'weekly', 'monthly', 'quarterly', 'annual', 'preventive', 'corrective', 'emergency');
CREATE TYPE maintenance_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled', 'overdue');

-- ICP-OES Maintenance Log
CREATE TABLE icp_oes_maintenance_log (
    id SERIAL PRIMARY KEY,
    maintenance_date TIMESTAMP WITH TIME ZONE NOT NULL,
    maintenance_type maintenance_type NOT NULL,
    maintenance_status maintenance_status DEFAULT 'completed',
    instrument_id VARCHAR(100) NOT NULL,
    instrument_model VARCHAR(255),
    serial_number VARCHAR(100),
    maintenance_category VARCHAR(100) NOT NULL,
    work_performed TEXT NOT NULL,
    
    -- Torch maintenance
    torch_condition VARCHAR(100),
    torch_hours DECIMAL(8,2),
    torch_replaced BOOLEAN DEFAULT FALSE,
    new_torch_serial VARCHAR(100),
    
    -- Pump maintenance
    pump_tubing_replaced BOOLEAN DEFAULT FALSE,
    pump_flow_rate DECIMAL(6,3),
    pump_pressure DECIMAL(6,2),
    
    -- Optics maintenance
    optics_cleaned BOOLEAN DEFAULT FALSE,
    purge_gas_flow DECIMAL(6,2),
    optical_chamber_condition VARCHAR(100),
    
    -- Nebulizer maintenance
    nebulizer_cleaned BOOLEAN DEFAULT FALSE,
    nebulizer_type VARCHAR(100),
    uptake_rate DECIMAL(6,3),
    
    -- Argon gas system
    argon_pressure DECIMAL(6,2),
    argon_flow_plasma DECIMAL(6,2),
    argon_flow_auxiliary DECIMAL(6,2),
    argon_flow_nebulizer DECIMAL(6,3),
    
    -- Performance checks
    wavelength_calibration BOOLEAN DEFAULT FALSE,
    intensity_check BOOLEAN DEFAULT FALSE,
    background_check BOOLEAN DEFAULT FALSE,
    stability_check BOOLEAN DEFAULT FALSE,
    
    -- Performance results
    detection_limits_acceptable BOOLEAN DEFAULT TRUE,
    precision_acceptable BOOLEAN DEFAULT TRUE,
    accuracy_acceptable BOOLEAN DEFAULT TRUE,
    
    -- Parts and costs
    parts_replaced TEXT,
    consumables_used TEXT,
    cost_estimate DECIMAL(10,2),
    
    -- Issues and follow-up
    issues_found TEXT,
    resolutions TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    next_maintenance_due TIMESTAMP WITH TIME ZONE,
    
    -- Duration
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_hours DECIMAL(5,2),
    
    -- Documentation
    procedure_followed VARCHAR(255),
    photos_taken BOOLEAN DEFAULT FALSE,
    documentation_path VARCHAR(500),
    
    -- Status
    instrument_operational BOOLEAN DEFAULT TRUE,
    notes TEXT,
    
    -- Tracking
    performed_by INTEGER NOT NULL REFERENCES users(id),
    supervisor_approval INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_icp_oes_maintenance_date ON icp_oes_maintenance_log(maintenance_date);
CREATE INDEX idx_icp_oes_maintenance_type ON icp_oes_maintenance_log(maintenance_type);
CREATE INDEX idx_icp_oes_maintenance_instrument ON icp_oes_maintenance_log(instrument_id);

-- ICP-OES Maintenance History
CREATE TABLE icp_oes_maintenance_history (
    id SERIAL PRIMARY KEY,
    maintenance_log_id INTEGER NOT NULL REFERENCES icp_oes_maintenance_log(id),
    action VARCHAR(50) NOT NULL,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    notes TEXT,
    reason VARCHAR(255),
    changed_by INTEGER NOT NULL REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language plpgsql;

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chemical_inventory_updated_at BEFORE UPDATE ON chemical_inventory_log FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mm_reagents_updated_at BEFORE UPDATE ON mm_reagents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pb_reagents_updated_at BEFORE UPDATE ON pb_reagents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tclp_reagents_updated_at BEFORE UPDATE ON tclp_reagents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mm_standards_updated_at BEFORE UPDATE ON mm_standards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_flameaa_standards_updated_at BEFORE UPDATE ON flameaa_standards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_equipment_updated_at BEFORE UPDATE ON equipment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_icp_oes_maintenance_updated_at BEFORE UPDATE ON icp_oes_maintenance_log FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- SAMPLE DATA (OPTIONAL)
-- =============================================================================

-- Insert default admin user (password: admin123!)
-- Note: This is for development only - change in production
INSERT INTO users (username, email, full_name, hashed_password, role, is_active, is_verified)
VALUES ('admin', 'admin@ehslabs.com', 'System Administrator', 
        '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- admin123!
        'admin', TRUE, TRUE);

-- Insert sample departments
INSERT INTO departments (name, code, description, manager_name, manager_email, location)
VALUES 
    ('Environmental Chemistry', 'ENVCH', 'Environmental analysis and chemistry laboratory', 'Dr. Jane Smith', 'j.smith@ehslabs.com', 'Building A, Floor 2'),
    ('Quality Control', 'QC', 'Quality control and assurance department', 'Mark Johnson', 'm.johnson@ehslabs.com', 'Building A, Floor 1'),
    ('Research & Development', 'RD', 'Research and development laboratory', 'Dr. Sarah Williams', 's.williams@ehslabs.com', 'Building B, Floor 3');

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON DATABASE ehs_electronic_journal IS 'EHS Electronic Journal - Laboratory Management System Database';
COMMENT ON TABLE users IS 'User accounts and authentication information';
COMMENT ON TABLE chemical_inventory_log IS 'Main chemical inventory tracking with current quantities';
COMMENT ON TABLE chemical_inventory_history IS 'Historical changes to chemical inventory';
COMMENT ON TABLE mm_reagents IS 'MM (Metals) reagents preparation and tracking';
COMMENT ON TABLE pb_reagents IS 'Lead reagents preparation and tracking';
COMMENT ON TABLE tclp_reagents IS 'TCLP extraction fluid reagents';
COMMENT ON TABLE mm_standards IS 'Metals standards for calibration and QC';
COMMENT ON TABLE flameaa_standards IS 'Flame AA standards for atomic absorption';
COMMENT ON TABLE equipment IS 'Laboratory equipment inventory and calibration tracking';
COMMENT ON TABLE pipette_log IS 'Pipette calibration and maintenance records';
COMMENT ON TABLE water_conductivity_tests IS 'Water quality conductivity test results';
COMMENT ON TABLE icp_oes_maintenance_log IS 'ICP-OES instrument maintenance records';