"""
Reagents models for MM, Pb, and TCLP reagents tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

# MM Reagents Models
class MMReagents(Base):
    """MM Reagents preparation and tracking"""
    __tablename__ = "mm_reagents"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reagent identification
    reagent_name = Column(String(255), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, unique=True)
    
    # Preparation details
    preparation_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Volume and concentration
    total_volume = Column(Numeric(10, 3), nullable=False)  # in mL
    concentration = Column(String(100), nullable=True)
    
    # Preparation method
    preparation_method = Column(Text, nullable=True)
    chemicals_used = Column(Text, nullable=True)
    
    # Quality control
    ph_value = Column(Numeric(4, 2), nullable=True)
    conductivity = Column(Numeric(10, 3), nullable=True)
    
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
    history_entries = relationship("MMReagentsHistory", back_populates="reagent")
    
    def __repr__(self):
        return f"<MMReagents(id={self.id}, reagent_name='{self.reagent_name}', batch='{self.batch_number}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "reagent_name": self.reagent_name,
            "batch_number": self.batch_number,
            "preparation_date": self.preparation_date.isoformat() if self.preparation_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "total_volume": float(self.total_volume) if self.total_volume else None,
            "concentration": self.concentration,
            "preparation_method": self.preparation_method,
            "chemicals_used": self.chemicals_used,
            "ph_value": float(self.ph_value) if self.ph_value else None,
            "conductivity": float(self.conductivity) if self.conductivity else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "prepared_by": self.prepared_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class MMReagentsHistory(Base):
    """History tracking for MM Reagents changes"""
    __tablename__ = "mm_reagents_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main reagent
    # SQL Server Migration Marker: Add foreign key constraint syntax
    reagent_id = Column(Integer, ForeignKey("mm_reagents.id"), nullable=False)
    
    # Change tracking
    action = Column(String(50), nullable=False)  # created, updated, used, disposed
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Usage tracking
    volume_used = Column(Numeric(10, 3), nullable=True)  # mL used
    remaining_volume = Column(Numeric(10, 3), nullable=True)
    
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
    reagent = relationship("MMReagents", back_populates="history_entries")
    user = relationship("User", foreign_keys=[changed_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "reagent_id": self.reagent_id,
            "action": self.action,
            "field_changed": self.field_changed,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "volume_used": float(self.volume_used) if self.volume_used else None,
            "remaining_volume": float(self.remaining_volume) if self.remaining_volume else None,
            "notes": self.notes,
            "reason": self.reason,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None
        }

# Pb Reagents Models
class PbReagents(Base):
    """Pb (Lead) Reagents preparation and tracking"""
    __tablename__ = "pb_reagents"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reagent identification
    reagent_name = Column(String(255), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, unique=True)
    
    # Preparation details
    preparation_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Volume and concentration
    total_volume = Column(Numeric(10, 3), nullable=False)  # in mL
    lead_concentration = Column(Numeric(10, 6), nullable=True)  # mg/L
    
    # Preparation method
    preparation_method = Column(Text, nullable=True)
    source_standard = Column(String(255), nullable=True)
    
    # Quality control
    verified_concentration = Column(Numeric(10, 6), nullable=True)
    verification_date = Column(DateTime, nullable=True)
    
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
    history_entries = relationship("PbReagentsHistory", back_populates="reagent")
    
    def to_dict(self):
        return {
            "id": self.id,
            "reagent_name": self.reagent_name,
            "batch_number": self.batch_number,
            "preparation_date": self.preparation_date.isoformat() if self.preparation_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "total_volume": float(self.total_volume) if self.total_volume else None,
            "lead_concentration": float(self.lead_concentration) if self.lead_concentration else None,
            "preparation_method": self.preparation_method,
            "source_standard": self.source_standard,
            "verified_concentration": float(self.verified_concentration) if self.verified_concentration else None,
            "verification_date": self.verification_date.isoformat() if self.verification_date else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "prepared_by": self.prepared_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class PbReagentsHistory(Base):
    """History tracking for Pb Reagents changes"""
    __tablename__ = "pb_reagents_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main reagent
    # SQL Server Migration Marker: Add foreign key constraint syntax
    reagent_id = Column(Integer, ForeignKey("pb_reagents.id"), nullable=False)
    
    # Change tracking (similar structure to MM Reagents History)
    action = Column(String(50), nullable=False)
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Usage tracking
    volume_used = Column(Numeric(10, 3), nullable=True)
    remaining_volume = Column(Numeric(10, 3), nullable=True)
    
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
    reagent = relationship("PbReagents", back_populates="history_entries")
    user = relationship("User", foreign_keys=[changed_by])

# TCLP Reagents Models
class TCLPReagents(Base):
    """TCLP (Toxicity Characteristic Leaching Procedure) Reagents"""
    __tablename__ = "tclp_reagents"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reagent identification
    reagent_name = Column(String(255), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, unique=True)
    reagent_type = Column(String(100), nullable=False)  # Extraction Fluid #1, #2, etc.
    
    # Preparation details
    preparation_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Volume and composition
    total_volume = Column(Numeric(10, 3), nullable=False)  # in mL
    ph_target = Column(Numeric(4, 2), nullable=True)
    final_ph = Column(Numeric(4, 2), nullable=True)
    
    # Preparation method
    preparation_method = Column(Text, nullable=True)
    chemicals_used = Column(Text, nullable=True)
    
    # Quality control
    conductivity = Column(Numeric(10, 3), nullable=True)
    verification_passed = Column(Boolean, default=False)
    
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
    history_entries = relationship("TCLPReagentsHistory", back_populates="reagent")
    
    def to_dict(self):
        return {
            "id": self.id,
            "reagent_name": self.reagent_name,
            "batch_number": self.batch_number,
            "reagent_type": self.reagent_type,
            "preparation_date": self.preparation_date.isoformat() if self.preparation_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "total_volume": float(self.total_volume) if self.total_volume else None,
            "ph_target": float(self.ph_target) if self.ph_target else None,
            "final_ph": float(self.final_ph) if self.final_ph else None,
            "preparation_method": self.preparation_method,
            "chemicals_used": self.chemicals_used,
            "conductivity": float(self.conductivity) if self.conductivity else None,
            "verification_passed": self.verification_passed,
            "is_active": self.is_active,
            "notes": self.notes,
            "prepared_by": self.prepared_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class TCLPReagentsHistory(Base):
    """History tracking for TCLP Reagents changes"""
    __tablename__ = "tclp_reagents_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main reagent
    # SQL Server Migration Marker: Add foreign key constraint syntax
    reagent_id = Column(Integer, ForeignKey("tclp_reagents.id"), nullable=False)
    
    # Change tracking (similar structure to other reagent histories)
    action = Column(String(50), nullable=False)
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Usage tracking
    volume_used = Column(Numeric(10, 3), nullable=True)
    remaining_volume = Column(Numeric(10, 3), nullable=True)
    
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
    reagent = relationship("TCLPReagents", back_populates="history_entries")

# Mercury Standards Models (similar to MM Standards)
class MercuryStandards(Base):
    """Mercury Standards preparation and tracking"""
    __tablename__ = "mercury_standards"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Standard identification
    standard_name = Column(String(255), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, unique=True)
    standard_type = Column(String(100), nullable=False)  # QC, Calibration, Spike, etc.
    
    # Preparation details
    preparation_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Concentration details
    target_concentration = Column(Numeric(12, 6), nullable=False)  # in ppm
    actual_concentration = Column(Numeric(12, 6), nullable=True)
    
    # Matrix and source
    matrix = Column(String(100), nullable=True)
    source_material = Column(String(255), nullable=True)
    dilution_factor = Column(Numeric(10, 6), nullable=True)
    
    # Volume tracking
    total_volume = Column(Numeric(10, 3), nullable=False)  # in mL
    initial_volume = Column(Numeric(10, 3), nullable=False)  # in mL
    current_volume = Column(Numeric(10, 3), nullable=False)  # in mL
    
    # Elements (for multi-element standards)
    elements = Column(Text, nullable=True)  # JSON string of elements and concentrations
    
    # Verification details
    verification_method = Column(String(255), nullable=True)
    certified = Column(Boolean, default=False)
    certificate_number = Column(String(100), nullable=True)
    
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
    history_entries = relationship("MercuryStandardsHistory", back_populates="standard")
    
    def to_dict(self):
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
            "initial_volume": float(self.initial_volume) if self.initial_volume else None,
            "current_volume": float(self.current_volume) if self.current_volume else None,
            "elements": self.elements,
            "verification_method": self.verification_method,
            "certified": self.certified,
            "certificate_number": self.certificate_number,
            "is_active": self.is_active,
            "notes": self.notes,
            "prepared_by": self.prepared_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class MercuryStandardsHistory(Base):
    """History tracking for Mercury Standards changes"""
    __tablename__ = "mercury_standards_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main standard
    # SQL Server Migration Marker: Add foreign key constraint syntax
    standard_id = Column(Integer, ForeignKey("mercury_standards.id"), nullable=False)
    
    # Change tracking
    action = Column(String(50), nullable=False)
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Usage tracking
    volume_used = Column(Numeric(10, 3), nullable=True)
    remaining_volume = Column(Numeric(10, 3), nullable=True)
    
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
    standard = relationship("MercuryStandards", back_populates="history_entries")

# Mercury Reagents Models (similar to MM Reagents)
class MercuryReagents(Base):
    """Mercury Reagents preparation and tracking"""
    __tablename__ = "mercury_reagents"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reagent identification
    reagent_name = Column(String(255), nullable=False, index=True)
    batch_number = Column(String(100), nullable=False, unique=True)
    
    # Preparation details
    preparation_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    
    # Volume and concentration
    total_volume = Column(Numeric(10, 3), nullable=False)  # in mL
    concentration = Column(String(100), nullable=True)
    
    # Preparation method
    preparation_method = Column(Text, nullable=True)
    chemicals_used = Column(Text, nullable=True)
    
    # Quality control
    ph_value = Column(Numeric(4, 2), nullable=True)
    conductivity = Column(Numeric(10, 3), nullable=True)
    
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
    history_entries = relationship("MercuryReagentsHistory", back_populates="reagent")
    
    def to_dict(self):
        return {
            "id": self.id,
            "reagent_name": self.reagent_name,
            "batch_number": self.batch_number,
            "preparation_date": self.preparation_date.isoformat() if self.preparation_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "total_volume": float(self.total_volume) if self.total_volume else None,
            "concentration": self.concentration,
            "preparation_method": self.preparation_method,
            "chemicals_used": self.chemicals_used,
            "ph_value": float(self.ph_value) if self.ph_value else None,
            "conductivity": float(self.conductivity) if self.conductivity else None,
            "is_active": self.is_active,
            "notes": self.notes,
            "prepared_by": self.prepared_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class MercuryReagentsHistory(Base):
    """History tracking for Mercury Reagents changes"""
    __tablename__ = "mercury_reagents_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main reagent
    # SQL Server Migration Marker: Add foreign key constraint syntax
    reagent_id = Column(Integer, ForeignKey("mercury_reagents.id"), nullable=False)
    
    # Change tracking
    action = Column(String(50), nullable=False)
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Usage tracking
    volume_used = Column(Numeric(10, 3), nullable=True)
    remaining_volume = Column(Numeric(10, 3), nullable=True)
    
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
    reagent = relationship("MercuryReagents", back_populates="history_entries")
    user = relationship("User", foreign_keys=[changed_by])