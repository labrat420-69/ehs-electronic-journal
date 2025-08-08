"""
Analytics models for dashboard graphs, presets, and configuration
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class GraphPreset(Base):
    """Store graph presets for customizable dashboard analytics"""
    __tablename__ = "graph_presets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Graph configuration
    graph_type = Column(String(50), nullable=False)  # line, bar, area, candlestick, etc.
    x_axis_field = Column(String(100), nullable=False)  # data field for X axis
    y_axis_field = Column(String(100), nullable=False)  # data field for Y axis
    data_source = Column(String(100), nullable=False)  # chemical_inventory, waste, reagents, etc.
    
    # Visual configuration
    config = Column(JSON, nullable=True)  # Stores graph styling, colors, etc.
    
    # User and sharing
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)  # Can other users see this preset
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<GraphPreset(id={self.id}, name='{self.name}', type='{self.graph_type}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "graph_type": self.graph_type,
            "x_axis_field": self.x_axis_field,
            "y_axis_field": self.y_axis_field,
            "data_source": self.data_source,
            "config": self.config,
            "created_by": self.created_by,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class DashboardReminder(Base):
    """Reminders and events for dashboard"""
    __tablename__ = "dashboard_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reminder_type = Column(String(50), nullable=False)  # event, reminder, deadline, etc.
    
    # Timing
    due_date = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    
    # Priority and status
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(50), default="active")  # active, completed, dismissed
    
    # User assignment
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    
    def __repr__(self):
        return f"<DashboardReminder(id={self.id}, title='{self.title}', due={self.due_date})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "reminder_type": self.reminder_type,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_completed": self.is_completed,
            "priority": self.priority,
            "status": self.status,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class DepartmentNote(Base):
    """Department-wide notes for dashboard"""
    __tablename__ = "department_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="general")  # general, announcement, procedure, etc.
    
    # Visibility and permissions
    is_pinned = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    department = Column(String(100), nullable=True)  # Restrict to specific department
    
    # User info
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<DepartmentNote(id={self.id}, title='{self.title}', type='{self.note_type}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "note_type": self.note_type,
            "is_pinned": self.is_pinned,
            "is_public": self.is_public,
            "department": self.department,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class WasteBox(Base):
    """Waste box tracking for disposal module"""
    __tablename__ = "waste_boxes"
    
    id = Column(Integer, primary_key=True, index=True)
    box_id = Column(String(100), unique=True, nullable=False, index=True)
    coc_job_id = Column(String(100), nullable=True, index=True)  # Chain of custody job ID
    
    # Box details
    box_type = Column(String(100), nullable=False)  # hazardous, non-hazardous, glass, etc.
    size = Column(String(50), nullable=False)  # small, medium, large
    location = Column(String(255), nullable=False)
    
    # Status tracking
    status = Column(String(50), default="active")  # active, full, disposed, in_storage
    fill_percentage = Column(Numeric(5, 2), default=0.0)  # 0.0 to 100.0
    
    # Dates
    created_date = Column(DateTime, server_default=func.now(), nullable=False)
    filled_date = Column(DateTime, nullable=True)
    disposed_date = Column(DateTime, nullable=True)
    storage_until_date = Column(DateTime, nullable=True)  # When extra samples can be disposed
    
    # User tracking
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    waste_items = relationship("WasteItem", back_populates="waste_box")
    
    def __repr__(self):
        return f"<WasteBox(id={self.id}, box_id='{self.box_id}', status='{self.status}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "box_id": self.box_id,
            "coc_job_id": self.coc_job_id,
            "box_type": self.box_type,
            "size": self.size,
            "location": self.location,
            "status": self.status,
            "fill_percentage": float(self.fill_percentage) if self.fill_percentage else 0.0,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "filled_date": self.filled_date.isoformat() if self.filled_date else None,
            "disposed_date": self.disposed_date.isoformat() if self.disposed_date else None,
            "storage_until_date": self.storage_until_date.isoformat() if self.storage_until_date else None,
            "created_by": self.created_by
        }

class WasteItem(Base):
    """Individual waste items in waste boxes"""
    __tablename__ = "waste_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Item details
    item_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    waste_type = Column(String(100), nullable=False)  # hazardous, non-hazardous, sharps, etc.
    quantity = Column(String(100), nullable=True)  # e.g., "500ml", "1 bottle"
    
    # Tracking
    coc_job_id = Column(String(100), nullable=True, index=True)
    sample_id = Column(String(100), nullable=True, index=True)
    is_extra_sample = Column(Boolean, default=False)
    
    # Box assignment
    waste_box_id = Column(Integer, ForeignKey("waste_boxes.id"), nullable=False)
    
    # Timestamps
    added_date = Column(DateTime, server_default=func.now(), nullable=False)
    disposal_ready_date = Column(DateTime, nullable=True)  # When extra sample can be disposed
    
    # User tracking
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    waste_box = relationship("WasteBox", back_populates="waste_items")
    creator = relationship("User", foreign_keys=[added_by])
    
    def __repr__(self):
        return f"<WasteItem(id={self.id}, name='{self.item_name}', box_id={self.waste_box_id})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "item_name": self.item_name,
            "description": self.description,
            "waste_type": self.waste_type,
            "quantity": self.quantity,
            "coc_job_id": self.coc_job_id,
            "sample_id": self.sample_id,
            "is_extra_sample": self.is_extra_sample,
            "waste_box_id": self.waste_box_id,
            "added_date": self.added_date.isoformat() if self.added_date else None,
            "disposal_ready_date": self.disposal_ready_date.isoformat() if self.disposal_ready_date else None,
            "added_by": self.added_by
        }