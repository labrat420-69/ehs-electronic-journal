"""
Equipment models for tracking laboratory equipment, pipettes, and water conductivity tests
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Equipment(Base):
    """General equipment tracking and calibration"""
    __tablename__ = "equipment"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Equipment identification
    equipment_name = Column(String(255), nullable=False, index=True)
    model_number = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True, unique=True)
    manufacturer = Column(String(255), nullable=True)
    
    # Equipment details
    equipment_type = Column(String(100), nullable=False)  # Balance, pH meter, Conductivity meter, etc.
    location = Column(String(255), nullable=True)
    purchase_date = Column(DateTime, nullable=True)
    warranty_expiration = Column(DateTime, nullable=True)
    
    # Calibration tracking
    calibration_frequency = Column(Integer, nullable=True)  # days between calibrations
    last_calibration = Column(DateTime, nullable=True)
    next_calibration_due = Column(DateTime, nullable=True)
    calibration_status = Column(String(50), default="unknown")  # current, overdue, due_soon
    
    # Service information
    service_provider = Column(String(255), nullable=True)
    service_contact = Column(String(255), nullable=True)
    last_service_date = Column(DateTime, nullable=True)
    next_service_due = Column(DateTime, nullable=True)
    
    # Status and notes
    is_active = Column(Boolean, default=True)
    is_in_service = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Tracking
    # SQL Server Migration Marker: Add foreign key constraint syntax
    responsible_user = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    responsible = relationship("User", foreign_keys=[responsible_user])
    
    def __repr__(self):
        return f"<Equipment(id={self.id}, name='{self.equipment_name}', type='{self.equipment_type}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "equipment_name": self.equipment_name,
            "model_number": self.model_number,
            "serial_number": self.serial_number,
            "manufacturer": self.manufacturer,
            "equipment_type": self.equipment_type,
            "location": self.location,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "warranty_expiration": self.warranty_expiration.isoformat() if self.warranty_expiration else None,
            "calibration_frequency": self.calibration_frequency,
            "last_calibration": self.last_calibration.isoformat() if self.last_calibration else None,
            "next_calibration_due": self.next_calibration_due.isoformat() if self.next_calibration_due else None,
            "calibration_status": self.calibration_status,
            "service_provider": self.service_provider,
            "service_contact": self.service_contact,
            "last_service_date": self.last_service_date.isoformat() if self.last_service_date else None,
            "next_service_due": self.next_service_due.isoformat() if self.next_service_due else None,
            "is_active": self.is_active,
            "is_in_service": self.is_in_service,
            "notes": self.notes,
            "responsible_user": self.responsible_user,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class PipetteLog(Base):
    """Pipette calibration and maintenance tracking"""
    __tablename__ = "pipette_log"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Pipette identification
    pipette_id = Column(String(100), nullable=False, index=True)  # Lab-assigned ID
    manufacturer = Column(String(255), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    
    # Pipette specifications
    volume_range_min = Column(Numeric(8, 3), nullable=True)  # µL
    volume_range_max = Column(Numeric(8, 3), nullable=True)  # µL
    pipette_type = Column(String(50), nullable=False)  # Fixed, Variable, Multi-channel
    channels = Column(Integer, default=1)  # Number of channels
    
    # Calibration details
    calibration_date = Column(DateTime, nullable=False)
    calibration_volume = Column(Numeric(8, 3), nullable=False)  # µL tested
    target_volume = Column(Numeric(8, 3), nullable=False)  # µL expected
    measured_volumes = Column(Text, nullable=True)  # JSON array of measurements
    
    # Calibration results
    mean_volume = Column(Numeric(8, 3), nullable=True)  # µL
    accuracy_percent = Column(Numeric(6, 3), nullable=True)  # %
    precision_cv = Column(Numeric(6, 3), nullable=True)  # Coefficient of variation %
    
    # Pass/fail criteria
    accuracy_limit = Column(Numeric(6, 3), default=2.0)  # % tolerance
    precision_limit = Column(Numeric(6, 3), default=1.0)  # % CV limit
    calibration_passed = Column(Boolean, default=False)
    
    # Service information
    service_required = Column(Boolean, default=False)
    service_notes = Column(Text, nullable=True)
    next_calibration_due = Column(DateTime, nullable=True)
    
    # Environmental conditions
    temperature = Column(Numeric(5, 2), nullable=True)  # °C
    humidity = Column(Numeric(5, 2), nullable=True)  # %
    barometric_pressure = Column(Numeric(7, 2), nullable=True)  # mmHg
    
    # Status and notes
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Tracking
    # SQL Server Migration Marker: Add foreign key constraint syntax
    calibrated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    calibrator = relationship("User", foreign_keys=[calibrated_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "pipette_id": self.pipette_id,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serial_number": self.serial_number,
            "volume_range_min": float(self.volume_range_min) if self.volume_range_min else None,
            "volume_range_max": float(self.volume_range_max) if self.volume_range_max else None,
            "pipette_type": self.pipette_type,
            "channels": self.channels,
            "calibration_date": self.calibration_date.isoformat() if self.calibration_date else None,
            "calibration_volume": float(self.calibration_volume) if self.calibration_volume else None,
            "target_volume": float(self.target_volume) if self.target_volume else None,
            "measured_volumes": self.measured_volumes,
            "mean_volume": float(self.mean_volume) if self.mean_volume else None,
            "accuracy_percent": float(self.accuracy_percent) if self.accuracy_percent else None,
            "precision_cv": float(self.precision_cv) if self.precision_cv else None,
            "accuracy_limit": float(self.accuracy_limit) if self.accuracy_limit else None,
            "precision_limit": float(self.precision_limit) if self.precision_limit else None,
            "calibration_passed": self.calibration_passed,
            "service_required": self.service_required,
            "service_notes": self.service_notes,
            "next_calibration_due": self.next_calibration_due.isoformat() if self.next_calibration_due else None,
            "temperature": float(self.temperature) if self.temperature else None,
            "humidity": float(self.humidity) if self.humidity else None,
            "barometric_pressure": float(self.barometric_pressure) if self.barometric_pressure else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "calibrated_by": self.calibrated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class WaterConductivityTests(Base):
    """Water conductivity test results tracking"""
    __tablename__ = "water_conductivity_tests"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Test identification
    test_date = Column(DateTime, nullable=False, index=True)
    test_time = Column(String(20), nullable=False)  # Time in EST format
    sample_id = Column(String(100), nullable=True)
    
    # Water source information
    water_source = Column(String(255), nullable=False)  # DI Water System A, Tap, etc.
    source_location = Column(String(255), nullable=True)  # Building, room, outlet
    
    # Test conditions
    water_temperature = Column(Numeric(5, 2), nullable=True)  # °C
    ambient_temperature = Column(Numeric(5, 2), nullable=True)  # °C
    
    # Conductivity measurements
    conductivity_reading = Column(Numeric(8, 3), nullable=False)  # µS/cm
    conductivity_units = Column(String(20), default="µS/cm")
    
    # Equipment used
    meter_model = Column(String(255), nullable=True)
    meter_serial = Column(String(100), nullable=True)
    probe_id = Column(String(100), nullable=True)
    last_calibration_date = Column(DateTime, nullable=True)
    
    # Quality standards
    specification_limit = Column(Numeric(8, 3), nullable=True)  # µS/cm max allowed
    meets_specification = Column(Boolean, default=True)
    
    # Multiple readings (for precision)
    reading_1 = Column(Numeric(8, 3), nullable=True)
    reading_2 = Column(Numeric(8, 3), nullable=True)
    reading_3 = Column(Numeric(8, 3), nullable=True)
    average_reading = Column(Numeric(8, 3), nullable=True)
    standard_deviation = Column(Numeric(8, 4), nullable=True)
    
    # Action taken
    action_required = Column(Boolean, default=False)
    action_taken = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    
    # Notes and observations
    notes = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    
    # Tracking
    # SQL Server Migration Marker: Add foreign key constraint syntax
    tested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    tester = relationship("User", foreign_keys=[tested_by])
    
    def __repr__(self):
        return f"<WaterConductivityTests(id={self.id}, date='{self.test_date}', conductivity={self.conductivity_reading})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "test_date": self.test_date.isoformat() if self.test_date else None,
            "test_time": self.test_time,
            "sample_id": self.sample_id,
            "water_source": self.water_source,
            "source_location": self.source_location,
            "water_temperature": float(self.water_temperature) if self.water_temperature else None,
            "ambient_temperature": float(self.ambient_temperature) if self.ambient_temperature else None,
            "conductivity_reading": float(self.conductivity_reading) if self.conductivity_reading else None,
            "conductivity_units": self.conductivity_units,
            "meter_model": self.meter_model,
            "meter_serial": self.meter_serial,
            "probe_id": self.probe_id,
            "last_calibration_date": self.last_calibration_date.isoformat() if self.last_calibration_date else None,
            "specification_limit": float(self.specification_limit) if self.specification_limit else None,
            "meets_specification": self.meets_specification,
            "reading_1": float(self.reading_1) if self.reading_1 else None,
            "reading_2": float(self.reading_2) if self.reading_2 else None,
            "reading_3": float(self.reading_3) if self.reading_3 else None,
            "average_reading": float(self.average_reading) if self.average_reading else None,
            "standard_deviation": float(self.standard_deviation) if self.standard_deviation else None,
            "action_required": self.action_required,
            "action_taken": self.action_taken,
            "follow_up_required": self.follow_up_required,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "notes": self.notes,
            "observations": self.observations,
            "tested_by": self.tested_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }