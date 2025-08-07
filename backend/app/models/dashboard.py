"""
Dashboard preferences model for storing user customization settings
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class DashboardPreferences(Base):
    """User dashboard preferences and layout settings"""
    __tablename__ = "dashboard_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Layout preferences
    layout_type = Column(String(50), default="two_column")  # two_column, single_column, grid
    chart_positions = Column(JSON)  # JSON array of chart positions and types
    
    # Chart preferences
    default_chart_type = Column(String(50), default="line")  # line, bar, area, scatter
    default_data_source = Column(String(100))
    auto_refresh = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=300)  # seconds
    
    # Display preferences
    show_sidebar = Column(Boolean, default=True)
    sidebar_collapsed = Column(Boolean, default=False)
    theme_preference = Column(String(20), default="default")  # default, dark, high_contrast
    
    # Data preferences
    default_date_range = Column(String(20), default="7_days")  # 7_days, 30_days, 90_days, all
    max_data_points = Column(Integer, default=100)
    
    # Saved configurations
    saved_charts = Column(JSON)  # JSON array of saved chart configurations
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="dashboard_preferences")
    
    def to_dict(self):
        """Convert preferences to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "layout_type": self.layout_type,
            "chart_positions": self.chart_positions,
            "default_chart_type": self.default_chart_type,
            "default_data_source": self.default_data_source,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "show_sidebar": self.show_sidebar,
            "sidebar_collapsed": self.sidebar_collapsed,
            "theme_preference": self.theme_preference,
            "default_date_range": self.default_date_range,
            "max_data_points": self.max_data_points,
            "saved_charts": self.saved_charts or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_default_preferences(self):
        """Get default preferences for new users"""
        return {
            "layout_type": "two_column",
            "chart_positions": [
                {"id": 1, "type": "placeholder", "title": "Chart 1", "x": 0, "y": 0},
                {"id": 2, "type": "placeholder", "title": "Chart 2", "x": 1, "y": 0}
            ],
            "default_chart_type": "line",
            "default_data_source": None,
            "auto_refresh": True,
            "refresh_interval": 300,
            "show_sidebar": True,
            "sidebar_collapsed": False,
            "theme_preference": "default",
            "default_date_range": "7_days",
            "max_data_points": 100,
            "saved_charts": []
        }