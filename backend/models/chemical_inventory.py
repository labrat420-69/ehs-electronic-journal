"""
Chemical Inventory models for tracking chemical stock and usage
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ChemicalInventoryLog(Base):
    """Main chemical inventory tracking table"""
    __tablename__ = "chemical_inventory_log"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Chemical identification
    chemical_name = Column(String(255), nullable=False, index=True)
    cas_number = Column(String(50), nullable=True, index=True)
    manufacturer = Column(String(255), nullable=True)
    catalog_number = Column(String(100), nullable=True)
    lot_number = Column(String(100), nullable=True)
    
    # Inventory details
    container_size = Column(String(50), nullable=True)  # e.g., "500ml", "1L", "100g"
    current_quantity = Column(Numeric(10, 3), nullable=False, default=0)
    unit = Column(String(20), nullable=False)  # ml, L, g, kg, etc.
    
    # Storage information
    storage_location = Column(String(255), nullable=True)
    storage_temperature = Column(String(50), nullable=True)  # Room temp, 4°C, -20°C, etc.
    storage_conditions = Column(Text, nullable=True)
    
    # Safety information
    hazard_class = Column(String(100), nullable=True)
    safety_notes = Column(Text, nullable=True)
    
    # Dates and expiration
    received_date = Column(DateTime, nullable=True)
    expiration_date = Column(DateTime, nullable=True)
    opened_date = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_hazardous = Column(Boolean, default=False)
    
    # Tracking information
    # SQL Server Migration Marker: Add foreign key constraint syntax
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    # SQL Server Migration Marker: Change func.now() to GETUTCDATE()
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    history_entries = relationship("ChemicalInventoryHistory", back_populates="chemical")
    
    def __repr__(self):
        return f"<ChemicalInventoryLog(id={self.id}, chemical_name='{self.chemical_name}', quantity={self.current_quantity} {self.unit})>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "chemical_name": self.chemical_name,
            "cas_number": self.cas_number,
            "manufacturer": self.manufacturer,
            "catalog_number": self.catalog_number,
            "lot_number": self.lot_number,
            "container_size": self.container_size,
            "current_quantity": float(self.current_quantity) if self.current_quantity else 0,
            "unit": self.unit,
            "storage_location": self.storage_location,
            "storage_temperature": self.storage_temperature,
            "storage_conditions": self.storage_conditions,
            "hazard_class": self.hazard_class,
            "safety_notes": self.safety_notes,
            "received_date": self.received_date.isoformat() if self.received_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "opened_date": self.opened_date.isoformat() if self.opened_date else None,
            "is_active": self.is_active,
            "is_hazardous": self.is_hazardous,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ChemicalInventoryHistory(Base):
    """History tracking for chemical inventory changes"""
    __tablename__ = "chemical_inventory_history"
    
    # SQL Server Migration Marker: Change SERIAL to IDENTITY(1,1)
    id = Column(Integer, primary_key=True, index=True)
    
    # Reference to main chemical inventory
    # SQL Server Migration Marker: Add foreign key constraint syntax
    chemical_id = Column(Integer, ForeignKey("chemical_inventory_log.id"), nullable=False)
    
    # Change tracking
    action = Column(String(50), nullable=False)  # created, updated, quantity_changed, disposed
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Quantity tracking for usage
    quantity_change = Column(Numeric(10, 3), nullable=True)  # Positive for additions, negative for usage
    remaining_quantity = Column(Numeric(10, 3), nullable=True)
    
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
    chemical = relationship("ChemicalInventoryLog", back_populates="history_entries")
    user = relationship("User", foreign_keys=[changed_by])
    
    def __repr__(self):
        return f"<ChemicalInventoryHistory(id={self.id}, chemical_id={self.chemical_id}, action='{self.action}')>"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "chemical_id": self.chemical_id,
            "action": self.action,
            "field_changed": self.field_changed,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "quantity_change": float(self.quantity_change) if self.quantity_change else None,
            "remaining_quantity": float(self.remaining_quantity) if self.remaining_quantity else None,
            "notes": self.notes,
            "reason": self.reason,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None
        }