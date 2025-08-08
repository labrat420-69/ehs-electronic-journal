"""
Initialize all models for SQLAlchemy
"""

from app.models.user import User, UserRole
from app.models.department import Department
from app.models.chemical_inventory import ChemicalInventoryLog, ChemicalInventoryHistory
from app.models.reagents import (
    MMReagents, MMReagentsHistory,
    PbReagents, PbReagentsHistory, 
    TCLPReagents, TCLPReagentsHistory
)
from app.models.standards import (
    MMStandards, MMStandardsHistory,
    FlameAAStandards, FlameAAStandardsHistory
)
from app.models.equipment import (
    Equipment, PipetteLog, WaterConductivityTests
)
from app.models.maintenance import (
    ICPOESMaintenanceLog, ICPOESMaintenanceHistory,
    MaintenanceType, MaintenanceStatus
)

# Export all models for easy import
__all__ = [
    # User and department models
    "User", "UserRole", "Department",
    
    # Chemical inventory models
    "ChemicalInventoryLog", "ChemicalInventoryHistory",
    
    # Reagents models
    "MMReagents", "MMReagentsHistory",
    "PbReagents", "PbReagentsHistory",
    "TCLPReagents", "TCLPReagentsHistory",
    
    # Standards models
    "MMStandards", "MMStandardsHistory",
    "FlameAAStandards", "FlameAAStandardsHistory",
    
    # Equipment models
    "Equipment", "PipetteLog", "WaterConductivityTests",
    
    # Maintenance models
    "ICPOESMaintenanceLog", "ICPOESMaintenanceHistory",
    "MaintenanceType", "MaintenanceStatus"
]