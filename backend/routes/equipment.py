"""
Equipment routes - Equipment logs, pipettes, water conductivity
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from backend.database import get_db
from backend.models.equipment import Equipment, PipetteLog, WaterConductivityTests
from backend.models.user import User
from backend.auth.jwt_handler import get_current_user, require_permissions

# Import templates - use the same pattern as main.py
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="frontend/templates")

router = APIRouter(prefix="/equipment", tags=["Equipment"])

# Pydantic models for Equipment
class EquipmentCreate(BaseModel):
    equipment_name: str
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    equipment_type: str
    location: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiration: Optional[datetime] = None
    calibration_frequency: Optional[int] = None  # days
    service_provider: Optional[str] = None
    service_contact: Optional[str] = None
    notes: Optional[str] = None

class EquipmentUpdate(BaseModel):
    equipment_name: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    equipment_type: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiration: Optional[datetime] = None
    calibration_frequency: Optional[int] = None
    last_calibration: Optional[datetime] = None
    next_calibration_due: Optional[datetime] = None
    calibration_status: Optional[str] = None
    service_provider: Optional[str] = None
    service_contact: Optional[str] = None
    last_service_date: Optional[datetime] = None
    next_service_due: Optional[datetime] = None
    is_in_service: Optional[bool] = None
    notes: Optional[str] = None

# Pydantic models for Pipette Log
class PipetteLogCreate(BaseModel):
    pipette_id: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    volume_range_min: Optional[float] = None
    volume_range_max: Optional[float] = None
    test_date: datetime
    test_volume: float
    target_volume: float
    actual_volume: float
    accuracy_percent: Optional[float] = None
    precision_cv: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    test_standard: Optional[str] = None
    calibration_status: str = "Pass"
    technician_notes: Optional[str] = None

    @validator('test_volume', 'target_volume', 'actual_volume')
    def volumes_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Volume must be positive')
        return v

class PipetteLogUpdate(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    volume_range_min: Optional[float] = None
    volume_range_max: Optional[float] = None
    accuracy_percent: Optional[float] = None
    precision_cv: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    test_standard: Optional[str] = None
    calibration_status: Optional[str] = None
    technician_notes: Optional[str] = None
    is_active: Optional[bool] = None

# Pydantic models for Water Conductivity Tests
class WaterConductivityCreate(BaseModel):
    test_date: datetime
    sample_source: str
    conductivity_reading: float  # μS/cm
    temperature: Optional[float] = None
    test_method: Optional[str] = None
    instrument_used: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    result_status: str = "Pass"
    notes: Optional[str] = None

    @validator('conductivity_reading')
    def conductivity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Conductivity must be non-negative')
        return v

class WaterConductivityUpdate(BaseModel):
    sample_source: Optional[str] = None
    conductivity_reading: Optional[float] = None
    temperature: Optional[float] = None
    test_method: Optional[str] = None
    instrument_used: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    result_status: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

# Equipment Routes
@router.get("/", response_class=HTMLResponse)
async def equipment_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """Equipment list page"""
    equipment = db.query(Equipment).filter(
        Equipment.is_active == True
    ).order_by(Equipment.equipment_name).all()
    
    context = {
        "request": request,
        "title": "Equipment Management - EHS Electronic Journal",
        "equipment": equipment,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("equipment/list.html", context)

@router.get("/add", response_class=HTMLResponse)
async def add_equipment_form(
    request: Request,
    current_user: User = Depends(require_permissions(["create"]))
):
    """Add equipment form"""
    context = {
        "request": request,
        "title": "Add Equipment - EHS Electronic Journal",
        "current_user": current_user
    }
    
    return templates.TemplateResponse("equipment/add.html", context)

@router.post("/api/", response_model=dict)
async def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["create"]))
):
    """Create new equipment entry"""
    
    try:
        # Calculate next calibration due date if calibration frequency is provided
        equipment_data = equipment.dict()
        if equipment.calibration_frequency:
            equipment_data['next_calibration_due'] = datetime.utcnow() + timedelta(days=equipment.calibration_frequency)
            equipment_data['calibration_status'] = 'due_soon'
        
        db_equipment = Equipment(**equipment_data, responsible_user=current_user.id)
        db.add(db_equipment)
        db.commit()
        db.refresh(db_equipment)
        
        return {
            "success": True,
            "message": "Equipment created successfully",
            "equipment": db_equipment.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating equipment: {str(e)}"
        )

@router.get("/api/", response_model=List[dict])
async def list_equipment(
    active_only: bool = True,
    equipment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """List all equipment"""
    
    query = db.query(Equipment)
    if active_only:
        query = query.filter(Equipment.is_active == True)
    if equipment_type:
        query = query.filter(Equipment.equipment_type == equipment_type)
    
    equipment = query.order_by(Equipment.equipment_name).all()
    return [item.to_dict() for item in equipment]

@router.get("/{equipment_id}", response_class=HTMLResponse)
async def equipment_detail(
    equipment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """Equipment detail page"""
    
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    context = {
        "request": request,
        "title": f"{equipment.equipment_name} - Equipment Details",
        "equipment": equipment,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("equipment/detail.html", context)

@router.put("/api/{equipment_id}", response_model=dict)
async def update_equipment(
    equipment_id: int,
    equipment_update: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["update"]))
):
    """Update equipment"""
    
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Update fields
    update_data = equipment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_equipment, field, value)
    
    # Recalculate calibration status if calibration date changed
    if 'last_calibration' in update_data and db_equipment.calibration_frequency:
        next_due = db_equipment.last_calibration + timedelta(days=db_equipment.calibration_frequency)
        db_equipment.next_calibration_due = next_due
        
        # Update status based on due date
        days_until_due = (next_due.date() - datetime.utcnow().date()).days
        if days_until_due < 0:
            db_equipment.calibration_status = "overdue"
        elif days_until_due <= 7:
            db_equipment.calibration_status = "due_soon"
        else:
            db_equipment.calibration_status = "current"
    
    try:
        db.commit()
        
        return {
            "success": True,
            "message": "Equipment updated successfully",
            "equipment": db_equipment.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating equipment: {str(e)}"
        )

# Pipette Log Routes
@router.get("/pipettes", response_class=HTMLResponse)
async def pipette_log_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """Pipette calibration logs"""
    pipette_logs = db.query(PipetteLog).filter(
        PipetteLog.is_active == True
    ).order_by(PipetteLog.calibration_date.desc()).all()
    
    context = {
        "request": request,
        "title": "Pipette Calibration Log - EHS Electronic Journal",
        "pipette_logs": pipette_logs,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("equipment/pipettes.html", context)

@router.post("/pipettes/api/", response_model=dict)
async def create_pipette_log(
    pipette_log: PipetteLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["create"]))
):
    """Create new pipette calibration log"""
    
    try:
        # Calculate accuracy percentage if not provided
        pipette_data = pipette_log.dict()
        if not pipette_data.get('accuracy_percent'):
            accuracy = ((pipette_log.actual_volume / pipette_log.target_volume) - 1) * 100
            pipette_data['accuracy_percent'] = round(accuracy, 2)
        
        db_pipette = PipetteLog(**pipette_data, tested_by=current_user.id)
        db.add(db_pipette)
        db.commit()
        db.refresh(db_pipette)
        
        return {
            "success": True,
            "message": "Pipette calibration log created successfully",
            "pipette_log": db_pipette.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating pipette log: {str(e)}"
        )

@router.get("/pipettes/api/", response_model=List[dict])
async def list_pipette_logs(
    pipette_id: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """List pipette calibration logs"""
    
    query = db.query(PipetteLog)
    if active_only:
        query = query.filter(PipetteLog.is_active == True)
    if pipette_id:
        query = query.filter(PipetteLog.pipette_id == pipette_id)
    
    logs = query.order_by(PipetteLog.calibration_date.desc()).all()
    return [log.to_dict() for log in logs]

# Water Conductivity Routes
@router.get("/water-conductivity", response_class=HTMLResponse)
async def water_conductivity_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """Water conductivity tests"""
    tests = db.query(WaterConductivityTests).filter(
        WaterConductivityTests.is_active == True
    ).order_by(WaterConductivityTests.test_date.desc()).all()
    
    context = {
        "request": request,
        "title": "Water Conductivity Tests - EHS Electronic Journal",
        "tests": tests,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("equipment/water_conductivity.html", context)

@router.post("/water-conductivity/api/", response_model=dict)
async def create_water_conductivity_test(
    test: WaterConductivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["create"]))
):
    """Create new water conductivity test"""
    
    try:
        db_test = WaterConductivityTests(**test.dict(), tested_by=current_user.id)
        db.add(db_test)
        db.commit()
        db.refresh(db_test)
        
        return {
            "success": True,
            "message": "Water conductivity test recorded successfully",
            "test": db_test.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating test: {str(e)}"
        )

@router.get("/water-conductivity/api/", response_model=List[dict])
async def list_water_conductivity_tests(
    source: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """List water conductivity tests"""
    
    query = db.query(WaterConductivityTests)
    if active_only:
        query = query.filter(WaterConductivityTests.is_active == True)
    if source:
        query = query.filter(WaterConductivityTests.sample_source.ilike(f"%{source}%"))
    
    tests = query.order_by(WaterConductivityTests.test_date.desc()).all()
    return [test.to_dict() for test in tests]

# Generic equipment API
@router.get("/api/", response_model=dict)
async def list_all_equipment_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """Get all equipment-related data"""
    
    equipment = db.query(Equipment).filter(Equipment.is_active == True).all()
    pipette_logs = db.query(PipetteLog).filter(PipetteLog.is_active == True).limit(20).all()
    water_tests = db.query(WaterConductivityTests).filter(WaterConductivityTests.is_active == True).limit(20).all()
    
    return {
        "equipment": [item.to_dict() for item in equipment],
        "recent_pipette_logs": [log.to_dict() for log in pipette_logs],
        "recent_water_tests": [test.to_dict() for test in water_tests]
    }