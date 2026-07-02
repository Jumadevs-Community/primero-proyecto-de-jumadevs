from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Task, Collaborator
from app.auth import get_current_user

router = APIRouter()


@router.get("/")
async def list_tasks(
    project_id: int = Query(...),
    status: str | None = None,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Task).where(Task.project_id == project_id, Task.deleted_at.is_(None))
    if status:
        q = q.where(Task.status == status)
    result = await db.execute(q.order_by(Task.created_at.desc()))
    return result.scalars().all()


@router.post("/", status_code=201)
async def create_task(
    project_id: int = Query(...),
    payload: dict = ...,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = Task(project_id=project_id, created_by=current_user, **payload)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}")
async def update_task(
    task_id: int,
    payload: dict,
    current_user: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.deleted_at.is_(None)))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    for k, v in payload.items():
        setattr(task, k, v)
    await db.commit()
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, current_user: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.deleted_at.is_(None)))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task not found")
    from datetime import datetime
    task.deleted_at = datetime.utcnow()
    await db.commit()
