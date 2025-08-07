"""
Reminders and notes routes for dashboard functionality
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.auth.jwt_handler import get_optional_user
from app.models.analytics import DashboardReminder, DepartmentNote
from pydantic import BaseModel

router = APIRouter()

# Pydantic models
class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    reminder_type: str
    due_date: datetime
    priority: str = "medium"
    assigned_to: Optional[int] = None

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_type: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    is_completed: Optional[bool] = None

class NoteCreate(BaseModel):
    title: str
    content: str
    note_type: str = "general"
    is_pinned: bool = False
    is_public: bool = True
    department: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_public: Optional[bool] = None

# Reminders API Routes
@router.post("/api/reminders")
async def create_reminder(
    reminder: ReminderCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new reminder"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db_reminder = DashboardReminder(
        title=reminder.title,
        description=reminder.description,
        reminder_type=reminder.reminder_type,
        due_date=reminder.due_date,
        priority=reminder.priority,
        assigned_to=reminder.assigned_to,
        created_by=current_user.id
    )
    
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    
    return {"success": True, "reminder": db_reminder.to_dict()}

@router.get("/api/reminders")
async def get_reminders(
    request: Request,
    status: Optional[str] = "active",
    priority: Optional[str] = None,
    assigned_to_me: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get reminders with optional filters"""
    current_user = await get_optional_user(request, db)
    
    query = db.query(DashboardReminder)
    
    if status:
        query = query.filter(DashboardReminder.status == status)
    
    if priority:
        query = query.filter(DashboardReminder.priority == priority)
    
    if assigned_to_me and current_user:
        query = query.filter(
            or_(
                DashboardReminder.assigned_to == current_user.id,
                DashboardReminder.created_by == current_user.id
            )
        )
    
    reminders = query.order_by(
        DashboardReminder.due_date.asc()
    ).limit(limit).all()
    
    return {"reminders": [reminder.to_dict() for reminder in reminders]}

@router.put("/api/reminders/{reminder_id}")
async def update_reminder(
    reminder_id: int,
    reminder_update: ReminderUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a reminder"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    reminder = db.query(DashboardReminder).filter(
        DashboardReminder.id == reminder_id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Check permissions
    if reminder.created_by != current_user.id and reminder.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this reminder")
    
    # Update fields
    update_data = reminder_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)
    
    if reminder_update.is_completed and not reminder.completed_at:
        reminder.completed_at = datetime.utcnow()
        reminder.status = "completed"
    
    db.commit()
    db.refresh(reminder)
    
    return {"success": True, "reminder": reminder.to_dict()}

@router.delete("/api/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a reminder"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    reminder = db.query(DashboardReminder).filter(
        and_(
            DashboardReminder.id == reminder_id,
            DashboardReminder.created_by == current_user.id
        )
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found or not authorized")
    
    db.delete(reminder)
    db.commit()
    
    return {"success": True}

# Notes API Routes
@router.post("/api/notes")
async def create_note(
    note: NoteCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new department note"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db_note = DepartmentNote(
        title=note.title,
        content=note.content,
        note_type=note.note_type,
        is_pinned=note.is_pinned,
        is_public=note.is_public,
        department=note.department,
        created_by=current_user.id
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return {"success": True, "note": db_note.to_dict()}

@router.get("/api/notes")
async def get_notes(
    note_type: Optional[str] = None,
    pinned_only: bool = False,
    department: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get department notes with optional filters"""
    query = db.query(DepartmentNote).filter(DepartmentNote.is_public == True)
    
    if note_type:
        query = query.filter(DepartmentNote.note_type == note_type)
    
    if pinned_only:
        query = query.filter(DepartmentNote.is_pinned == True)
    
    if department:
        query = query.filter(
            or_(
                DepartmentNote.department == department,
                DepartmentNote.department.is_(None)
            )
        )
    
    notes = query.order_by(
        desc(DepartmentNote.is_pinned),
        desc(DepartmentNote.created_at)
    ).limit(limit).all()
    
    return {"notes": [note.to_dict() for note in notes]}

@router.put("/api/notes/{note_id}")
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a note"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    note = db.query(DepartmentNote).filter(
        and_(
            DepartmentNote.id == note_id,
            DepartmentNote.created_by == current_user.id
        )
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not authorized")
    
    # Update fields
    update_data = note_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    db.commit()
    db.refresh(note)
    
    return {"success": True, "note": note.to_dict()}

@router.delete("/api/notes/{note_id}")
async def delete_note(
    note_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a note"""
    current_user = await get_optional_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    note = db.query(DepartmentNote).filter(
        and_(
            DepartmentNote.id == note_id,
            DepartmentNote.created_by == current_user.id
        )
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not authorized")
    
    db.delete(note)
    db.commit()
    
    return {"success": True}

# HTML Routes for integrated dashboard
@router.get("/reminders", response_class=HTMLResponse)
async def reminders_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Reminders management page"""
    current_user = await get_optional_user(request, db)
    
    # Get user's reminders
    user_reminders = []
    if current_user:
        user_reminders = db.query(DashboardReminder).filter(
            or_(
                DashboardReminder.created_by == current_user.id,
                DashboardReminder.assigned_to == current_user.id
            ),
            DashboardReminder.status == "active"
        ).order_by(DashboardReminder.due_date).all()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔔 Reminders - EHS Electronic Journal</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f8f9fa, #e9ecef); min-height: 100vh; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
            
            .header {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
            .logo {{ font-size: 32px; font-weight: bold; color: #fbbc04; margin-bottom: 10px; }}
            .subtitle {{ color: #666; font-size: 18px; }}
            
            .action-bar {{ background: white; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .btn {{ padding: 12px 24px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }}
            .btn-primary {{ background: linear-gradient(135deg, #1a73e8, #4285f4); color: white; }}
            .btn:hover {{ transform: translateY(-1px); }}
            
            .reminders-list {{ background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .section-title {{ font-size: 20px; font-weight: 600; color: #202124; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #e8eaed; }}
            
            .reminder-card {{ background: #f8f9fa; border-left: 4px solid #1a73e8; padding: 15px; margin-bottom: 15px; border-radius: 0 8px 8px 0; transition: all 0.2s; }}
            .reminder-card:hover {{ transform: translateX(3px); background: white; }}
            .reminder-card.priority-high {{ border-left-color: #ea4335; }}
            .reminder-card.priority-critical {{ border-left-color: #d93025; background: #ffeaea; }}
            
            .reminder-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }}
            .reminder-title {{ font-weight: 600; color: #202124; }}
            .reminder-due {{ font-size: 12px; color: #5f6368; }}
            .reminder-description {{ color: #5f6368; font-size: 14px; margin-bottom: 10px; }}
            .reminder-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #9aa0a6; }}
            .reminder-actions {{ display: flex; gap: 5px; }}
            .btn-sm {{ padding: 4px 8px; font-size: 11px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🔔 Reminders & Events</div>
                <div class="subtitle">Stay on top of important lab tasks and deadlines</div>
                <p style="margin-top: 15px;"><a href="/analytics" style="color: #1a73e8;">← Back to Analytics Dashboard</a></p>
            </div>
            
            <div class="action-bar">
                <button class="btn btn-primary" onclick="showAddReminderModal()">
                    <i class="fas fa-plus"></i> Add Reminder
                </button>
            </div>

            <div class="reminders-list">
                <h2 class="section-title">
                    <i class="fas fa-bell"></i> Your Reminders
                    <span style="float: right; font-size: 14px; color: #5f6368;">Total: {len(user_reminders)}</span>
                </h2>
                
                <div id="reminders-container">
                    {"".join([f'''
                    <div class="reminder-card priority-{reminder.priority}" data-reminder-id="{reminder.id}">
                        <div class="reminder-header">
                            <div class="reminder-title">{reminder.title}</div>
                            <div class="reminder-due">Due: {reminder.due_date.strftime("%m/%d/%Y %I:%M %p") if reminder.due_date else "No due date"}</div>
                        </div>
                        {f'<div class="reminder-description">{reminder.description}</div>' if reminder.description else ''}
                        <div class="reminder-meta">
                            <span>Type: {reminder.reminder_type} | Priority: {reminder.priority}</span>
                            <div class="reminder-actions">
                                <button class="btn btn-success btn-sm" onclick="markCompleted({reminder.id})">
                                    <i class="fas fa-check"></i>
                                </button>
                                <button class="btn btn-warning btn-sm" onclick="editReminder({reminder.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-danger btn-sm" onclick="deleteReminder({reminder.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    ''' for reminder in user_reminders]) if user_reminders else '<p style="text-align: center; color: #9aa0a6; padding: 40px;">No active reminders. Add one to get started!</p>'}
                </div>
            </div>
        </div>

        <script>
        function showAddReminderModal() {{
            const title = prompt('Reminder title:');
            const description = prompt('Description (optional):') || '';
            const reminderType = prompt('Type (task/deadline/maintenance/calibration):') || 'task';
            const dueDateStr = prompt('Due date (YYYY-MM-DD HH:MM):');
            const priority = prompt('Priority (low/medium/high/critical):') || 'medium';
            
            if (title && dueDateStr) {{
                alert(`Creating reminder: ${{title}} - Implementation in progress`);
                // TODO: API call to create reminder
            }}
        }}

        function markCompleted(reminderId) {{
            alert(`Marking reminder ${{reminderId}} as completed - Implementation in progress`);
            // TODO: API call to update reminder
        }}

        function editReminder(reminderId) {{
            alert(`Editing reminder ${{reminderId}} - Implementation in progress`);
            // TODO: Show edit modal
        }}

        function deleteReminder(reminderId) {{
            if (confirm('Delete this reminder?')) {{
                alert(`Deleting reminder ${{reminderId}} - Implementation in progress`);
                // TODO: API call to delete reminder
            }}
        }}
        </script>
    </body>
    </html>
    """
    
    return html_content

@router.get("/notes", response_class=HTMLResponse)
async def notes_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Department notes page"""
    current_user = await get_optional_user(request, db)
    
    # Get public notes
    public_notes = db.query(DepartmentNote).filter(
        DepartmentNote.is_public == True
    ).order_by(
        desc(DepartmentNote.is_pinned),
        desc(DepartmentNote.created_at)
    ).limit(20).all()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📝 Department Notes - EHS Electronic Journal</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f8f9fa, #e9ecef); min-height: 100vh; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
            
            .header {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
            .logo {{ font-size: 32px; font-weight: bold; color: #34a853; margin-bottom: 10px; }}
            .subtitle {{ color: #666; font-size: 18px; }}
            
            .action-bar {{ background: white; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .btn {{ padding: 12px 24px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }}
            .btn-primary {{ background: linear-gradient(135deg, #1a73e8, #4285f4); color: white; }}
            .btn:hover {{ transform: translateY(-1px); }}
            
            .notes-list {{ background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
            .section-title {{ font-size: 20px; font-weight: 600; color: #202124; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #e8eaed; }}
            
            .note-card {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px; transition: all 0.2s; border: 1px solid transparent; }}
            .note-card:hover {{ border-color: #e8eaed; background: white; transform: translateY(-1px); }}
            .note-card.pinned {{ border-left: 4px solid #fbbc04; background: #fffbf0; }}
            
            .note-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
            .note-title {{ font-weight: 600; color: #202124; font-size: 16px; }}
            .note-type {{ padding: 3px 8px; border-radius: 12px; font-size: 11px; background: #e8eaed; color: #5f6368; text-transform: uppercase; }}
            
            .note-content {{ color: #5f6368; line-height: 1.5; margin-bottom: 12px; }}
            .note-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #9aa0a6; }}
            .note-actions {{ display: flex; gap: 5px; }}
            .btn-sm {{ padding: 4px 8px; font-size: 11px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">📝 Department Notes</div>
                <div class="subtitle">Shared announcements, procedures, and important information</div>
                <p style="margin-top: 15px;"><a href="/analytics" style="color: #1a73e8;">← Back to Analytics Dashboard</a></p>
            </div>
            
            <div class="action-bar">
                <button class="btn btn-primary" onclick="showAddNoteModal()">
                    <i class="fas fa-plus"></i> Add Note
                </button>
            </div>

            <div class="notes-list">
                <h2 class="section-title">
                    <i class="fas fa-sticky-note"></i> Recent Notes
                    <span style="float: right; font-size: 14px; color: #5f6368;">Total: {len(public_notes)}</span>
                </h2>
                
                <div id="notes-container">
                    {"".join([f'''
                    <div class="note-card {"pinned" if note.is_pinned else ""}" data-note-id="{note.id}">
                        <div class="note-header">
                            <div class="note-title">
                                {"<i class='fas fa-thumbtack'></i> " if note.is_pinned else ""}{note.title}
                            </div>
                            <div class="note-type">{note.note_type}</div>
                        </div>
                        <div class="note-content">{note.content}</div>
                        <div class="note-meta">
                            <span>Created: {note.created_at.strftime("%m/%d/%Y %I:%M %p") if note.created_at else "Unknown"}</span>
                            {"<div class='note-actions'><button class='btn btn-warning btn-sm' onclick='editNote(" + str(note.id) + ")'><i class='fas fa-edit'></i></button><button class='btn btn-danger btn-sm' onclick='deleteNote(" + str(note.id) + ")'><i class='fas fa-trash'></i></button></div>" if current_user and note.created_by == current_user.id else ""}
                        </div>
                    </div>
                    ''' for note in public_notes]) if public_notes else '<p style="text-align: center; color: #9aa0a6; padding: 40px;">No notes yet. Add the first one!</p>'}
                </div>
            </div>
        </div>

        <script>
        function showAddNoteModal() {{
            const title = prompt('Note title:');
            const content = prompt('Note content:');
            const noteType = prompt('Type (general/announcement/procedure/important):') || 'general';
            const isPinned = confirm('Pin this note to the top?');
            
            if (title && content) {{
                alert(`Creating note: ${{title}} - Implementation in progress`);
                // TODO: API call to create note
            }}
        }}

        function editNote(noteId) {{
            alert(`Editing note ${{noteId}} - Implementation in progress`);
            // TODO: Show edit modal
        }}

        function deleteNote(noteId) {{
            if (confirm('Delete this note?')) {{
                alert(`Deleting note ${{noteId}} - Implementation in progress`);
                // TODO: API call to delete note
            }}
        }}
        </script>
    </body>
    </html>
    """
    
    return html_content