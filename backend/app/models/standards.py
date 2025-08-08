"""
Standards models for MM and FlameAA standards tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

# MM Standards Models
class MMStandards(Base):
    """MM (Metals) Standards preparation and tracking"""
    __tablename__ = "mm_standards"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Standard identification
    standard_name = Column(String(255), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, unique=True)
    standard_type = Column(String(100), nullable=False)  # QC, Calibration, Spike, etc.
    
    # Preparation details
    preparation_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Concentration and composition
    target_concentration = Column(Numeric(12, 6), nullable=False)  # mg/L
    actual_concentration = Column(Numeric(12, 6), nullable=True)   # verified concentration
    matrix = Column(String(100), nullable=True)  # DI water, 2% HNO3, etc.
    
    # Source and preparation
    source_material = Column(String(255), nullable=True)  # Parent standard or stock
    dilution_factor = Column(Numeric(10, 4), nullable=True)
    total_volume = Column(Numeric(10, 3), nullable=False)  # mL
    
    # Elements/analytes
    elements = Column(Text, nullable=True)  # JSON string of element concentrations
    
    # Quality control
    verification_method = Column(String(100), nullable=True)
    certified = Column(Boolean, default=False)
    certificate_number = Column(String(100), nullable=True)
    
    # Usage tracking
    initial_volume = Column(Numeric(10, 3), nullable=False)
    current_volume = Column(Numeric(10, 3), nullable=False)
    
    # Status and notes
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Tracking
    # SQL Server Migration Marker: Add foreign key constraint syntax
    prepared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    preparer = relationship("User", foreign_keys=[prepared_by])
    history_entries = relationship("MMStandardsHistory", back_populates="standard")
    
    def __repr__(self):
        return f"<MMStandards(id={self.id}, standard_name='{self.standard_name}', batch='{self.batch_number}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "standard_name": self.standard_name,
            "batch_number": self.batch_number,
            "standard_type": self.standard_type,
            "preparation_date": self.preparation_date.isoformat() if self.preparation_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "target_concentration": float(self.target_concentration) if self.target_concentration else None,
            "actual_concentration": float(self.actual_concentration) if self.actual_concentration else None,
            "matrix": self.matrix,
            "source_material": self.source_material,
            "dilution_factor": float(self.dilution_factor) if self.dilution_factor else None,
            "total_volume": float(self.total_volume) if self.total_volume else None,
            "elements": self.elements,
            "verification_method": self.verification_method,
            "certified": self.certified,
            "certificate_number": self.certificate_number,
            "initial_volume": float(self.initial_volume) if self.initial_volume else None,
            "current_volume": float(self.current_volume) if self.current_volume else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "prepared_by": self.prepared_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class MMStandardsHistory(Base):
    """History tracking for MM Standards changes"""
    __tablename__ = "mm_standards_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main standard
    # SQL Server Migration Marker: Add foreign key constraint syntax
    standard_id = Column(Integer, ForeignKey("mm_standards.id"), nullable=False)
    
    # Change tracking
    action = Column(String(50), nullable=False)  # created, updated, used, verified, disposed
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Usage tracking
    volume_used = Column(Numeric(10, 3), nullable=True)  # mL used
    remaining_volume = Column(Numeric(10, 3), nullable=True)
    
    # Analysis information (when used)
    analysis_type = Column(String(100), nullable=True)  # ICP-MS, ICP-OES, AA, etc.
    instrument_used = Column(String(255), nullable=True)
    
    # Notes and reason
    notes = Column(Text, nullable=True)
    reason = Column(String(255), nullable=True)
    
    # User who made the change
    # SQL Server Migration Marker: Add foreign key constraint syntax
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamp
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    changed_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    standard = relationship("MMStandards", back_populates="history_entries")
    user = relationship("User", foreign_keys=[changed_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "standard_id": self.standard_id,
            "action": self.action,
            "field_changed": self.field_changed,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "volume_used": float(self.volume_used) if self.volume_used else None,
            "remaining_volume": float(self.remaining_volume) if self.remaining_volume else None,
            "analysis_type": self.analysis_type,
            "instrument_used": self.instrument_used,
            "notes": self.notes,
            "reason": self.reason,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None
        }

# FlameAA Standards Models
class FlameAAStandards(Base):
    """Flame AA (Atomic Absorption) Standards preparation and tracking"""
    __tablename__ = "flameaa_standards"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Standard identification
    standard_name = Column(String(255), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, unique=True)
    element = Column(String(20), nullable=False)  # Pb, Cd, Cr, etc.
    
    # Preparation details
    preparation_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Concentration
    target_concentration = Column(Numeric(10, 4), nullable=False)  # mg/L
    actual_concentration = Column(Numeric(10, 4), nullable=True)   # verified concentration
    matrix = Column(String(100), nullable=True)  # Matrix composition
    
    # Source and preparation
    source_standard = Column(String(255), nullable=True)  # 1000 ppm stock, etc.
    dilution_series = Column(Text, nullable=True)  # Step-by-step dilution
    total_volume = Column(Numeric(10, 3), nullable=False)  # mL
    
    # Flame AA specific
    wavelength = Column(Numeric(6, 2), nullable=True)  # nm
    slit_width = Column(Numeric(4, 2), nullable=True)  # nm
    flame_type = Column(String(50), nullable=True)  # Air-Acetylene, N2O-Acetylene
    
    # Quality control
    absorbance_value = Column(Numeric(8, 4), nullable=True)
    linearity_check = Column(Boolean, default=False)
    correlation_coefficient = Column(Numeric(6, 4), nullable=True)  # R²
    
    # Usage tracking
    initial_volume = Column(Numeric(10, 3), nullable=False)
    current_volume = Column(Numeric(10, 3), nullable=False)
    
    # Status and notes
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Tracking
    # SQL Server Migration Marker: Add foreign key constraint syntax
    prepared_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    preparer = relationship("User", foreign_keys=[prepared_by])
    history_entries = relationship("FlameAAStandardsHistory", back_populates="standard")
    
    def to_dict(self):
        return {
            "id": self.id,
            "standard_name": self.standard_name,
            "batch_number": self.batch_number,
            "element": self.element,
            "preparation_date": self.preparation_date.isoformat() if self.preparation_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "target_concentration": float(self.target_concentration) if self.target_concentration else None,
            "actual_concentration": float(self.actual_concentration) if self.actual_concentration else None,
            "matrix": self.matrix,
            "source_standard": self.source_standard,
            "dilution_series": self.dilution_series,
            "total_volume": float(self.total_volume) if self.total_volume else None,
            "wavelength": float(self.wavelength) if self.wavelength else None,
            "slit_width": float(self.slit_width) if self.slit_width else None,
            "flame_type": self.flame_type,
            "absorbance_value": float(self.absorbance_value) if self.absorbance_value else None,
            "linearity_check": self.linearity_check,
            "correlation_coefficient": float(self.correlation_coefficient) if self.correlation_coefficient else None,
            "initial_volume": float(self.initial_volume) if self.initial_volume else None,
            "current_volume": float(self.current_volume) if self.current_volume else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "prepared_by": self.prepared_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class FlameAAStandardsHistory(Base):
    """History tracking for FlameAA Standards changes"""
    __tablename__ = "flameaa_standards_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main standard
    # SQL Server Migration Marker: Add foreign key constraint syntax
    standard_id = Column(Integer, ForeignKey("flameaa_standards.id"), nullable=False)
    
    # Change tracking
    action = Column(String(50), nullable=False)  # created, updated, used, verified, disposed
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Usage tracking
    volume_used = Column(Numeric(10, 3), nullable=True)  # mL used
    remaining_volume = Column(Numeric(10, 3), nullable=True)
    
    # Analysis information
    analysis_date = Column(DateTime, nullable=True)
    instrument_used = Column(String(255), nullable=True)
    method_used = Column(String(100), nullable=True)
    
    # Notes and reason
    notes = Column(Text, nullable=True)
    reason = Column(String(255), nullable=True)
    
    # User who made the change
    # SQL Server Migration Marker: Add foreign key constraint syntax
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamp
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    changed_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    standard = relationship("FlameAAStandards", back_populates="history_entries")
    user = relationship("User", foreign_keys=[changed_by])