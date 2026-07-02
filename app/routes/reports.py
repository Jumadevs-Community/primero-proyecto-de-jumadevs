import csv, io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Task, TaskStatus, Collaborator
from app.auth import get_current_user

router = APIRouter()


@router.get("/{project_id}/summary")
async def project_summary(project_id: int, current_user: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    counts = {}
    for status in TaskStatus:
        r = await db.execute(select(func.count(Task.id)).where(
            Task.project_id == project_id, Task.status == status, Task.deleted_at.is_(None)))
        counts[status.value] = r.scalar()
    total = sum(counts.values())
    return {"project_id": project_id, "total_tasks": total, "by_status": counts,
            "completion_pct": round(counts.get("done", 0) / total * 100, 1) if total else 0.0}


@router.get("/{project_id}/export/csv")
async def export_csv(project_id: int, current_user: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.project_id == project_id, Task.deleted_at.is_(None)).order_by(Task.created_at))
    tasks = result.scalars().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Status", "Priority", "Assignee", "Due Date", "Created At"])
    for t in tasks:
        writer.writerow([t.id, t.title, t.status.value, t.priority.value, t.assignee_id or "", t.due_date or "", t.created_at])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_tasks.csv"})

# subtask: GET /reports/{project_id}/summary
