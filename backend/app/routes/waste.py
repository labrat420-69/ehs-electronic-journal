"""
Waste disposal routes for COC tracking and waste box management
"""

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Optional
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import qrcode

from app.database import get_db
from app.auth.jwt_handler import get_optional_user
from app.models.analytics import WasteBox, WasteItem
from pydantic import BaseModel

router = APIRouter(prefix="/waste", tags=["waste"])

# Pydantic models
class WasteBoxCreate(BaseModel):
    box_id: str
    coc_job_id: Optional[str] = None
    box_type: str
    size: str
    location: str

class WasteItemCreate(BaseModel):
    item_name: str
    description: Optional[str] = None
    waste_type: str
    quantity: Optional[str] = None
    coc_job_id: Optional[str] = None
    sample_id: Optional[str] = None
    is_extra_sample: bool = False
    waste_box_id: int

@router.get("/", response_class=HTMLResponse)
async def waste_management_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """Waste disposal management dashboard"""
    current_user = await get_optional_user(request, db)
    
    # Get active waste boxes
    active_boxes = db.query(WasteBox).filter(
        WasteBox.status.in_(["active", "full"])
    ).order_by(desc(WasteBox.created_date)).all()
    
    # Get recent waste items
    recent_items = db.query(WasteItem).join(WasteBox).order_by(
        desc(WasteItem.added_date)
    ).limit(10).all()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🗑️ Waste Disposal Management - EHS Electronic Journal</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f8f9fa, #e9ecef); min-height: 100vh; }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
            
            .header {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
            .logo {{ font-size: 32px; font-weight: bold; color: #ea4335; margin-bottom: 10px; }}
            .subtitle {{ color: #666; font-size: 18px; }}
            
            .action-bar {{ background: white; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .action-buttons {{ display: flex; gap: 15px; flex-wrap: wrap; }}
            .btn {{ padding: 12px 24px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; text-decoration: none; }}
            .btn-primary {{ background: linear-gradient(135deg, #1a73e8, #4285f4); color: white; }}
            .btn-success {{ background: linear-gradient(135deg, #34a853, #66bb6a); color: white; }}
            .btn-warning {{ background: linear-gradient(135deg, #fbbc04, #ffc107); color: #333; }}
            .btn-danger {{ background: linear-gradient(135deg, #ea4335, #f44336); color: white; }}
            .btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
            
            .dashboard-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 25px; }}
            
            .waste-boxes {{ background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .section-title {{ font-size: 20px; font-weight: 600; color: #202124; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #e8eaed; }}
            
            .box-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
            .box-card {{ background: #f8f9fa; border: 2px solid #e8eaed; border-radius: 10px; padding: 20px; transition: all 0.2s; position: relative; }}
            .box-card:hover {{ border-color: #1a73e8; transform: translateY(-2px); }}
            
            .box-header {{ display: flex; justify-content: between; align-items: flex-start; margin-bottom: 15px; }}
            .box-id {{ font-size: 18px; font-weight: 600; color: #202124; }}
            .box-status {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
            .status-active {{ background: #e8f5e8; color: #2d5d2d; }}
            .status-full {{ background: #fff3cd; color: #856404; }}
            .status-disposed {{ background: #d1ecf1; color: #0c5460; }}
            
            .box-details {{ margin-bottom: 15px; color: #5f6368; font-size: 14px; }}
            .box-progress {{ margin-bottom: 15px; }}
            .progress-bar {{ width: 100%; height: 8px; background: #e8eaed; border-radius: 4px; overflow: hidden; }}
            .progress-fill {{ height: 100%; background: linear-gradient(90deg, #34a853, #66bb6a); transition: width 0.3s; }}
            
            .box-actions {{ display: flex; gap: 8px; }}
            .btn-sm {{ padding: 6px 12px; font-size: 12px; }}
            
            .recent-items {{ background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .item-list {{ max-height: 600px; overflow-y: auto; }}
            .item-card {{ background: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 12px; border-left: 4px solid #1a73e8; }}
            .item-card.hazardous {{ border-left-color: #ea4335; }}
            .item-name {{ font-weight: 600; color: #202124; margin-bottom: 5px; }}
            .item-details {{ color: #5f6368; font-size: 13px; }}
            
            .quick-actions {{ background: white; border-radius: 12px; padding: 25px; margin-top: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .quick-actions-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
            .quick-action {{ background: #f8f9fa; border: 2px solid #e8eaed; border-radius: 8px; padding: 20px; text-align: center; text-decoration: none; color: #5f6368; transition: all 0.2s; }}
            .quick-action:hover {{ border-color: #1a73e8; color: #1a73e8; transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🗑️ Waste Disposal Management</div>
                <div class="subtitle">COC Tracking, Waste Box Labels & Sample Disposal</div>
                <p style="margin-top: 15px;"><a href="/analytics" style="color: #1a73e8;">← Back to Analytics Dashboard</a></p>
            </div>
            
            <div class="action-bar">
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="showCreateBoxModal()">
                        <i class="fas fa-plus"></i> Create Waste Box
                    </button>
                    <button class="btn btn-success" onclick="showAddItemModal()">
                        <i class="fas fa-flask"></i> Add Waste Item
                    </button>
                    <button class="btn btn-warning" onclick="printLabels()">
                        <i class="fas fa-print"></i> Print Box Labels
                    </button>
                    <button class="btn btn-danger" onclick="showBulkDisposalModal()">
                        <i class="fas fa-trash-alt"></i> Bulk Disposal
                    </button>
                </div>
            </div>

            <div class="dashboard-grid">
                <!-- Left Column: Active Waste Boxes -->
                <div class="waste-boxes">
                    <h2 class="section-title">
                        <i class="fas fa-boxes"></i> Active Waste Boxes
                        <span style="float: right; font-size: 14px; color: #5f6368;">Total: {len(active_boxes)}</span>
                    </h2>
                    
                    <div class="box-grid" id="boxes-container">
                        {"".join([f'''
                        <div class="box-card" data-box-id="{box.id}">
                            <div class="box-header">
                                <div>
                                    <div class="box-id">{box.box_id}</div>
                                    <div class="box-status status-{box.status}">{box.status}</div>
                                </div>
                            </div>
                            <div class="box-details">
                                <strong>Type:</strong> {box.box_type}<br>
                                <strong>Size:</strong> {box.size}<br>
                                <strong>Location:</strong> {box.location}<br>
                                {"<strong>COC Job:</strong> " + (box.coc_job_id or "Not assigned") + "<br>" if box.coc_job_id else ""}
                                <strong>Created:</strong> {box.created_date.strftime("%m/%d/%Y") if box.created_date else "Unknown"}
                            </div>
                            <div class="box-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {box.fill_percentage or 0}%"></div>
                                </div>
                                <small>{box.fill_percentage or 0}% Full</small>
                            </div>
                            <div class="box-actions">
                                <button class="btn btn-primary btn-sm" onclick="viewBoxDetails({box.id})">
                                    <i class="fas fa-eye"></i> View
                                </button>
                                <button class="btn btn-warning btn-sm" onclick="printBoxLabel({box.id})">
                                    <i class="fas fa-print"></i> Label
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="markAsDisposed({box.id})">
                                    <i class="fas fa-check"></i> Dispose
                                </button>
                            </div>
                        </div>
                        ''' for box in active_boxes]) if active_boxes else '<p style="text-align: center; color: #9aa0a6; padding: 40px;">No active waste boxes. Create one to get started.</p>'}
                    </div>
                </div>

                <!-- Right Column: Recent Items -->
                <div class="recent-items">
                    <h2 class="section-title">
                        <i class="fas fa-history"></i> Recent Waste Items
                    </h2>
                    
                    <div class="item-list" id="items-container">
                        {"".join([f'''
                        <div class="item-card {"hazardous" if item.waste_type == "hazardous" else ""}">
                            <div class="item-name">{item.item_name}</div>
                            <div class="item-details">
                                Type: {item.waste_type} | Qty: {item.quantity or "Unknown"}<br>
                                {"COC: " + (item.coc_job_id or "N/A") + " | " if item.coc_job_id else ""}
                                {"Sample ID: " + (item.sample_id or "N/A") + " | " if item.sample_id else ""}
                                Box: {item.waste_box.box_id if hasattr(item, 'waste_box') else "Unknown"}<br>
                                Added: {item.added_date.strftime("%m/%d/%Y %I:%M %p") if item.added_date else "Unknown"}
                                {"| Extra Sample" if item.is_extra_sample else ""}
                            </div>
                        </div>
                        ''' for item in recent_items]) if recent_items else '<p style="text-align: center; color: #9aa0a6; padding: 40px;">No recent waste items.</p>'}
                    </div>
                </div>
            </div>
            
            <div class="quick-actions">
                <h2 class="section-title"><i class="fas fa-bolt"></i> Quick Actions</h2>
                <div class="quick-actions-grid">
                    <div class="quick-action">
                        <i class="fas fa-qrcode" style="font-size: 24px; margin-bottom: 10px;"></i><br>
                        <strong>Scan COC Job ID</strong><br>
                        <small>Quick entry via barcode</small>
                    </div>
                    <div class="quick-action">
                        <i class="fas fa-clock" style="font-size: 24px; margin-bottom: 10px;"></i><br>
                        <strong>Storage Timer</strong><br>
                        <small>Track extra sample timing</small>
                    </div>
                    <div class="quick-action">
                        <i class="fas fa-exchange-alt" style="font-size: 24px; margin-bottom: 10px;"></i><br>
                        <strong>Move Items</strong><br>
                        <small>Transfer between boxes</small>
                    </div>
                    <div class="quick-action">
                        <i class="fas fa-file-excel" style="font-size: 24px; margin-bottom: 10px;"></i><br>
                        <strong>Export Report</strong><br>
                        <small>Generate disposal log</small>
                    </div>
                </div>
            </div>
        </div>

        <script>
        // Placeholder functions for modals and actions
        function showCreateBoxModal() {{
            const boxId = prompt('Enter Box ID:');
            const boxType = prompt('Enter Box Type (hazardous/non-hazardous/glass/sharps):');
            const size = prompt('Enter Size (small/medium/large):');
            const location = prompt('Enter Storage Location:');
            const cocJobId = prompt('Enter COC Job ID (optional):') || null;
            
            if (boxId && boxType && size && location) {{
                alert(`Creating box: ${{boxId}} - Implementation in progress`);
                // TODO: API call to create box
            }}
        }}

        function showAddItemModal() {{
            const itemName = prompt('Enter Item Name:');
            const wasteType = prompt('Enter Waste Type (hazardous/non-hazardous/sharps):');
            const quantity = prompt('Enter Quantity (optional):') || null;
            const cocJobId = prompt('Enter COC Job ID (optional):') || null;
            const sampleId = prompt('Enter Sample ID (optional):') || null;
            const isExtraSample = confirm('Is this an extra sample for storage?');
            
            if (itemName && wasteType) {{
                alert(`Adding item: ${{itemName}} - Implementation in progress`);
                // TODO: API call to add item
            }}
        }}

        function printLabels() {{
            alert('Label printing functionality - Implementation in progress');
        }}

        function showBulkDisposalModal() {{
            alert('Bulk disposal modal - Implementation in progress');
        }}

        function viewBoxDetails(boxId) {{
            alert(`Viewing box details for ID: ${{boxId}} - Implementation in progress`);
        }}

        function printBoxLabel(boxId) {{
            window.open(`/waste/boxes/${{boxId}}/label`, '_blank');
        }}

        function markAsDisposed(boxId) {{
            if (confirm('Mark this box as disposed? This action cannot be undone.')) {{
                alert(`Marking box ${{boxId}} as disposed - Implementation in progress`);
                // TODO: API call to update box status
            }}
        }}
        </script>
    </body>
    </html>
    """
    
    return html_content

@router.post("/boxes")
async def create_waste_box(
    box: WasteBoxCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new waste box"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Check if box ID already exists
    existing_box = db.query(WasteBox).filter(WasteBox.box_id == box.box_id).first()
    if existing_box:
        raise HTTPException(status_code=400, detail="Box ID already exists")
    
    db_box = WasteBox(
        box_id=box.box_id,
        coc_job_id=box.coc_job_id,
        box_type=box.box_type,
        size=box.size,
        location=box.location,
        created_by=current_user.id
    )
    
    db.add(db_box)
    db.commit()
    db.refresh(db_box)
    
    return {"success": True, "box": db_box.to_dict()}

@router.post("/items")
async def add_waste_item(
    item: WasteItemCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Add a waste item to a box"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Verify waste box exists
    waste_box = db.query(WasteBox).filter(WasteBox.id == item.waste_box_id).first()
    if not waste_box:
        raise HTTPException(status_code=404, detail="Waste box not found")
    
    db_item = WasteItem(
        item_name=item.item_name,
        description=item.description,
        waste_type=item.waste_type,
        quantity=item.quantity,
        coc_job_id=item.coc_job_id,
        sample_id=item.sample_id,
        is_extra_sample=item.is_extra_sample,
        waste_box_id=item.waste_box_id,
        added_by=current_user.id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return {"success": True, "item": db_item.to_dict()}

@router.get("/boxes/{box_id}/label")
async def print_box_label(box_id: int, db: Session = Depends(get_db)):
    """Generate a printable label for a waste box"""
    waste_box = db.query(WasteBox).filter(WasteBox.id == box_id).first()
    if not waste_box:
        raise HTTPException(status_code=404, detail="Waste box not found")
    
    # Create PDF in memory
    buffer = io.BytesIO()
    
    # Create PDF with ReportLab
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"<b>WASTE BOX LABEL</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Box details table
    box_data = [
        ['Box ID:', waste_box.box_id],
        ['Type:', waste_box.box_type.upper()],
        ['Size:', waste_box.size.upper()],
        ['Location:', waste_box.location],
        ['COC Job ID:', waste_box.coc_job_id or 'Not assigned'],
        ['Created:', waste_box.created_date.strftime('%m/%d/%Y') if waste_box.created_date else 'Unknown'],
        ['Status:', waste_box.status.upper()]
    ]
    
    table = Table(box_data, colWidths=[2*72, 4*72])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Generate QR code for box ID
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"WASTE_BOX:{waste_box.box_id}")
    qr.make(fit=True)
    
    # Add QR code info
    qr_info = Paragraph("<b>QR Code for Quick Scanning</b><br/>Scan to quickly access box details", styles['Normal'])
    story.append(qr_info)
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    
    # Return as streaming response
    headers = {
        'Content-Disposition': f'attachment; filename="waste_box_label_{waste_box.box_id}.pdf"'
    }
    
    return StreamingResponse(
        io.BytesIO(buffer.read()),
        media_type='application/pdf',
        headers=headers
    )

@router.get("/boxes")
async def list_waste_boxes(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List waste boxes with optional status filter"""
    query = db.query(WasteBox)
    
    if status:
        query = query.filter(WasteBox.status == status)
    
    boxes = query.order_by(desc(WasteBox.created_date)).all()
    return {"boxes": [box.to_dict() for box in boxes]}

@router.get("/items")
async def list_waste_items(
    box_id: Optional[int] = None,
    waste_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List waste items with optional filters"""
    query = db.query(WasteItem)
    
    if box_id:
        query = query.filter(WasteItem.waste_box_id == box_id)
    
    if waste_type:
        query = query.filter(WasteItem.waste_type == waste_type)
    
    items = query.order_by(desc(WasteItem.added_date)).limit(limit).all()
    return {"items": [item.to_dict() for item in items]}