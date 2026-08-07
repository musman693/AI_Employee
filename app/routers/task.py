"""
task.py — AI Task Manager API endpoints.

Endpoints:
  POST   /api/v1/task/                        Create a new task
  GET    /api/v1/task/                        List all tasks (with filters)
  GET    /api/v1/task/{task_id}               Get task details
  PUT    /api/v1/task/{task_id}               Update a task
  PATCH  /api/v1/task/{task_id}/status        Update task progress/status
  DELETE /api/v1/task/{task_id}               Delete a task
  POST   /api/v1/task/{task_id}/assign        Assign task to user
  GET    /api/v1/task/my-tasks                Get tasks assigned to current user
  GET    /api/v1/task/overdue                 Get overdue tasks
  GET    /api/v1/task/summary                 Get task summary statistics

Note: Tasks are stored in-memory for now. Connect to PostgreSQL for persistence.
      AI reminders and suggestions use mock logic; uncomment OpenAI blocks for live AI.
"""

from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import math

from app.models.task_models import (
    Task, TaskPriority, TaskStatus,
    CreateTaskRequest, UpdateTaskRequest,
    AssignTaskRequest, UpdateTaskStatusRequest,
    TaskListResponse, TaskSummary,
)

router = APIRouter()

# ── In-memory task store (replace with PostgreSQL in production) ──────────────
_tasks: dict[str, dict] = {}
_task_counter = 0


def _generate_task_id() -> str:
    """Generate a unique task ID like TASK-001."""
    global _task_counter
    _task_counter += 1
    return f"TASK-{_task_counter:03d}"


def _get_task_or_404(task_id: str) -> dict:
    """Get a task from the store or raise 404."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return _tasks[task_id]


def _is_overdue(task: dict) -> bool:
    """Check if a task is overdue."""
    if task["due_date"] is None:
        return False
    if task["status"] == TaskStatus.COMPLETED:
        return False
    due = task["due_date"]
    if isinstance(due, str):
        due = date.fromisoformat(due)
    return due < date.today()


def _generate_ai_suggestions(task: dict) -> Optional[str]:
    """Generate AI-powered task suggestions (mock implementation)."""
    # Uncomment below for live OpenAI integration:
    # import openai, os
    # openai.api_key = os.getenv("OPENAI_API_KEY", "")
    # response = openai.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{
    #         "role": "system",
    #         "content": "You are a project management AI assistant. Provide actionable suggestions."
    #     }, {
    #         "role": "user",
    #         "content": f"Task: {task['title']}, Priority: {task['priority']}, Due: {task['due_date']}"
    #     }]
    # )
    # return response.choices[0].message.content

    # Mock AI suggestions based on task properties
    suggestions = []
    if task["priority"] == TaskPriority.URGENT:
        suggestions.append("This urgent task should be prioritized immediately.")
    if task["due_date"]:
        due = task["due_date"]
        if isinstance(due, str):
            due = date.fromisoformat(due)
        days_left = (due - date.today()).days
        if days_left <= 2:
            suggestions.append(f"Due in {days_left} days — consider breaking into smaller subtasks.")
        elif days_left < 0:
            suggestions.append("This task is overdue — escalate to management if blocked.")
    if task.get("progress_percent", 0) > 0 and task.get("progress_percent", 0) < 50:
        suggestions.append("Progress is slow — review for blockers and consider pair programming.")
    if len(task.get("tags", [])) == 0:
        suggestions.append("Add relevant tags to improve task discoverability and reporting.")

    return " ".join(suggestions) if suggestions else None


# ─────────────────────────────────────────────────────────────────────────────
# Static routes MUST come before dynamic {task_id} routes
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# POST / — Create a new task
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=Task, status_code=201,
             summary="AI Task Manager — create a new task")
def create_task(payload: CreateTaskRequest):
    """
    Create a new task with title, description, priority, due date, and optional AI reminders.
    Returns the created task with a generated ID.
    """
    now = datetime.utcnow().isoformat()
    task_id = _generate_task_id()

    task_data = {
        "id": task_id,
        "title": payload.title,
        "description": payload.description,
        "priority": payload.priority,
        "status": TaskStatus.TODO,
        "assigned_to": payload.assigned_to,
        "assigned_by": None,
        "due_date": payload.due_date.isoformat() if payload.due_date else None,
        "estimated_hours": payload.estimated_hours,
        "actual_hours": None,
        "progress_percent": 0,
        "tags": payload.tags,
        "project": payload.project,
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
        "ai_reminder_enabled": payload.ai_reminder_enabled,
        "ai_suggestions": None,
    }

    # Generate AI suggestions
    task_data["ai_suggestions"] = _generate_ai_suggestions(task_data)

    _tasks[task_id] = task_data
    return task_data


# ─────────────────────────────────────────────────────────────────────────────
# GET /my-tasks — Get tasks assigned to current user (BEFORE /{task_id})
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/my-tasks", response_model=TaskListResponse,
            summary="AI Task Manager — get my tasks")
def get_my_tasks(
    user_email: str = Query(..., description="Current user's email address"),
    include_completed: bool = Query(False, description="Include completed tasks"),
):
    """
    Get all tasks assigned to the current user.
    Use include_completed=true to also show completed tasks.
    """
    tasks = [t for t in _tasks.values() if t["assigned_to"] == user_email]

    if not include_completed:
        tasks = [t for t in tasks if t["status"] != TaskStatus.COMPLETED]

    # Sort by priority then due date
    priority_order = {TaskPriority.URGENT: 0, TaskPriority.HIGH: 1, TaskPriority.MEDIUM: 2, TaskPriority.LOW: 3}
    tasks.sort(key=lambda t: (priority_order.get(t["priority"], 4), t.get("due_date") or "9999-12-31"))

    return TaskListResponse(
        tasks=tasks,
        total=len(tasks),
        page=1,
        page_size=100,
        total_pages=1,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /overdue — Get overdue tasks (BEFORE /{task_id})
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/overdue", response_model=TaskListResponse,
            summary="AI Task Manager — get overdue tasks")
def get_overdue_tasks(
    assigned_to: Optional[str] = Query(None, description="Filter by specific assignee"),
):
    """
    Get all tasks that are past their due date and not completed.
    Useful for AI reminders and escalation workflows.
    """
    overdue_tasks = [t for t in _tasks.values() if _is_overdue(t)]

    if assigned_to:
        overdue_tasks = [t for t in overdue_tasks if t["assigned_to"] == assigned_to]

    # Sort by due date (most overdue first)
    overdue_tasks.sort(key=lambda t: t.get("due_date") or "9999-12-31")

    return TaskListResponse(
        tasks=overdue_tasks,
        total=len(overdue_tasks),
        page=1,
        page_size=100,
        total_pages=1,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /summary — Get task summary statistics (BEFORE /{task_id})
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/summary", response_model=TaskSummary,
            summary="AI Task Manager — get task summary statistics")
def get_task_summary(
    user_email: Optional[str] = Query(None, description="Filter stats for specific user"),
):
    """
    Get summary statistics about tasks including total count, completion rate,
    overdue count, and high-priority pending tasks.
    """
    tasks = list(_tasks.values())

    if user_email:
        tasks = [t for t in tasks if t["assigned_to"] == user_email]

    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == TaskStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t["status"] == TaskStatus.IN_PROGRESS)
    overdue = sum(1 for t in tasks if _is_overdue(t))
    my_tasks = sum(1 for t in tasks if t["assigned_to"] == user_email) if user_email else total
    high_priority_pending = sum(
        1 for t in tasks
        if t["priority"] in (TaskPriority.HIGH, TaskPriority.URGENT)
        and t["status"] not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)
    )

    return TaskSummary(
        total_tasks=total,
        completed_tasks=completed,
        in_progress_tasks=in_progress,
        overdue_tasks=overdue,
        my_tasks=my_tasks,
        high_priority_pending=high_priority_pending,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET / — List all tasks (with filters)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=TaskListResponse,
            summary="AI Task Manager — list all tasks")
def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assignee email"),
    project: Optional[str] = Query(None, description="Filter by project name"),
    overdue: Optional[bool] = Query(None, description="Filter overdue tasks only"),
):
    """
    List tasks with pagination and optional filters for status, priority, assignee, project.
    Set overdue=true to get only overdue tasks.
    """
    tasks = list(_tasks.values())

    # Apply filters
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]
    if assigned_to:
        tasks = [t for t in tasks if t["assigned_to"] == assigned_to]
    if project:
        tasks = [t for t in tasks if t["project"] == project]
    if overdue:
        tasks = [t for t in tasks if _is_overdue(t)]

    # Sort by priority (urgent first) then by due date
    priority_order = {TaskPriority.URGENT: 0, TaskPriority.HIGH: 1, TaskPriority.MEDIUM: 2, TaskPriority.LOW: 3}
    tasks.sort(key=lambda t: (priority_order.get(t["priority"], 4), t.get("due_date") or "9999-12-31"))

    # Paginate
    total = len(tasks)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    start = (page - 1) * page_size
    end = start + page_size
    paginated_tasks = tasks[start:end]

    return TaskListResponse(
        tasks=paginated_tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /{task_id} — Get task details
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/{task_id}", response_model=Task,
            summary="AI Task Manager — get task details")
def get_task(task_id: str):
    """Get detailed information about a specific task by ID."""
    return _get_task_or_404(task_id)


# ─────────────────────────────────────────────────────────────────────────────
# PUT /{task_id} — Update a task
# ─────────────────────────────────────────────────────────────────────────────
@router.put("/{task_id}", response_model=Task,
            summary="AI Task Manager — update a task")
def update_task(task_id: str, payload: UpdateTaskRequest):
    """
    Update a task's title, description, priority, due date, tags, or project.
    Fields not provided will remain unchanged.
    """
    task = _get_task_or_404(task_id)

    if payload.title is not None:
        task["title"] = payload.title
    if payload.description is not None:
        task["description"] = payload.description
    if payload.priority is not None:
        task["priority"] = payload.priority
    if payload.due_date is not None:
        task["due_date"] = payload.due_date.isoformat()
    if payload.estimated_hours is not None:
        task["estimated_hours"] = payload.estimated_hours
    if payload.tags is not None:
        task["tags"] = payload.tags
    if payload.project is not None:
        task["project"] = payload.project
    if payload.ai_reminder_enabled is not None:
        task["ai_reminder_enabled"] = payload.ai_reminder_enabled

    task["updated_at"] = datetime.utcnow().isoformat()

    # Regenerate AI suggestions
    task["ai_suggestions"] = _generate_ai_suggestions(task)

    _tasks[task_id] = task
    return task


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /{task_id}/status — Update task progress/status
# ─────────────────────────────────────────────────────────────────────────────
@router.patch("/{task_id}/status", response_model=Task,
              summary="AI Task Manager — update task progress")
def update_task_status(task_id: str, payload: UpdateTaskStatusRequest):
    """
    Update a task's status, progress percentage, and/or actual hours spent.
    Automatically sets completed_at when status changes to COMPLETED.
    """
    task = _get_task_or_404(task_id)

    if payload.status is not None:
        task["status"] = payload.status
        if payload.status == TaskStatus.COMPLETED:
            task["completed_at"] = datetime.utcnow().isoformat()
            task["progress_percent"] = 100
        elif payload.status == TaskStatus.CANCELLED:
            task["completed_at"] = datetime.utcnow().isoformat()
        else:
            task["completed_at"] = None

    if payload.progress_percent is not None:
        task["progress_percent"] = payload.progress_percent

    if payload.actual_hours is not None:
        task["actual_hours"] = payload.actual_hours

    task["updated_at"] = datetime.utcnow().isoformat()
    _tasks[task_id] = task
    return task


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /{task_id} — Delete a task
# ─────────────────────────────────────────────────────────────────────────────
@router.delete("/{task_id}", status_code=204,
               summary="AI Task Manager — delete a task")
def delete_task(task_id: str):
    """Delete a task by ID. This action cannot be undone."""
    _get_task_or_404(task_id)
    del _tasks[task_id]


# ─────────────────────────────────────────────────────────────────────────────
# POST /{task_id}/assign — Assign task to user
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/{task_id}/assign", response_model=Task,
             summary="AI Task Manager — assign task to user")
def assign_task(task_id: str, payload: AssignTaskRequest):
    """
    Assign a task to a user. Optionally record who made the assignment.
    The task status will be set to TODO if it was unassigned.
    """
    task = _get_task_or_404(task_id)

    task["assigned_to"] = payload.assigned_to
    task["assigned_by"] = payload.assigned_by
    task["updated_at"] = datetime.utcnow().isoformat()

    # Reset status if task was unassigned
    if task["status"] == TaskStatus.TODO and not task.get("assigned_by"):
        task["status"] = TaskStatus.TODO

    _tasks[task_id] = task
    return task


