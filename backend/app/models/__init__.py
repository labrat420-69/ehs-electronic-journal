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

# Export all models for easy import
__all__ = [
    "User", "UserRole", "Department",
    "ChemicalInventoryLog", "ChemicalInventoryHistory",
    "MMReagents", "MMReagentsHistory",
    "PbReagents", "PbReagentsHistory",
    "TCLPReagents", "TCLPReagentsHistory"
]