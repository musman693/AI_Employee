"""
task_models.py — Pydantic models for AI Task Manager.

Models:
  - TaskPriority: Low, Medium, High, Urgent
  - TaskStatus: Todo, InProgress, InReview, Completed, Cancelled
  - Task: Full task model with all fields
  - CreateTaskRequest: Request model for creating a task
  - UpdateTaskRequest: Request model for updating a task
  - AssignTaskRequest: Request model for assigning a task
  - UpdateTaskStatusRequest: Request model for updating task progress
  - TaskListResponse: Paginated task list response
"""

from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """Complete task model with all fields."""
    id: str
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    assigned_to: Optional[str] = None
    assigned_by: Optional[str] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    progress_percent: int = 0
    tags: List[str] = []
    project: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    ai_reminder_enabled: bool = False
    ai_suggestions: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "TASK-001",
            "title": "Build AI Email Assistant",
            "description": "Implement email drafting and auto-reply features",
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "tayyab@example.com",
            "assigned_by": "manager@example.com",
            "due_date": "2026-08-15",
            "estimated_hours": 40.0,
            "actual_hours": 12.5,
            "progress_percent": 60,
            "tags": ["backend", "ai", "email"],
            "project": "AI Employee OS",
            "created_at": "2026-08-01T10:00:00",
            "updated_at": "2026-08-07T14:30:00",
            "completed_at": None,
            "ai_reminder_enabled": True,
            "ai_suggestions": "Consider adding spam detection to the email classifier."
        }
    })


class CreateTaskRequest(BaseModel):
    """Request model for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, gt=0)
    tags: List[str] = []
    project: Optional[str] = None
    ai_reminder_enabled: bool = False

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "Implement Workflow Automation",
            "description": "Build trigger-action workflow engine",
            "priority": "high",
            "assigned_to": "muzahir@example.com",
            "due_date": "2026-08-20",
            "estimated_hours": 24.0,
            "tags": ["backend", "automation"],
            "project": "AI Employee OS",
            "ai_reminder_enabled": True
        }
    })


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    project: Optional[str] = None
    ai_reminder_enabled: Optional[bool] = None


class AssignTaskRequest(BaseModel):
    """Request model for assigning a task to a user."""
    assigned_to: str = Field(..., min_length=1)
    assigned_by: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "assigned_to": "developer@example.com",
            "assigned_by": "manager@example.com"
        }
    })


class UpdateTaskStatusRequest(BaseModel):
    """Request model for updating task progress/status."""
    status: Optional[TaskStatus] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    actual_hours: Optional[float] = Field(None, ge=0)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "in_progress",
            "progress_percent": 50,
            "actual_hours": 8.5
        }
    })


class TaskListResponse(BaseModel):
    """Paginated task list response."""
    tasks: List[Task]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "tasks": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
            "total_pages": 0
        }
    })


class TaskSummary(BaseModel):
    """Summary statistics for tasks."""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    my_tasks: int
    high_priority_pending: int

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_tasks": 25,
            "completed_tasks": 12,
            "in_progress_tasks": 8,
            "overdue_tasks": 3,
            "my_tasks": 7,
            "high_priority_pending": 4
        }
    })