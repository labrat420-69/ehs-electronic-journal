"""
Maintenance models for ICP-OES and other equipment maintenance tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base
import enum

class MaintenanceType(enum.Enum):
    """Types of maintenance activities"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"

class MaintenanceStatus(enum.Enum):
    """Status of maintenance activities"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

class ICPOESMaintenanceLog(Base):
    """ICP-OES (Inductively Coupled Plasma - Optical Emission Spectroscopy) maintenance tracking"""
    __tablename__ = "icp_oes_maintenance_log"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Maintenance identification
    maintenance_date = Column(DateTime, nullable=False, index=True)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    maintenance_status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.COMPLETED)
    
    # Equipment identification
    instrument_id = Column(String(100), nullable=False)
    instrument_model = Column(String(255), nullable=True)
    serial_number = Column(String(100), nullable=True)
    
    # Maintenance details
    maintenance_category = Column(String(100), nullable=False)  # Torch, Pump, Optics, etc.
    work_performed = Column(Text, nullable=False)
    
    # Torch maintenance specifics
    torch_condition = Column(String(100), nullable=True)  # Good, Fair, Replaced
    torch_hours = Column(Numeric(8, 2), nullable=True)  # Operating hours
    torch_replaced = Column(Boolean, default=False)
    new_torch_serial = Column(String(100), nullable=True)
    
    # Pump maintenance
    pump_tubing_replaced = Column(Boolean, default=False)
    pump_flow_rate = Column(Numeric(6, 3), nullable=True)  # mL/min
    pump_pressure = Column(Numeric(6, 2), nullable=True)  # psi
    
    # Optics maintenance
    optics_cleaned = Column(Boolean, default=False)
    purge_gas_flow = Column(Numeric(6, 2), nullable=True)  # L/min
    optical_chamber_condition = Column(String(100), nullable=True)
    
    # Nebulizer maintenance
    nebulizer_cleaned = Column(Boolean, default=False)
    nebulizer_type = Column(String(100), nullable=True)
    uptake_rate = Column(Numeric(6, 3), nullable=True)  # mL/min
    
    # Argon gas system
    argon_pressure = Column(Numeric(6, 2), nullable=True)  # psi
    argon_flow_plasma = Column(Numeric(6, 2), nullable=True)  # L/min
    argon_flow_auxiliary = Column(Numeric(6, 2), nullable=True)  # L/min
    argon_flow_nebulizer = Column(Numeric(6, 3), nullable=True)  # L/min
    
    # Performance checks
    wavelength_calibration = Column(Boolean, default=False)
    intensity_check = Column(Boolean, default=False)
    background_check = Column(Boolean, default=False)
    stability_check = Column(Boolean, default=False)
    
    # Performance results
    detection_limits_acceptable = Column(Boolean, default=True)
    precision_acceptable = Column(Boolean, default=True)
    accuracy_acceptable = Column(Boolean, default=True)
    
    # Parts and consumables
    parts_replaced = Column(Text, nullable=True)  # JSON list of parts
    consumables_used = Column(Text, nullable=True)  # JSON list of consumables
    cost_estimate = Column(Numeric(10, 2), nullable=True)  # USD
    
    # Issues and resolutions
    issues_found = Column(Text, nullable=True)
    resolutions = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    next_maintenance_due = Column(DateTime, nullable=True)
    
    # Duration and effort
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_hours = Column(Numeric(5, 2), nullable=True)
    
    # Documentation
    procedure_followed = Column(String(255), nullable=True)  # SOP reference
    photos_taken = Column(Boolean, default=False)
    documentation_path = Column(String(500), nullable=True)  # File path for photos/docs
    
    # Status and notes
    instrument_operational = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Tracking
    # SQL Server Migration Marker: Add foreign key constraint syntax
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    supervisor_approval = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    technician = relationship("User", foreign_keys=[performed_by])
    supervisor = relationship("User", foreign_keys=[supervisor_approval])
    history_entries = relationship("ICPOESMaintenanceHistory", back_populates="maintenance_log")
    
    def __repr__(self):
        return f"<ICPOESMaintenanceLog(id={self.id}, date='{self.maintenance_date}', type='{self.maintenance_type.value}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "maintenance_date": self.maintenance_date.isoformat() if self.maintenance_date else None,
            "maintenance_type": self.maintenance_type.value,
            "maintenance_status": self.maintenance_status.value,
            "instrument_id": self.instrument_id,
            "instrument_model": self.instrument_model,
            "serial_number": self.serial_number,
            "maintenance_category": self.maintenance_category,
            "work_performed": self.work_performed,
            "torch_condition": self.torch_condition,
            "torch_hours": float(self.torch_hours) if self.torch_hours else None,
            "torch_replaced": self.torch_replaced,
            "new_torch_serial": self.new_torch_serial,
            "pump_tubing_replaced": self.pump_tubing_replaced,
            "pump_flow_rate": float(self.pump_flow_rate) if self.pump_flow_rate else None,
            "pump_pressure": float(self.pump_pressure) if self.pump_pressure else None,
            "optics_cleaned": self.optics_cleaned,
            "purge_gas_flow": float(self.purge_gas_flow) if self.purge_gas_flow else None,
            "optical_chamber_condition": self.optical_chamber_condition,
            "nebulizer_cleaned": self.nebulizer_cleaned,
            "nebulizer_type": self.nebulizer_type,
            "uptake_rate": float(self.uptake_rate) if self.uptake_rate else None,
            "argon_pressure": float(self.argon_pressure) if self.argon_pressure else None,
            "argon_flow_plasma": float(self.argon_flow_plasma) if self.argon_flow_plasma else None,
            "argon_flow_auxiliary": float(self.argon_flow_auxiliary) if self.argon_flow_auxiliary else None,
            "argon_flow_nebulizer": float(self.argon_flow_nebulizer) if self.argon_flow_nebulizer else None,
            "wavelength_calibration": self.wavelength_calibration,
            "intensity_check": self.intensity_check,
            "background_check": self.background_check,
            "stability_check": self.stability_check,
            "detection_limits_acceptable": self.detection_limits_acceptable,
            "precision_acceptable": self.precision_acceptable,
            "accuracy_acceptable": self.accuracy_acceptable,
            "parts_replaced": self.parts_replaced,
            "consumables_used": self.consumables_used,
            "cost_estimate": float(self.cost_estimate) if self.cost_estimate else None,
            "issues_found": self.issues_found,
            "resolutions": self.resolutions,
            "follow_up_required": self.follow_up_required,
            "next_maintenance_due": self.next_maintenance_due.isoformat() if self.next_maintenance_due else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_hours": float(self.duration_hours) if self.duration_hours else None,
            "procedure_followed": self.procedure_followed,
            "photos_taken": self.photos_taken,
            "documentation_path": self.documentation_path,
            "instrument_operational": self.instrument_operational,
            "notes": self.notes,
            "performed_by": self.performed_by,
            "supervisor_approval": self.supervisor_approval,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ICPOESMaintenanceHistory(Base):
    """History tracking for ICP-OES maintenance log changes"""
    __tablename__ = "icp_oes_maintenance_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main maintenance log
    # SQL Server Migration Marker: Add foreign key constraint syntax
    maintenance_log_id = Column(Integer, ForeignKey("icp_oes_maintenance_log.id"), nullable=False)
    
    # Change tracking
    action = Column(String(50), nullable=False)  # created, updated, approved, cancelled
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Status changes
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=True)
    
    # Notes and reason for change
    notes = Column(Text, nullable=True)
    reason = Column(String(255), nullable=True)
    
    # User who made the change
    # SQL Server Migration Marker: Add foreign key constraint syntax
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamp
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    changed_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    maintenance_log = relationship("ICPOESMaintenanceLog", back_populates="history_entries")
    user = relationship("User", foreign_keys=[changed_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "maintenance_log_id": self.maintenance_log_id,
            "action": self.action,
            "field_changed": self.field_changed,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "notes": self.notes,
            "reason": self.reason,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None
        }