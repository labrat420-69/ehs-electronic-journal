"""
Chemical inventory routes
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from backend.database import get_db
from backend.models.chemical_inventory import ChemicalInventoryLog, ChemicalInventoryHistory
from backend.models.user import User
from backend.auth.jwt_handler import get_current_user, require_permissions
from backend.utils.validation import validate_required_fields

# Import templates - use the same pattern as main.py
from fastapi.templating import Jinja2Templates
from backend.utils.template_helpers import template_functions

templates = Jinja2Templates(directory="frontend/templates")
# Add template helper functions for robust role-based access control
templates.env.globals.update(template_functions)

router = APIRouter(prefix="/chemical_inventory", tags=["Chemical Inventory"])

# Test route without authentication
@router.get("/test", response_class=HTMLResponse)
async def test_route():
    """Test route without authentication"""
    return "<h1>Chemical Inventory Test Route Works!</h1>"

# Pydantic models for request validation
class ChemicalInventoryCreate(BaseModel):
    chemical_name: str
    cas_number: Optional[str] = None
    manufacturer: Optional[str] = None
    catalog_number: Optional[str] = None
    lot_number: Optional[str] = None
    container_size: Optional[str] = None
    current_quantity: float
    unit: str
    storage_location: Optional[str] = None
    storage_temperature: Optional[str] = None
    storage_conditions: Optional[str] = None
    hazard_class: Optional[str] = None
    safety_notes: Optional[str] = None
    received_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    opened_date: Optional[datetime] = None
    is_hazardous: bool = False

    @validator('current_quantity')
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Quantity must be positive')
        return v

class ChemicalInventoryUpdate(BaseModel):
    chemical_name: Optional[str] = None
    cas_number: Optional[str] = None
    manufacturer: Optional[str] = None
    catalog_number: Optional[str] = None
    lot_number: Optional[str] = None
    container_size: Optional[str] = None
    current_quantity: Optional[float] = None
    unit: Optional[str] = None
    storage_location: Optional[str] = None
    storage_temperature: Optional[str] = None
    storage_conditions: Optional[str] = None
    hazard_class: Optional[str] = None
    safety_notes: Optional[str] = None
    received_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    opened_date: Optional[datetime] = None
    is_hazardous: Optional[bool] = None
    is_active: Optional[bool] = None

class QuantityUpdate(BaseModel):
    quantity_change: float
    reason: str
    notes: Optional[str] = None

    @validator('quantity_change')
    def quantity_change_not_zero(cls, v):
        if v == 0:
            raise ValueError('Quantity change cannot be zero')
        return v

# HTML Routes
@router.get("/", response_class=HTMLResponse)
async def chemical_inventory_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """List all chemicals in inventory"""
    chemicals = db.query(ChemicalInventoryLog).filter(
        ChemicalInventoryLog.is_active == True
    ).order_by(ChemicalInventoryLog.chemical_name).all()
    
    context = {
        "request": request,
        "title": "Chemical Inventory - EHS Electronic Journal",
        "chemicals": chemicals,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("chemical_inventory/list.html", context)

@router.get("/add", response_class=HTMLResponse)
async def add_chemical_form(
    request: Request,
    current_user: User = Depends(require_permissions(["create"]))
):
    """Add new chemical form"""
    context = {
        "request": request,
        "title": "Add Chemical - EHS Electronic Journal",
        "current_user": current_user
    }
    
    return templates.TemplateResponse("chemical_inventory/add.html", context)

@router.get("/{chemical_id}", response_class=HTMLResponse)
async def chemical_detail(
    chemical_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """View chemical details and history"""
    chemical = db.query(ChemicalInventoryLog).filter(
        ChemicalInventoryLog.id == chemical_id
    ).first()
    
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    history = db.query(ChemicalInventoryHistory).filter(
        ChemicalInventoryHistory.chemical_id == chemical_id
    ).order_by(ChemicalInventoryHistory.changed_at.desc()).all()
    
    context = {
        "request": request,
        "title": f"{chemical.chemical_name} - Chemical Details",
        "chemical": chemical,
        "history": history,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("chemical_inventory/detail.html", context)

@router.get("/edit/{chemical_id}", response_class=HTMLResponse)
async def edit_chemical_form(
    chemical_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["update"]))
):
    """Edit chemical form"""
    chemical = db.query(ChemicalInventoryLog).filter(
        ChemicalInventoryLog.id == chemical_id
    ).first()
    
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    context = {
        "request": request,
        "title": f"Edit {chemical.chemical_name} - Chemical Inventory",
        "chemical": chemical,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("chemical_inventory/edit.html", context)

# API Routes
@router.post("/api/", response_model=dict)
async def create_chemical(
    chemical: ChemicalInventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["create"]))
):
    """Create a new chemical inventory entry"""
    
    # Create new chemical inventory entry
    db_chemical = ChemicalInventoryLog(
        **chemical.dict(),
        created_by=current_user.id
    )
    
    try:
        db.add(db_chemical)
        db.commit()
        db.refresh(db_chemical)
        
        # Create history entry
        history_entry = ChemicalInventoryHistory(
            chemical_id=db_chemical.id,
            action="created",
            new_value=f"Chemical {db_chemical.chemical_name} created",
            notes="Initial inventory entry",
            remaining_quantity=db_chemical.current_quantity,
            changed_by=current_user.id
        )
        
        db.add(history_entry)
        db.commit()
        
        return {
            "success": True,
            "message": "Chemical inventory entry created successfully",
            "chemical": db_chemical.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating chemical: {str(e)}"
        )

@router.put("/api/{chemical_id}", response_model=dict)
async def update_chemical(
    chemical_id: int,
    chemical_update: ChemicalInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["update"]))
):
    """Update chemical inventory entry"""
    
    db_chemical = db.query(ChemicalInventoryLog).filter(
        ChemicalInventoryLog.id == chemical_id
    ).first()
    
    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    # Track changes for history
    changes = []
    update_data = chemical_update.dict(exclude_unset=True)
    
    for field, new_value in update_data.items():
        old_value = getattr(db_chemical, field)
        if old_value != new_value:
            changes.append({
                "field": field,
                "old_value": str(old_value) if old_value else None,
                "new_value": str(new_value) if new_value else None
            })
            setattr(db_chemical, field, new_value)
    
    if not changes:
        return {
            "success": True,
            "message": "No changes detected",
            "chemical": db_chemical.to_dict()
        }
    
    try:
        db.commit()
        
        # Create history entries for each change
        for change in changes:
            history_entry = ChemicalInventoryHistory(
                chemical_id=chemical_id,
                action="updated",
                field_changed=change["field"],
                old_value=change["old_value"],
                new_value=change["new_value"],
                remaining_quantity=db_chemical.current_quantity,
                changed_by=current_user.id
            )
            db.add(history_entry)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Chemical updated successfully. {len(changes)} field(s) modified.",
            "chemical": db_chemical.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating chemical: {str(e)}"
        )

@router.patch("/api/{chemical_id}/quantity", response_model=dict)
async def update_quantity(
    chemical_id: int,
    quantity_update: QuantityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["update"]))
):
    """Update chemical quantity with usage tracking"""
    
    db_chemical = db.query(ChemicalInventoryLog).filter(
        ChemicalInventoryLog.id == chemical_id
    ).first()
    
    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    old_quantity = db_chemical.current_quantity
    new_quantity = old_quantity + quantity_update.quantity_change
    
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient quantity available"
        )
    
    try:
        db_chemical.current_quantity = new_quantity
        db.commit()
        
        # Create history entry for quantity change
        action = "quantity_added" if quantity_update.quantity_change > 0 else "quantity_used"
        history_entry = ChemicalInventoryHistory(
            chemical_id=chemical_id,
            action=action,
            field_changed="current_quantity",
            old_value=str(old_quantity),
            new_value=str(new_quantity),
            quantity_change=quantity_update.quantity_change,
            remaining_quantity=new_quantity,
            reason=quantity_update.reason,
            notes=quantity_update.notes,
            changed_by=current_user.id
        )
        
        db.add(history_entry)
        db.commit()
        
        return {
            "success": True,
            "message": f"Quantity updated: {quantity_update.quantity_change:+.3f} {db_chemical.unit}",
            "chemical": db_chemical.to_dict(),
            "old_quantity": float(old_quantity),
            "new_quantity": float(new_quantity)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating quantity: {str(e)}"
        )

@router.delete("/api/{chemical_id}", response_model=dict)
async def delete_chemical(
    chemical_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["delete"]))
):
    """Soft delete chemical (mark as inactive)"""
    
    db_chemical = db.query(ChemicalInventoryLog).filter(
        ChemicalInventoryLog.id == chemical_id
    ).first()
    
    if not db_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    try:
        db_chemical.is_active = False
        db.commit()
        
        # Create history entry
        history_entry = ChemicalInventoryHistory(
            chemical_id=chemical_id,
            action="deactivated",
            field_changed="is_active",
            old_value="True",
            new_value="False",
            notes="Chemical marked as inactive",
            remaining_quantity=db_chemical.current_quantity,
            changed_by=current_user.id
        )
        
        db.add(history_entry)
        db.commit()
        
        return {
            "success": True,
            "message": "Chemical marked as inactive"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deactivating chemical: {str(e)}"
        )

@router.get("/api/", response_model=List[dict])
async def list_chemicals(
    active_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """List all chemicals with optional filtering"""
    
    query = db.query(ChemicalInventoryLog)
    
    if active_only:
        query = query.filter(ChemicalInventoryLog.is_active == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            ChemicalInventoryLog.chemical_name.ilike(search_term) |
            ChemicalInventoryLog.cas_number.ilike(search_term) |
            ChemicalInventoryLog.manufacturer.ilike(search_term)
        )
    
    chemicals = query.order_by(ChemicalInventoryLog.chemical_name).all()
    
    return [chemical.to_dict() for chemical in chemicals]

@router.get("/api/{chemical_id}/history", response_model=List[dict])
async def get_chemical_history(
    chemical_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """Get history for a specific chemical"""
    
    # Verify chemical exists
    chemical = db.query(ChemicalInventoryLog).filter(
        ChemicalInventoryLog.id == chemical_id
    ).first()
    
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    history = db.query(ChemicalInventoryHistory).filter(
        ChemicalInventoryHistory.chemical_id == chemical_id
    ).order_by(ChemicalInventoryHistory.changed_at.desc()).all()
    
    return [entry.to_dict() for entry in history]