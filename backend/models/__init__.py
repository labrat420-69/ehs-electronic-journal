"""
Initialize all models for SQLAlchemy
"""

from backend.models.user import User, UserRole
from backend.models.department import Department
from backend.models.chemical_inventory import ChemicalInventoryLog, ChemicalInventoryHistory
from backend.models.reagents import (
    MMReagents, MMReagentsHistory,
    PbReagents, PbReagentsHistory, 
    TCLPReagents, TCLPReagentsHistory
)
from backend.models.standards import (
    MMStandards, MMStandardsHistory,
    FlameAAStandards, FlameAAStandardsHistory
)
from backend.models.equipment import (
    Equipment, PipetteLog, WaterConductivityTests
)
from backend.models.maintenance import (
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