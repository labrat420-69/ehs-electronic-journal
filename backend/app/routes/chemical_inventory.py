"""
Chemical inventory routes with full CRUD operations
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.chemical_inventory import ChemicalInventoryLog, ChemicalInventoryHistory
from app.models.user import User
from app.auth.jwt_handler import get_current_user, get_optional_user
from app.utils.timezone_utils import get_est_time

# Import templates
from pathlib import Path
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

router = APIRouter()

# Pydantic models for API
class ChemicalInventoryCreate(BaseModel):
    chemical_name: str
    cas_number: Optional[str] = None
    manufacturer: Optional[str] = None
    catalog_number: Optional[str] = None
    lot_number: Optional[str] = None
    container_size: Optional[str] = None
    current_quantity: float = 0
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

class QuantityUpdateRequest(BaseModel):
    quantity_change: float
    reason: Optional[str] = None
    notes: Optional[str] = None

def log_chemical_history(
    db: Session,
    chemical_id: int,
    action: str,
    user_id: int,
    field_changed: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    quantity_change: Optional[float] = None,
    remaining_quantity: Optional[float] = None,
    notes: Optional[str] = None,
    reason: Optional[str] = None
):
    """Helper function to log chemical inventory changes"""
    history_entry = ChemicalInventoryHistory(
        chemical_id=chemical_id,
        action=action,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value,
        quantity_change=quantity_change,
        remaining_quantity=remaining_quantity,
        notes=notes,
        reason=reason,
        changed_by=user_id
    )
    db.add(history_entry)
    db.commit()

@router.get("/", response_class=HTMLResponse)
async def chemical_inventory_list(
    request: Request,
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search chemicals by name or CAS number"),
    show_inactive: bool = Query(False, description="Include inactive chemicals"),
    hazardous_only: bool = Query(False, description="Show only hazardous chemicals")
):
    """List all chemicals in inventory with search and filtering"""
    current_user = await get_optional_user(request, db)
    
    # Build query with filters
    query = db.query(ChemicalInventoryLog)
    
    if not show_inactive:
        query = query.filter(ChemicalInventoryLog.is_active == True)
    
    if hazardous_only:
        query = query.filter(ChemicalInventoryLog.is_hazardous == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            ChemicalInventoryLog.chemical_name.ilike(search_term) |
            ChemicalInventoryLog.cas_number.ilike(search_term)
        )
    
    chemicals = query.order_by(ChemicalInventoryLog.chemical_name).all()
    
    # Calculate statistics
    total_chemicals = len(chemicals)
    hazardous_count = sum(1 for c in chemicals if c.is_hazardous)
    expiring_soon = []
    
    # Check for chemicals expiring within 30 days
    if chemicals:
        now = datetime.now()
        for chemical in chemicals:
            if chemical.expiration_date:
                days_to_expiry = (chemical.expiration_date - now).days
                if 0 <= days_to_expiry <= 30:
                    expiring_soon.append({
                        'chemical': chemical,
                        'days_remaining': days_to_expiry
                    })
    
    context = {
        "request": request,
        "title": "Chemical Inventory - EHS Electronic Journal",
        "current_user": current_user,
        "chemicals": chemicals,
        "total_chemicals": total_chemicals,
        "hazardous_count": hazardous_count,
        "expiring_count": len(expiring_soon),
        "expiring_soon": expiring_soon,
        "search": search or "",
        "show_inactive": show_inactive,
        "hazardous_only": hazardous_only,
        "current_time_est": get_est_time().strftime("%m/%d/%Y, %I:%M:%S %p")
    }
    
    return templates.TemplateResponse("chemical_inventory/list.html", context)

@router.get("/add", response_class=HTMLResponse)
async def add_chemical_form(
    request: Request,
    db: Session = Depends(get_db)
):
    """Display form to add new chemical to inventory"""
    current_user = await get_optional_user(request, db)
    
    context = {
        "request": request,
        "title": "Add Chemical - EHS Electronic Journal",
        "current_user": current_user,
        "current_time_est": get_est_time().strftime("%m/%d/%Y, %I:%M:%S %p")
    }
    
    return templates.TemplateResponse("chemical_inventory/add.html", context)

@router.post("/add")
async def add_chemical(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add new chemical to inventory"""
    form_data = await request.form()
    
    try:
        # Parse form data
        chemical_data = ChemicalInventoryCreate(
            chemical_name=form_data.get("chemical_name"),
            cas_number=form_data.get("cas_number") or None,
            manufacturer=form_data.get("manufacturer") or None,
            catalog_number=form_data.get("catalog_number") or None,
            lot_number=form_data.get("lot_number") or None,
            container_size=form_data.get("container_size") or None,
            current_quantity=float(form_data.get("current_quantity", 0)),
            unit=form_data.get("unit"),
            storage_location=form_data.get("storage_location") or None,
            storage_temperature=form_data.get("storage_temperature") or None,
            storage_conditions=form_data.get("storage_conditions") or None,
            hazard_class=form_data.get("hazard_class") or None,
            safety_notes=form_data.get("safety_notes") or None,
            received_date=datetime.strptime(form_data.get("received_date"), "%Y-%m-%d") if form_data.get("received_date") else None,
            expiration_date=datetime.strptime(form_data.get("expiration_date"), "%Y-%m-%d") if form_data.get("expiration_date") else None,
            opened_date=datetime.strptime(form_data.get("opened_date"), "%Y-%m-%d") if form_data.get("opened_date") else None,
            is_hazardous=bool(form_data.get("is_hazardous"))
        )
        
        # Create new chemical inventory entry
        chemical = ChemicalInventoryLog(
            **chemical_data.dict(),
            created_by=current_user.id
        )
        
        db.add(chemical)
        db.commit()
        db.refresh(chemical)
        
        # Log the creation
        log_chemical_history(
            db=db,
            chemical_id=chemical.id,
            action="created",
            user_id=current_user.id,
            notes=f"Chemical {chemical.chemical_name} added to inventory",
            remaining_quantity=chemical.current_quantity
        )
        
        # Return success response
        return JSONResponse(
            content={"success": True, "message": f"Chemical {chemical.chemical_name} added successfully", "chemical_id": chemical.id},
            status_code=201
        )
        
    except ValueError as e:
        return JSONResponse(
            content={"success": False, "message": f"Invalid data: {str(e)}"},
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Error adding chemical: {str(e)}"},
            status_code=500
        )

@router.get("/history")
async def chemical_history(
    request: Request,
    db: Session = Depends(get_db),
    chemical_id: Optional[int] = Query(None, description="Filter by specific chemical ID"),
    limit: int = Query(100, description="Number of history entries to return")
):
    """View chemical inventory history with optional filtering"""
    current_user = await get_optional_user(request, db)
    
    # Build query
    query = db.query(ChemicalInventoryHistory)
    
    if chemical_id:
        query = query.filter(ChemicalInventoryHistory.chemical_id == chemical_id)
        
    history_entries = query.order_by(ChemicalInventoryHistory.changed_at.desc()).limit(limit).all()
    
    context = {
        "request": request,
        "title": "Chemical History - EHS Electronic Journal", 
        "current_user": current_user,
        "history_entries": history_entries,
        "chemical_id": chemical_id,
        "current_time_est": get_est_time().strftime("%m/%d/%Y, %I:%M:%S %p")
    }
    
    return templates.TemplateResponse("chemical_inventory/history.html", context)

@router.get("/{chemical_id}")
async def get_chemical(
    chemical_id: int,
    db: Session = Depends(get_db)
):
    """Get specific chemical details (API endpoint)"""
    chemical = db.query(ChemicalInventoryLog).filter(ChemicalInventoryLog.id == chemical_id).first()
    
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    return JSONResponse(content=chemical.to_dict())

@router.put("/{chemical_id}")
async def update_chemical(
    chemical_id: int,
    chemical_update: ChemicalInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update chemical information"""
    chemical = db.query(ChemicalInventoryLog).filter(ChemicalInventoryLog.id == chemical_id).first()
    
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    # Track changes for history
    changes = []
    update_data = chemical_update.dict(exclude_unset=True)
    
    for field, new_value in update_data.items():
        old_value = getattr(chemical, field)
        if old_value != new_value:
            changes.append({
                "field": field,
                "old_value": str(old_value) if old_value is not None else None,
                "new_value": str(new_value) if new_value is not None else None
            })
            setattr(chemical, field, new_value)
    
    if changes:
        db.commit()
        db.refresh(chemical)
        
        # Log all changes
        for change in changes:
            log_chemical_history(
                db=db,
                chemical_id=chemical.id,
                action="updated",
                user_id=current_user.id,
                field_changed=change["field"],
                old_value=change["old_value"],
                new_value=change["new_value"],
                remaining_quantity=chemical.current_quantity
            )
        
        return JSONResponse(content={"success": True, "message": "Chemical updated successfully"})
    
    return JSONResponse(content={"success": True, "message": "No changes detected"})

@router.post("/{chemical_id}/quantity")
async def update_quantity(
    chemical_id: int,
    quantity_update: QuantityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update chemical quantity (usage or addition)"""
    chemical = db.query(ChemicalInventoryLog).filter(ChemicalInventoryLog.id == chemical_id).first()
    
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    old_quantity = chemical.current_quantity
    new_quantity = old_quantity + quantity_update.quantity_change
    
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Insufficient quantity available")
    
    chemical.current_quantity = new_quantity
    db.commit()
    db.refresh(chemical)
    
    # Log quantity change
    log_chemical_history(
        db=db,
        chemical_id=chemical.id,
        action="quantity_changed",
        user_id=current_user.id,
        quantity_change=quantity_update.quantity_change,
        remaining_quantity=new_quantity,
        notes=quantity_update.notes,
        reason=quantity_update.reason
    )
    
    return JSONResponse(content={
        "success": True,
        "message": f"Quantity updated: {old_quantity} → {new_quantity} {chemical.unit}",
        "old_quantity": float(old_quantity),
        "new_quantity": float(new_quantity),
        "change": quantity_update.quantity_change
    })

@router.delete("/{chemical_id}")
async def deactivate_chemical(
    chemical_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate (soft delete) a chemical entry"""
    chemical = db.query(ChemicalInventoryLog).filter(ChemicalInventoryLog.id == chemical_id).first()
    
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")
    
    chemical.is_active = False
    db.commit()
    
    # Log deactivation
    log_chemical_history(
        db=db,
        chemical_id=chemical.id,
        action="deactivated",
        user_id=current_user.id,
        notes="Chemical entry deactivated",
        remaining_quantity=chemical.current_quantity
    )
    
    return JSONResponse(content={"success": True, "message": f"Chemical {chemical.chemical_name} deactivated successfully"})