-- EHS Electronic Journal - SQL Server Database Schema
-- Laboratory Management System for EHS Labs Environmental Hazards Services
-- Migrated from PostgreSQL version

-- =============================================================================
-- USERS AND DEPARTMENTS
-- =============================================================================

-- Users table
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    full_name NVARCHAR(255) NOT NULL,
    hashed_password NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'manager', 'lab_tech', 'user', 'read_only')),
    is_active BIT DEFAULT 1,
    is_verified BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    last_login DATETIME2,
    department NVARCHAR(100),
    phone NVARCHAR(20),
    extension NVARCHAR(10)
);

-- Create indexes for users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Departments table
CREATE TABLE departments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) UNIQUE NOT NULL,
    code NVARCHAR(20) UNIQUE NOT NULL,
    description NTEXT,
    manager_name NVARCHAR(255),
    manager_email NVARCHAR(255),
    phone NVARCHAR(20),
    location NVARCHAR(255),
    budget_code NVARCHAR(50),
    cost_center NVARCHAR(50),
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL
);

CREATE INDEX idx_departments_name ON departments(name);
CREATE INDEX idx_departments_code ON departments(code);

-- =============================================================================
-- CHEMICAL INVENTORY
-- =============================================================================

-- Chemical inventory main table
CREATE TABLE chemical_inventory_log (
    id INT IDENTITY(1,1) PRIMARY KEY,
    chemical_name NVARCHAR(255) NOT NULL,
    cas_number NVARCHAR(50),
    manufacturer NVARCHAR(255),
    catalog_number NVARCHAR(100),
    lot_number NVARCHAR(100),
    container_size NVARCHAR(50),
    current_quantity DECIMAL(10,3) NOT NULL DEFAULT 0,
    unit NVARCHAR(20) NOT NULL,
    storage_location NVARCHAR(255),
    storage_temperature NVARCHAR(50),
    storage_conditions NTEXT,
    hazard_class NVARCHAR(100),
    safety_notes NTEXT,
    received_date DATETIME2,
    expiration_date DATETIME2,
    opened_date DATETIME2,
    is_active BIT DEFAULT 1,
    is_hazardous BIT DEFAULT 0,
    created_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE INDEX idx_chemical_inventory_name ON chemical_inventory_log(chemical_name);
CREATE INDEX idx_chemical_inventory_cas ON chemical_inventory_log(cas_number);
CREATE INDEX idx_chemical_inventory_active ON chemical_inventory_log(is_active);
CREATE INDEX idx_chemical_inventory_hazardous ON chemical_inventory_log(is_hazardous);
CREATE INDEX idx_chemical_inventory_expiration ON chemical_inventory_log(expiration_date);

-- Chemical inventory history
CREATE TABLE chemical_inventory_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    chemical_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    field_changed NVARCHAR(100),
    old_value NTEXT,
    new_value NTEXT,
    quantity_change DECIMAL(10,3),
    remaining_quantity DECIMAL(10,3),
    notes NTEXT,
    reason NVARCHAR(255),
    changed_by INT NOT NULL,
    changed_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (chemical_id) REFERENCES chemical_inventory_log(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

CREATE INDEX idx_chemical_history_chemical_id ON chemical_inventory_history(chemical_id);
CREATE INDEX idx_chemical_history_action ON chemical_inventory_history(action);
CREATE INDEX idx_chemical_history_date ON chemical_inventory_history(changed_at);

-- =============================================================================
-- REAGENTS TABLES
-- =============================================================================

-- MM Reagents
CREATE TABLE mm_reagents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reagent_name NVARCHAR(255) NOT NULL,
    batch_number NVARCHAR(100) UNIQUE NOT NULL,
    preparation_date DATETIME2 NOT NULL,
    expiration_date DATETIME2,
    total_volume DECIMAL(10,3) NOT NULL,
    concentration NVARCHAR(100),
    preparation_method NTEXT,
    chemicals_used NTEXT,
    ph_value DECIMAL(4,2),
    conductivity DECIMAL(10,3),
    is_active BIT DEFAULT 1,
    notes NTEXT,
    prepared_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (prepared_by) REFERENCES users(id)
);

CREATE INDEX idx_mm_reagents_name ON mm_reagents(reagent_name);
CREATE INDEX idx_mm_reagents_batch ON mm_reagents(batch_number);
CREATE INDEX idx_mm_reagents_active ON mm_reagents(is_active);

-- MM Reagents History
CREATE TABLE mm_reagents_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reagent_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    field_changed NVARCHAR(100),
    old_value NTEXT,
    new_value NTEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    notes NTEXT,
    reason NVARCHAR(255),
    changed_by INT NOT NULL,
    changed_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (reagent_id) REFERENCES mm_reagents(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- Pb Reagents
CREATE TABLE pb_reagents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reagent_name NVARCHAR(255) NOT NULL,
    batch_number NVARCHAR(100) UNIQUE NOT NULL,
    preparation_date DATETIME2 NOT NULL,
    expiration_date DATETIME2,
    total_volume DECIMAL(10,3) NOT NULL,
    lead_concentration DECIMAL(10,6),
    preparation_method NTEXT,
    source_standard NVARCHAR(255),
    verified_concentration DECIMAL(10,6),
    verification_date DATETIME2,
    is_active BIT DEFAULT 1,
    notes NTEXT,
    prepared_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (prepared_by) REFERENCES users(id)
);

CREATE INDEX idx_pb_reagents_name ON pb_reagents(reagent_name);
CREATE INDEX idx_pb_reagents_batch ON pb_reagents(batch_number);

-- Pb Reagents History
CREATE TABLE pb_reagents_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reagent_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    field_changed NVARCHAR(100),
    old_value NTEXT,
    new_value NTEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    notes NTEXT,
    reason NVARCHAR(255),
    changed_by INT NOT NULL,
    changed_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (reagent_id) REFERENCES pb_reagents(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- TCLP Reagents
CREATE TABLE tclp_reagents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reagent_name NVARCHAR(255) NOT NULL,
    batch_number NVARCHAR(100) UNIQUE NOT NULL,
    reagent_type NVARCHAR(100) NOT NULL,
    preparation_date DATETIME2 NOT NULL,
    expiration_date DATETIME2,
    total_volume DECIMAL(10,3) NOT NULL,
    ph_target DECIMAL(4,2),
    final_ph DECIMAL(4,2),
    preparation_method NTEXT,
    chemicals_used NTEXT,
    conductivity DECIMAL(10,3),
    verification_passed BIT DEFAULT 0,
    is_active BIT DEFAULT 1,
    notes NTEXT,
    prepared_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (prepared_by) REFERENCES users(id)
);

CREATE INDEX idx_tclp_reagents_name ON tclp_reagents(reagent_name);
CREATE INDEX idx_tclp_reagents_batch ON tclp_reagents(batch_number);
CREATE INDEX idx_tclp_reagents_type ON tclp_reagents(reagent_type);

-- TCLP Reagents History
CREATE TABLE tclp_reagents_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reagent_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    field_changed NVARCHAR(100),
    old_value NTEXT,
    new_value NTEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    notes NTEXT,
    reason NVARCHAR(255),
    changed_by INT NOT NULL,
    changed_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (reagent_id) REFERENCES tclp_reagents(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- =============================================================================
-- STANDARDS TABLES
-- =============================================================================

-- MM Standards
CREATE TABLE mm_standards (
    id INT IDENTITY(1,1) PRIMARY KEY,
    standard_name NVARCHAR(255) NOT NULL,
    batch_number NVARCHAR(100) UNIQUE NOT NULL,
    standard_type NVARCHAR(100) NOT NULL,
    preparation_date DATETIME2 NOT NULL,
    expiration_date DATETIME2,
    target_concentration DECIMAL(12,6) NOT NULL,
    actual_concentration DECIMAL(12,6),
    matrix NVARCHAR(100),
    source_material NVARCHAR(255),
    dilution_factor DECIMAL(10,4),
    total_volume DECIMAL(10,3) NOT NULL,
    elements NTEXT,
    verification_method NVARCHAR(100),
    certified BIT DEFAULT 0,
    certificate_number NVARCHAR(100),
    initial_volume DECIMAL(10,3) NOT NULL,
    current_volume DECIMAL(10,3) NOT NULL,
    is_active BIT DEFAULT 1,
    notes NTEXT,
    prepared_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (prepared_by) REFERENCES users(id)
);

CREATE INDEX idx_mm_standards_name ON mm_standards(standard_name);
CREATE INDEX idx_mm_standards_batch ON mm_standards(batch_number);
CREATE INDEX idx_mm_standards_type ON mm_standards(standard_type);

-- MM Standards History
CREATE TABLE mm_standards_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    standard_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    field_changed NVARCHAR(100),
    old_value NTEXT,
    new_value NTEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    analysis_type NVARCHAR(100),
    instrument_used NVARCHAR(255),
    notes NTEXT,
    reason NVARCHAR(255),
    changed_by INT NOT NULL,
    changed_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (standard_id) REFERENCES mm_standards(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- FlameAA Standards
CREATE TABLE flameaa_standards (
    id INT IDENTITY(1,1) PRIMARY KEY,
    standard_name NVARCHAR(255) NOT NULL,
    batch_number NVARCHAR(100) UNIQUE NOT NULL,
    element NVARCHAR(20) NOT NULL,
    preparation_date DATETIME2 NOT NULL,
    expiration_date DATETIME2,
    target_concentration DECIMAL(10,4) NOT NULL,
    actual_concentration DECIMAL(10,4),
    matrix NVARCHAR(100),
    source_standard NVARCHAR(255),
    dilution_series NTEXT,
    total_volume DECIMAL(10,3) NOT NULL,
    wavelength DECIMAL(6,2),
    slit_width DECIMAL(4,2),
    flame_type NVARCHAR(50),
    absorbance_value DECIMAL(8,4),
    linearity_check BIT DEFAULT 0,
    correlation_coefficient DECIMAL(6,4),
    initial_volume DECIMAL(10,3) NOT NULL,
    current_volume DECIMAL(10,3) NOT NULL,
    is_active BIT DEFAULT 1,
    notes NTEXT,
    prepared_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (prepared_by) REFERENCES users(id)
);

CREATE INDEX idx_flameaa_standards_name ON flameaa_standards(standard_name);
CREATE INDEX idx_flameaa_standards_batch ON flameaa_standards(batch_number);
CREATE INDEX idx_flameaa_standards_element ON flameaa_standards(element);

-- FlameAA Standards History
CREATE TABLE flameaa_standards_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    standard_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    field_changed NVARCHAR(100),
    old_value NTEXT,
    new_value NTEXT,
    volume_used DECIMAL(10,3),
    remaining_volume DECIMAL(10,3),
    analysis_date DATETIME2,
    instrument_used NVARCHAR(255),
    method_used NVARCHAR(100),
    notes NTEXT,
    reason NVARCHAR(255),
    changed_by INT NOT NULL,
    changed_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (standard_id) REFERENCES flameaa_standards(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- =============================================================================
-- EQUIPMENT TABLES
-- =============================================================================

-- Equipment main table
CREATE TABLE equipment (
    id INT IDENTITY(1,1) PRIMARY KEY,
    equipment_name NVARCHAR(255) NOT NULL,
    model_number NVARCHAR(100),
    serial_number NVARCHAR(100) UNIQUE,
    manufacturer NVARCHAR(255),
    equipment_type NVARCHAR(100) NOT NULL,
    location NVARCHAR(255),
    purchase_date DATETIME2,
    warranty_expiration DATETIME2,
    calibration_frequency INT,
    last_calibration DATETIME2,
    next_calibration_due DATETIME2,
    calibration_status NVARCHAR(50) DEFAULT 'unknown',
    service_provider NVARCHAR(255),
    service_contact NVARCHAR(255),
    last_service_date DATETIME2,
    next_service_due DATETIME2,
    is_active BIT DEFAULT 1,
    is_in_service BIT DEFAULT 1,
    notes NTEXT,
    responsible_user INT,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (responsible_user) REFERENCES users(id)
);

CREATE INDEX idx_equipment_name ON equipment(equipment_name);
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_serial ON equipment(serial_number);
CREATE INDEX idx_equipment_calibration_due ON equipment(next_calibration_due);

-- Pipette calibration log
CREATE TABLE pipette_log (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pipette_id NVARCHAR(100) NOT NULL,
    manufacturer NVARCHAR(255),
    model NVARCHAR(100),
    serial_number NVARCHAR(100),
    volume_range_min DECIMAL(8,3),
    volume_range_max DECIMAL(8,3),
    pipette_type NVARCHAR(50) NOT NULL,
    channels INT DEFAULT 1,
    calibration_date DATETIME2 NOT NULL,
    calibration_volume DECIMAL(8,3) NOT NULL,
    target_volume DECIMAL(8,3) NOT NULL,
    measured_volumes NTEXT,
    mean_volume DECIMAL(8,3),
    accuracy_percent DECIMAL(6,3),
    precision_cv DECIMAL(6,3),
    accuracy_limit DECIMAL(6,3) DEFAULT 2.0,
    precision_limit DECIMAL(6,3) DEFAULT 1.0,
    calibration_passed BIT DEFAULT 0,
    service_required BIT DEFAULT 0,
    service_notes NTEXT,
    next_calibration_due DATETIME2,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    barometric_pressure DECIMAL(7,2),
    is_active BIT DEFAULT 1,
    notes NTEXT,
    calibrated_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (calibrated_by) REFERENCES users(id)
);

CREATE INDEX idx_pipette_log_pipette_id ON pipette_log(pipette_id);
CREATE INDEX idx_pipette_log_calibration_date ON pipette_log(calibration_date);

-- Water conductivity tests
CREATE TABLE water_conductivity_tests (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_date DATETIME2 NOT NULL,
    test_time NVARCHAR(20) NOT NULL,
    sample_id NVARCHAR(100),
    water_source NVARCHAR(255) NOT NULL,
    source_location NVARCHAR(255),
    water_temperature DECIMAL(5,2),
    ambient_temperature DECIMAL(5,2),
    conductivity_reading DECIMAL(8,3) NOT NULL,
    conductivity_units NVARCHAR(20) DEFAULT 'µS/cm',
    meter_model NVARCHAR(255),
    meter_serial NVARCHAR(100),
    probe_id NVARCHAR(100),
    last_calibration_date DATETIME2,
    specification_limit DECIMAL(8,3),
    meets_specification BIT DEFAULT 1,
    reading_1 DECIMAL(8,3),
    reading_2 DECIMAL(8,3),
    reading_3 DECIMAL(8,3),
    average_reading DECIMAL(8,3),
    standard_deviation DECIMAL(8,4),
    action_required BIT DEFAULT 0,
    action_taken NTEXT,
    follow_up_required BIT DEFAULT 0,
    follow_up_date DATETIME2,
    notes NTEXT,
    observations NTEXT,
    tested_by INT NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (tested_by) REFERENCES users(id)
);

CREATE INDEX idx_water_conductivity_test_date ON water_conductivity_tests(test_date);
CREATE INDEX idx_water_conductivity_source ON water_conductivity_tests(water_source);

-- =============================================================================
-- MAINTENANCE TABLES
-- =============================================================================

-- ICP-OES Maintenance Log
CREATE TABLE icp_oes_maintenance_log (
    id INT IDENTITY(1,1) PRIMARY KEY,
    maintenance_date DATETIME2 NOT NULL,
    maintenance_type NVARCHAR(20) NOT NULL CHECK (maintenance_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'annual', 'preventive', 'corrective', 'emergency')),
    maintenance_status NVARCHAR(20) DEFAULT 'completed' CHECK (maintenance_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'overdue')),
    instrument_id NVARCHAR(100) NOT NULL,
    instrument_model NVARCHAR(255),
    serial_number NVARCHAR(100),
    maintenance_category NVARCHAR(100) NOT NULL,
    work_performed NTEXT NOT NULL,
    
    -- Torch maintenance
    torch_condition NVARCHAR(100),
    torch_hours DECIMAL(8,2),
    torch_replaced BIT DEFAULT 0,
    new_torch_serial NVARCHAR(100),
    
    -- Pump maintenance
    pump_tubing_replaced BIT DEFAULT 0,
    pump_flow_rate DECIMAL(6,3),
    pump_pressure DECIMAL(6,2),
    
    -- Optics maintenance
    optics_cleaned BIT DEFAULT 0,
    purge_gas_flow DECIMAL(6,2),
    optical_chamber_condition NVARCHAR(100),
    
    -- Nebulizer maintenance
    nebulizer_cleaned BIT DEFAULT 0,
    nebulizer_type NVARCHAR(100),
    uptake_rate DECIMAL(6,3),
    
    -- Argon gas system
    argon_pressure DECIMAL(6,2),
    argon_flow_plasma DECIMAL(6,2),
    argon_flow_auxiliary DECIMAL(6,2),
    argon_flow_nebulizer DECIMAL(6,3),
    
    -- Performance checks
    wavelength_calibration BIT DEFAULT 0,
    intensity_check BIT DEFAULT 0,
    background_check BIT DEFAULT 0,
    stability_check BIT DEFAULT 0,
    
    -- Performance results
    detection_limits_acceptable BIT DEFAULT 1,
    precision_acceptable BIT DEFAULT 1,
    accuracy_acceptable BIT DEFAULT 1,
    
    -- Parts and costs
    parts_replaced NTEXT,
    consumables_used NTEXT,
    cost_estimate DECIMAL(10,2),
    
    -- Issues and follow-up
    issues_found NTEXT,
    resolutions NTEXT,
    follow_up_required BIT DEFAULT 0,
    next_maintenance_due DATETIME2,
    
    -- Duration
    start_time DATETIME2,
    end_time DATETIME2,
    duration_hours DECIMAL(5,2),
    
    -- Documentation
    procedure_followed NVARCHAR(255),
    photos_taken BIT DEFAULT 0,
    documentation_path NVARCHAR(500),
    
    -- Status
    instrument_operational BIT DEFAULT 1,
    notes NTEXT,
    
    -- Tracking
    performed_by INT NOT NULL,
    supervisor_approval INT,
    created_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    updated_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (performed_by) REFERENCES users(id),
    FOREIGN KEY (supervisor_approval) REFERENCES users(id)
);

CREATE INDEX idx_icp_oes_maintenance_date ON icp_oes_maintenance_log(maintenance_date);
CREATE INDEX idx_icp_oes_maintenance_type ON icp_oes_maintenance_log(maintenance_type);
CREATE INDEX idx_icp_oes_maintenance_instrument ON icp_oes_maintenance_log(instrument_id);

-- ICP-OES Maintenance History
CREATE TABLE icp_oes_maintenance_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    maintenance_log_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    field_changed NVARCHAR(100),
    old_value NTEXT,
    new_value NTEXT,
    old_status NVARCHAR(50),
    new_status NVARCHAR(50),
    notes NTEXT,
    reason NVARCHAR(255),
    changed_by INT NOT NULL,
    changed_at DATETIME2 DEFAULT GETUTCDATE() NOT NULL,
    FOREIGN KEY (maintenance_log_id) REFERENCES icp_oes_maintenance_log(id),
    FOREIGN KEY (changed_by) REFERENCES users(id)
);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT COLUMNS
-- =============================================================================

-- Create trigger function equivalent for SQL Server
CREATE TRIGGER trg_users_updated_at
ON users
AFTER UPDATE
AS
BEGIN
    UPDATE users 
    SET updated_at = GETUTCDATE()
    FROM users u
    INNER JOIN inserted i ON u.id = i.id
END;

CREATE TRIGGER trg_departments_updated_at
ON departments
AFTER UPDATE
AS
BEGIN
    UPDATE departments 
    SET updated_at = GETUTCDATE()
    FROM departments d
    INNER JOIN inserted i ON d.id = i.id
END;

CREATE TRIGGER trg_chemical_inventory_updated_at
ON chemical_inventory_log
AFTER UPDATE
AS
BEGIN
    UPDATE chemical_inventory_log 
    SET updated_at = GETUTCDATE()
    FROM chemical_inventory_log c
    INNER JOIN inserted i ON c.id = i.id
END;

CREATE TRIGGER trg_mm_reagents_updated_at
ON mm_reagents
AFTER UPDATE
AS
BEGIN
    UPDATE mm_reagents 
    SET updated_at = GETUTCDATE()
    FROM mm_reagents m
    INNER JOIN inserted i ON m.id = i.id
END;

CREATE TRIGGER trg_pb_reagents_updated_at
ON pb_reagents
AFTER UPDATE
AS
BEGIN
    UPDATE pb_reagents 
    SET updated_at = GETUTCDATE()
    FROM pb_reagents p
    INNER JOIN inserted i ON p.id = i.id
END;

CREATE TRIGGER trg_tclp_reagents_updated_at
ON tclp_reagents
AFTER UPDATE
AS
BEGIN
    UPDATE tclp_reagents 
    SET updated_at = GETUTCDATE()
    FROM tclp_reagents t
    INNER JOIN inserted i ON t.id = i.id
END;

CREATE TRIGGER trg_mm_standards_updated_at
ON mm_standards
AFTER UPDATE
AS
BEGIN
    UPDATE mm_standards 
    SET updated_at = GETUTCDATE()
    FROM mm_standards m
    INNER JOIN inserted i ON m.id = i.id
END;

CREATE TRIGGER trg_flameaa_standards_updated_at
ON flameaa_standards
AFTER UPDATE
AS
BEGIN
    UPDATE flameaa_standards 
    SET updated_at = GETUTCDATE()
    FROM flameaa_standards f
    INNER JOIN inserted i ON f.id = i.id
END;

CREATE TRIGGER trg_equipment_updated_at
ON equipment
AFTER UPDATE
AS
BEGIN
    UPDATE equipment 
    SET updated_at = GETUTCDATE()
    FROM equipment e
    INNER JOIN inserted i ON e.id = i.id
END;

CREATE TRIGGER trg_icp_oes_maintenance_updated_at
ON icp_oes_maintenance_log
AFTER UPDATE
AS
BEGIN
    UPDATE icp_oes_maintenance_log 
    SET updated_at = GETUTCDATE()
    FROM icp_oes_maintenance_log m
    INNER JOIN inserted i ON m.id = i.id
END;

-- =============================================================================
-- SAMPLE DATA (OPTIONAL)
-- =============================================================================

-- Insert default admin user (password: admin123!)
-- Note: This is for development only - change in production
INSERT INTO users (username, email, full_name, hashed_password, role, is_active, is_verified)
VALUES ('admin', 'admin@ehslabs.com', 'System Administrator', 
        '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', -- admin123!
        'admin', 1, 1);

-- Insert sample departments
INSERT INTO departments (name, code, description, manager_name, manager_email, location)
VALUES 
    ('Environmental Chemistry', 'ENVCH', 'Environmental analysis and chemistry laboratory', 'Dr. Jane Smith', 'j.smith@ehslabs.com', 'Building A, Floor 2'),
    ('Quality Control', 'QC', 'Quality control and assurance department', 'Mark Johnson', 'm.johnson@ehslabs.com', 'Building A, Floor 1'),
    ('Research & Development', 'RD', 'Research and development laboratory', 'Dr. Sarah Williams', 's.williams@ehslabs.com', 'Building B, Floor 3');