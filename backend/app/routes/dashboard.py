"""
Dashboard routes
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.database import get_db
from app.auth.jwt_handler import get_optional_user
from app.models.chemical_inventory import ChemicalInventoryLog, ChemicalInventoryHistory
from app.models.reagents import MMReagents, PbReagents, TCLPReagents
from app.models.standards import MMStandards, FlameAAStandards  
from app.models.equipment import Equipment, PipetteLog, WaterConductivityTests
from app.models.maintenance import ICPOESMaintenanceLog, MaintenanceStatus

# Import templates from main.py setup
from pathlib import Path
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "frontend" / "templates"))

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Main dashboard page with comprehensive overview"""
    current_user = await get_optional_user(request, db)
    
    # Get dashboard statistics
    stats = await get_dashboard_statistics(db)
    recent_activity = await get_recent_activity(db)
    alerts = await get_system_alerts(db)
    
    context = {
        "request": request,
        "title": "Dashboard - EHS Electronic Journal",
        "current_user": current_user,
        "stats": stats,
        "recent_activity": recent_activity,
        "alerts": alerts,
        "current_time_est": datetime.now().strftime("%m/%d/%Y %I:%M %p")
    }
    
    return templates.TemplateResponse("dashboard/overview.html", context)

@router.get("/api/stats", response_model=dict)
async def dashboard_api_stats(
    db: Session = Depends(get_db)
):
    """API endpoint for dashboard statistics"""
    return await get_dashboard_statistics(db)

@router.get("/api/activity", response_model=dict) 
async def dashboard_api_activity(
    db: Session = Depends(get_db)
):
    """API endpoint for recent activity"""
    return await get_recent_activity(db)

@router.get("/api/alerts", response_model=dict)
async def dashboard_api_alerts(
    db: Session = Depends(get_db)
):
    """API endpoint for system alerts"""
    return await get_system_alerts(db)

async def get_dashboard_statistics(db: Session) -> dict:
    """Get comprehensive dashboard statistics"""
    
    # Chemical Inventory Stats
    total_chemicals = db.query(ChemicalInventoryLog).filter(ChemicalInventoryLog.is_active == True).count()
    low_stock_chemicals = db.query(ChemicalInventoryLog).filter(
        and_(
            ChemicalInventoryLog.is_active == True,
            ChemicalInventoryLog.current_quantity < 10
        )
    ).count()
    
    expired_chemicals = db.query(ChemicalInventoryLog).filter(
        and_(
            ChemicalInventoryLog.is_active == True,
            ChemicalInventoryLog.expiration_date < datetime.now()
        )
    ).count()
    
    # Reagents Stats
    active_mm_reagents = db.query(MMReagents).filter(MMReagents.is_active == True).count()
    active_pb_reagents = db.query(PbReagents).filter(PbReagents.is_active == True).count()
    active_tclp_reagents = db.query(TCLPReagents).filter(TCLPReagents.is_active == True).count()
    
    # Standards Stats
    active_mm_standards = db.query(MMStandards).filter(MMStandards.is_active == True).count()
    active_flameaa_standards = db.query(FlameAAStandards).filter(FlameAAStandards.is_active == True).count()
    
    # Equipment Stats
    total_equipment = db.query(Equipment).filter(Equipment.is_active == True).count()
    overdue_calibrations = db.query(Equipment).filter(
        and_(
            Equipment.is_active == True,
            Equipment.next_calibration_due < datetime.now()
        )
    ).count()
    
    # Recent activity counts (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    
    recent_chemical_history = db.query(ChemicalInventoryHistory).filter(
        ChemicalInventoryHistory.changed_at >= week_ago
    ).count()
    
    recent_maintenance = db.query(ICPOESMaintenanceLog).filter(
        ICPOESMaintenanceLog.maintenance_date >= week_ago
    ).count()
    
    recent_pipette_tests = db.query(PipetteLog).filter(
        PipetteLog.calibration_date >= week_ago
    ).count()
    
    recent_water_tests = db.query(WaterConductivityTests).filter(
        WaterConductivityTests.test_date >= week_ago
    ).count()
    
    return {
        "chemical_inventory": {
            "total": total_chemicals,
            "low_stock": low_stock_chemicals,
            "expired": expired_chemicals,
            "recent_activity": recent_chemical_history
        },
        "reagents": {
            "mm_active": active_mm_reagents,
            "pb_active": active_pb_reagents,
            "tclp_active": active_tclp_reagents,
            "total_active": active_mm_reagents + active_pb_reagents + active_tclp_reagents
        },
        "standards": {
            "mm_active": active_mm_standards,
            "flameaa_active": active_flameaa_standards,
            "total_active": active_mm_standards + active_flameaa_standards
        },
        "equipment": {
            "total": total_equipment,
            "overdue_calibrations": overdue_calibrations,
            "recent_pipette_tests": recent_pipette_tests,
            "recent_water_tests": recent_water_tests
        },
        "maintenance": {
            "recent_activities": recent_maintenance
        }
    }

async def get_recent_activity(db: Session, limit: int = 15) -> dict:
    """Get recent activity across all modules"""
    
    # Recent chemical inventory changes
    chemical_history = db.query(ChemicalInventoryHistory).join(
        ChemicalInventoryLog
    ).order_by(ChemicalInventoryHistory.changed_at.desc()).limit(limit).all()
    
    # Recent maintenance
    maintenance_logs = db.query(ICPOESMaintenanceLog).order_by(
        ICPOESMaintenanceLog.maintenance_date.desc()
    ).limit(limit).all()
    
    # Recent equipment tests
    pipette_tests = db.query(PipetteLog).order_by(
        PipetteLog.calibration_date.desc()
    ).limit(10).all()
    
    water_tests = db.query(WaterConductivityTests).order_by(
        WaterConductivityTests.test_date.desc()
    ).limit(10).all()
    
    # Format activity feed
    activities = []
    
    # Add chemical activities
    for history in chemical_history:
        activities.append({
            "type": "chemical_inventory",
            "action": history.action,
            "description": f"Chemical inventory: {history.action}",
            "details": history.notes or f"Changed {history.field_changed}",
            "timestamp": history.changed_at,
            "user_id": history.changed_by,
            "icon": "fas fa-flask"
        })
    
    # Add maintenance activities
    for maintenance in maintenance_logs:
        activities.append({
            "type": "maintenance",
            "action": "maintenance_performed",
            "description": f"ICP-OES maintenance: {maintenance.maintenance_category}",
            "details": maintenance.work_performed[:100] + "..." if len(maintenance.work_performed) > 100 else maintenance.work_performed,
            "timestamp": maintenance.maintenance_date,
            "user_id": maintenance.performed_by,
            "icon": "fas fa-wrench"
        })
    
    # Add equipment test activities
    for test in pipette_tests:
        activities.append({
            "type": "equipment",
            "action": "pipette_test",
            "description": f"Pipette calibration: {test.pipette_id}",
            "details": f"Status: {test.calibration_status}",
            "timestamp": test.calibration_date,
            "user_id": test.tested_by,
            "icon": "fas fa-tools"
        })
    
    for test in water_tests:
        activities.append({
            "type": "equipment", 
            "action": "water_test",
            "description": f"Water conductivity test: {test.sample_source}",
            "details": f"{test.conductivity_reading:.2f} μS/cm - {test.result_status}",
            "timestamp": test.test_date,
            "user_id": test.tested_by,
            "icon": "fas fa-tint"
        })
    
    # Sort by timestamp and limit
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "activities": activities[:limit]
    }

async def get_system_alerts(db: Session) -> dict:
    """Get system alerts and notifications"""
    
    alerts = []
    
    # Expired chemicals
    expired_chemicals = db.query(ChemicalInventoryLog).filter(
        and_(
            ChemicalInventoryLog.is_active == True,
            ChemicalInventoryLog.expiration_date < datetime.now()
        )
    ).all()
    
    for chemical in expired_chemicals:
        alerts.append({
            "type": "danger",
            "category": "expiration",
            "title": "Expired Chemical",
            "message": f"{chemical.chemical_name} has expired",
            "details": f"Expired on {chemical.expiration_date.strftime('%m/%d/%Y')}",
            "action_url": f"/chemical_inventory/{chemical.id}",
            "icon": "fas fa-exclamation-triangle"
        })
    
    # Chemicals expiring soon (within 30 days)
    soon_expire = datetime.now() + timedelta(days=30)
    expiring_chemicals = db.query(ChemicalInventoryLog).filter(
        and_(
            ChemicalInventoryLog.is_active == True,
            ChemicalInventoryLog.expiration_date.between(datetime.now(), soon_expire)
        )
    ).all()
    
    for chemical in expiring_chemicals:
        days_until = (chemical.expiration_date - datetime.now()).days
        alerts.append({
            "type": "warning",
            "category": "expiration_warning", 
            "title": "Chemical Expiring Soon",
            "message": f"{chemical.chemical_name} expires in {days_until} days",
            "details": f"Expires on {chemical.expiration_date.strftime('%m/%d/%Y')}",
            "action_url": f"/chemical_inventory/{chemical.id}",
            "icon": "fas fa-clock"
        })
    
    # Low stock chemicals
    low_stock = db.query(ChemicalInventoryLog).filter(
        and_(
            ChemicalInventoryLog.is_active == True,
            ChemicalInventoryLog.current_quantity < 10
        )
    ).all()
    
    for chemical in low_stock:
        alerts.append({
            "type": "info",
            "category": "low_stock",
            "title": "Low Stock Alert",
            "message": f"{chemical.chemical_name} is running low",
            "details": f"Current stock: {chemical.current_quantity} {chemical.unit}",
            "action_url": f"/chemical_inventory/{chemical.id}",
            "icon": "fas fa-arrow-down"
        })
    
    # Overdue equipment calibrations
    overdue_equipment = db.query(Equipment).filter(
        and_(
            Equipment.is_active == True,
            Equipment.next_calibration_due < datetime.now()
        )
    ).all()
    
    for equipment in overdue_equipment:
        days_overdue = (datetime.now() - equipment.next_calibration_due).days
        alerts.append({
            "type": "danger",
            "category": "calibration_overdue",
            "title": "Calibration Overdue",
            "message": f"{equipment.equipment_name} calibration is overdue",
            "details": f"Overdue by {days_overdue} days",
            "action_url": f"/equipment/{equipment.id}",
            "icon": "fas fa-calendar-times"
        })
    
    # Sort alerts by priority (danger > warning > info)
    priority_order = {"danger": 1, "warning": 2, "info": 3}
    alerts.sort(key=lambda x: (priority_order.get(x["type"], 4), x["message"]))
    
    return {
        "alerts": alerts,
        "summary": {
            "total": len(alerts),
            "danger": len([a for a in alerts if a["type"] == "danger"]),
            "warning": len([a for a in alerts if a["type"] == "warning"]), 
            "info": len([a for a in alerts if a["type"] == "info"])
        }
    }