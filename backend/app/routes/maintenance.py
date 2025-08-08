"""
Maintenance routes - ICP-OES and other equipment maintenance
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from app.database import get_db
from app.models.maintenance import (
    ICPOESMaintenanceLog, ICPOESMaintenanceHistory,
    MaintenanceType, MaintenanceStatus
)
from app.models.user import User
from app.auth.jwt_handler import get_current_user, require_permissions

# Import templates
from pathlib import Path
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

# Pydantic models for ICP-OES Maintenance
class ICPOESMaintenanceCreate(BaseModel):
    maintenance_date: datetime
    maintenance_type: MaintenanceType
    instrument_id: str
    instrument_model: Optional[str] = None
    serial_number: Optional[str] = None
    maintenance_category: str  # Torch, Pump, Optics, etc.
    work_performed: str
    
    # Torch maintenance
    torch_condition: Optional[str] = None
    torch_hours: Optional[float] = None
    torch_replaced: bool = False
    new_torch_serial: Optional[str] = None
    
    # Pump maintenance
    pump_tubing_replaced: bool = False
    pump_flow_rate: Optional[float] = None
    pump_pressure: Optional[float] = None
    
    # Optics maintenance
    optics_cleaned: bool = False
    purge_gas_flow: Optional[float] = None
    optical_chamber_condition: Optional[str] = None
    
    # Nebulizer maintenance
    nebulizer_cleaned: bool = False
    nebulizer_type: Optional[str] = None
    uptake_rate: Optional[float] = None
    
    # Argon gas system
    argon_pressure: Optional[float] = None
    argon_flow_plasma: Optional[float] = None
    argon_flow_auxiliary: Optional[float] = None
    argon_flow_nebulizer: Optional[float] = None
    
    # Performance checks
    wavelength_calibration: bool = False
    intensity_check: bool = False
    background_check: bool = False
    stability_check: bool = False
    
    # Performance results
    detection_limits_acceptable: bool = True
    precision_acceptable: bool = True
    accuracy_acceptable: bool = True
    
    # Parts and costs
    parts_replaced: Optional[str] = None  # JSON list
    consumables_used: Optional[str] = None  # JSON list
    cost_estimate: Optional[float] = None
    
    # Issues and follow-up
    issues_found: Optional[str] = None
    resolutions: Optional[str] = None
    follow_up_required: bool = False
    next_maintenance_due: Optional[datetime] = None
    
    # Duration and effort
    maintenance_duration: Optional[float] = None  # hours
    technician_notes: Optional[str] = None

class ICPOESMaintenanceUpdate(BaseModel):
    maintenance_status: Optional[MaintenanceStatus] = None
    maintenance_category: Optional[str] = None
    work_performed: Optional[str] = None
    torch_condition: Optional[str] = None
    torch_hours: Optional[float] = None
    torch_replaced: Optional[bool] = None
    new_torch_serial: Optional[str] = None
    pump_tubing_replaced: Optional[bool] = None
    pump_flow_rate: Optional[float] = None
    pump_pressure: Optional[float] = None
    optics_cleaned: Optional[bool] = None
    purge_gas_flow: Optional[float] = None
    optical_chamber_condition: Optional[str] = None
    nebulizer_cleaned: Optional[bool] = None
    nebulizer_type: Optional[str] = None
    uptake_rate: Optional[float] = None
    argon_pressure: Optional[float] = None
    argon_flow_plasma: Optional[float] = None
    argon_flow_auxiliary: Optional[float] = None
    argon_flow_nebulizer: Optional[float] = None
    wavelength_calibration: Optional[bool] = None
    intensity_check: Optional[bool] = None
    background_check: Optional[bool] = None
    stability_check: Optional[bool] = None
    detection_limits_acceptable: Optional[bool] = None
    precision_acceptable: Optional[bool] = None
    accuracy_acceptable: Optional[bool] = None
    parts_replaced: Optional[str] = None
    consumables_used: Optional[str] = None
    cost_estimate: Optional[float] = None
    issues_found: Optional[str] = None
    resolutions: Optional[str] = None
    follow_up_required: Optional[bool] = None
    next_maintenance_due: Optional[datetime] = None
    maintenance_duration: Optional[float] = None
    technician_notes: Optional[str] = None

# ICP-OES Maintenance Routes
@router.get("/icp-oes", response_class=HTMLResponse)
async def icp_oes_maintenance_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """ICP-OES maintenance logs"""
    maintenance_logs = db.query(ICPOESMaintenanceLog).order_by(
        ICPOESMaintenanceLog.maintenance_date.desc()
    ).all()
    
    context = {
        "request": request,
        "title": "ICP-OES Maintenance Log - EHS Electronic Journal",
        "maintenance_logs": maintenance_logs,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("maintenance/icp_oes.html", context)

@router.get("/icp-oes/add", response_class=HTMLResponse)
async def add_icp_maintenance_form(
    request: Request,
    current_user: User = Depends(require_permissions(["create"]))
):
    """Add ICP-OES maintenance form"""
    context = {
        "request": request,
        "title": "Add ICP-OES Maintenance - EHS Electronic Journal",
        "current_user": current_user,
        "maintenance_types": [e.value for e in MaintenanceType],
        "maintenance_statuses": [e.value for e in MaintenanceStatus]
    }
    
    return templates.TemplateResponse("maintenance/add_icp_oes.html", context)

@router.post("/icp-oes/api/", response_model=dict)
async def create_icp_maintenance(
    maintenance: ICPOESMaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["create"]))
):
    """Create new ICP-OES maintenance log"""
    
    try:
        db_maintenance = ICPOESMaintenanceLog(
            **maintenance.dict(),
            maintenance_status=MaintenanceStatus.COMPLETED,
            performed_by=current_user.id
        )
        db.add(db_maintenance)
        db.commit()
        db.refresh(db_maintenance)
        
        # Create history entry
        history_entry = ICPOESMaintenanceHistory(
            maintenance_id=db_maintenance.id,
            action="created",
            new_value=f"ICP-OES maintenance performed on {db_maintenance.instrument_id}",
            notes="Initial maintenance log entry",
            changed_by=current_user.id
        )
        
        db.add(history_entry)
        db.commit()
        
        return {
            "success": True,
            "message": "ICP-OES maintenance log created successfully",
            "maintenance": db_maintenance.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating maintenance log: {str(e)}"
        )

@router.get("/icp-oes/api/", response_model=List[dict])
async def list_icp_maintenance(
    instrument_id: Optional[str] = None,
    maintenance_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """List ICP-OES maintenance logs"""
    
    query = db.query(ICPOESMaintenanceLog)
    if instrument_id:
        query = query.filter(ICPOESMaintenanceLog.instrument_id == instrument_id)
    if maintenance_type:
        query = query.filter(ICPOESMaintenanceLog.maintenance_type == maintenance_type)
    
    logs = query.order_by(ICPOESMaintenanceLog.maintenance_date.desc()).all()
    return [log.to_dict() for log in logs]

@router.get("/icp-oes/{maintenance_id}", response_class=HTMLResponse)
async def icp_maintenance_detail(
    maintenance_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """ICP-OES maintenance detail page"""
    
    maintenance = db.query(ICPOESMaintenanceLog).filter(
        ICPOESMaintenanceLog.id == maintenance_id
    ).first()
    
    if not maintenance:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    
    history = db.query(ICPOESMaintenanceHistory).filter(
        ICPOESMaintenanceHistory.maintenance_id == maintenance_id
    ).order_by(ICPOESMaintenanceHistory.changed_at.desc()).all()
    
    context = {
        "request": request,
        "title": f"ICP-OES Maintenance - {maintenance.maintenance_date.strftime('%Y-%m-%d')}",
        "maintenance": maintenance,
        "history": history,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("maintenance/icp_oes_detail.html", context)

@router.put("/icp-oes/api/{maintenance_id}", response_model=dict)
async def update_icp_maintenance(
    maintenance_id: int,
    maintenance_update: ICPOESMaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["update"]))
):
    """Update ICP-OES maintenance log"""
    
    db_maintenance = db.query(ICPOESMaintenanceLog).filter(
        ICPOESMaintenanceLog.id == maintenance_id
    ).first()
    
    if not db_maintenance:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    
    # Track changes for history
    changes = []
    update_data = maintenance_update.dict(exclude_unset=True)
    
    for field, new_value in update_data.items():
        old_value = getattr(db_maintenance, field)
        if old_value != new_value:
            changes.append({
                "field": field,
                "old_value": str(old_value) if old_value else None,
                "new_value": str(new_value) if new_value else None
            })
            setattr(db_maintenance, field, new_value)
    
    if not changes:
        return {
            "success": True,
            "message": "No changes detected",
            "maintenance": db_maintenance.to_dict()
        }
    
    try:
        db.commit()
        
        # Create history entries for each change
        for change in changes:
            history_entry = ICPOESMaintenanceHistory(
                maintenance_id=maintenance_id,
                action="updated",
                field_changed=change["field"],
                old_value=change["old_value"],
                new_value=change["new_value"],
                changed_by=current_user.id
            )
            db.add(history_entry)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Maintenance log updated successfully. {len(changes)} field(s) modified.",
            "maintenance": db_maintenance.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating maintenance log: {str(e)}"
        )

# General maintenance dashboard
@router.get("/", response_class=HTMLResponse)
async def maintenance_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """General maintenance dashboard"""
    
    # Get recent ICP-OES maintenance
    recent_icp_maintenance = db.query(ICPOESMaintenanceLog).order_by(
        ICPOESMaintenanceLog.maintenance_date.desc()
    ).limit(10).all()
    
    # Get upcoming maintenance (follow-up required)
    upcoming_maintenance = db.query(ICPOESMaintenanceLog).filter(
        ICPOESMaintenanceLog.follow_up_required == True
    ).order_by(ICPOESMaintenanceLog.next_maintenance_due).all()
    
    context = {
        "request": request,
        "title": "Maintenance Dashboard - EHS Electronic Journal",
        "recent_icp_maintenance": recent_icp_maintenance,
        "upcoming_maintenance": upcoming_maintenance,
        "current_user": current_user
    }
    
    return templates.TemplateResponse("maintenance/dashboard.html", context)

@router.get("/api/dashboard", response_model=dict)
async def maintenance_dashboard_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["read"]))
):
    """Get maintenance dashboard data"""
    
    # Recent maintenance
    recent_maintenance = db.query(ICPOESMaintenanceLog).order_by(
        ICPOESMaintenanceLog.maintenance_date.desc()
    ).limit(20).all()
    
    # Overdue maintenance
    overdue_maintenance = db.query(ICPOESMaintenanceLog).filter(
        ICPOESMaintenanceLog.follow_up_required == True,
        ICPOESMaintenanceLog.next_maintenance_due < datetime.utcnow()
    ).all()
    
    # Due soon (within 7 days)
    due_soon = db.query(ICPOESMaintenanceLog).filter(
        ICPOESMaintenanceLog.follow_up_required == True,
        ICPOESMaintenanceLog.next_maintenance_due >= datetime.utcnow(),
        ICPOESMaintenanceLog.next_maintenance_due <= datetime.utcnow() + timedelta(days=7)
    ).all()
    
    # Maintenance statistics
    total_maintenance = db.query(ICPOESMaintenanceLog).count()
    completed_this_month = db.query(ICPOESMaintenanceLog).filter(
        ICPOESMaintenanceLog.maintenance_date >= datetime.utcnow().replace(day=1),
        ICPOESMaintenanceLog.maintenance_status == MaintenanceStatus.COMPLETED
    ).count()
    
    return {
        "recent_maintenance": [m.to_dict() for m in recent_maintenance],
        "overdue_maintenance": [m.to_dict() for m in overdue_maintenance],
        "due_soon": [m.to_dict() for m in due_soon],
        "statistics": {
            "total_maintenance": total_maintenance,
            "completed_this_month": completed_this_month,
            "overdue_count": len(overdue_maintenance),
            "due_soon_count": len(due_soon)
        }
    }