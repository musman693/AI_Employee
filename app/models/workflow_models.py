"""
workflow_models.py — Pydantic models for Workflow Automation Engine.

Models:
  - WorkflowTriggerType: Event types that can trigger workflows
  - WorkflowActionType: Action types that workflows can execute
  - WorkflowStatus: Status of a workflow definition
  - WorkflowTrigger: Trigger definition for a workflow
  - WorkflowAction: Action definition for a workflow
  - Workflow: Complete workflow definition
  - WorkflowExecution: Record of a workflow execution
  - CreateWorkflowRequest: Request model for creating a workflow
  - ExecuteWorkflowRequest: Request model for manually triggering a workflow
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any


class WorkflowTriggerType(str, Enum):
    """Event types that can trigger workflows."""
    INVOICE_PAID = "invoice.paid"
    INVOICE_SENT = "invoice.sent"
    INVOICE_OVERDUE = "invoice.overdue"
    TASK_COMPLETED = "task.completed"
    TASK_OVERDUE = "task.overdue"
    TASK_ASSIGNED = "task.assigned"
    CUSTOMER_CREATED = "customer.created"
    DEAL_WON = "deal.won"
    DEAL_LOST = "deal.lost"
    QUOTATION_APPROVED = "quotation.approved"
    QUOTATION_REJECTED = "quotation.rejected"
    MANUAL = "manual"  # Manual trigger via API


class WorkflowActionType(str, Enum):
    """Action types that workflows can execute."""
    SEND_EMAIL = "send_email"
    CREATE_RECEIPT = "create_receipt"
    UPDATE_CRM = "update_crm"
    NOTIFY_SLACK = "notify_slack"
    NOTIFY_SALES = "notify_sales"
    CREATE_FOLLOWUP = "create_followup"
    CREATE_TASK = "create_task"
    UPDATE_INVOICE = "update_invoice"
    GENERATE_DOCUMENT = "generate_document"
    WEBHOOK = "webhook"
    DELAY = "delay"


class WorkflowStatus(str, Enum):
    """Status of a workflow definition."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class WorkflowExecutionStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowTrigger(BaseModel):
    """Trigger definition for a workflow."""
    type: WorkflowTriggerType
    conditions: Optional[Dict[str, Any]] = None  # e.g., {"amount_gt": 10000}
    filters: Optional[Dict[str, Any]] = None  # e.g., {"project": "enterprise"}

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "type": "invoice.paid",
            "conditions": {"amount_gt": 50000},
            "filters": {"min_amount": 10000}
        }
    })


class WorkflowAction(BaseModel):
    """Action definition for a workflow."""
    type: WorkflowActionType
    name: str
    config: Dict[str, Any]  # Action-specific configuration
    order: int = 0
    retry_count: int = 0
    delay_seconds: Optional[int] = None  # Delay before executing this action

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "type": "send_email",
            "name": "Send Thank You Email",
            "config": {
                "to": "{{client_email}}",
                "subject": "Thank you for your payment!",
                "body": "Dear {{client_name}}, thank you for your payment of {{amount}}."
            },
            "order": 1,
            "retry_count": 3,
            "delay_seconds": None
        }
    })


class Workflow(BaseModel):
    """Complete workflow definition."""
    id: str
    name: str
    description: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.DRAFT
    trigger: WorkflowTrigger
    actions: List[WorkflowAction]
    created_at: str
    updated_at: str
    created_by: Optional[str] = None
    execution_count: int = 0
    last_executed_at: Optional[str] = None
    tags: List[str] = []

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "WF-001",
            "name": "Invoice Paid → Thank You Flow",
            "description": "When an invoice is paid, create receipt, notify sales, and send thank you email.",
            "status": "active",
            "trigger": {
                "type": "invoice.paid",
                "conditions": {"amount_gt": 10000}
            },
            "actions": [
                {"type": "create_receipt", "name": "Generate Receipt", "config": {}, "order": 0},
                {"type": "notify_sales", "name": "Notify Account Manager", "config": {"channel": "slack"}, "order": 1},
                {"type": "send_email", "name": "Send Thank You", "config": {"template": "thank_you"}, "order": 2}
            ],
            "created_at": "2026-08-01T10:00:00",
            "updated_at": "2026-08-07T14:30:00",
            "created_by": "manager@example.com",
            "execution_count": 15,
            "last_executed_at": "2026-08-07T09:15:00",
            "tags": ["finance", "automation"]
        }
    })


class WorkflowExecution(BaseModel):
    """Record of a workflow execution."""
    id: str
    workflow_id: str
    workflow_name: str
    status: WorkflowExecutionStatus = WorkflowExecutionStatus.PENDING
    triggered_by: str  # Event that triggered the execution
    trigger_data: Dict[str, Any]  # Data from the triggering event
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    action_results: List[Dict[str, Any]] = []  # Results from each action
    error_message: Optional[str] = None
    retry_count: int = 0

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "EXEC-001",
            "workflow_id": "WF-001",
            "workflow_name": "Invoice Paid → Thank You Flow",
            "status": "completed",
            "triggered_by": "invoice.paid",
            "trigger_data": {"invoice_id": "INV-123", "amount": 50000},
            "started_at": "2026-08-07T09:15:00",
            "completed_at": "2026-08-07T09:15:45",
            "action_results": [
                {"action": "create_receipt", "status": "success", "result": {"receipt_id": "RCP-456"}},
                {"action": "notify_sales", "status": "success"},
                {"action": "send_email", "status": "success", "result": {"message_id": "MSG-789"}}
            ],
            "error_message": None,
            "retry_count": 0
        }
    })


class CreateWorkflowRequest(BaseModel):
    """Request model for creating a workflow."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    trigger: WorkflowTrigger
    actions: List[WorkflowAction]
    status: WorkflowStatus = WorkflowStatus.DRAFT
    tags: List[str] = []

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "New Client Onboarding Flow",
            "description": "Automated workflow for new customer onboarding.",
            "trigger": {
                "type": "customer.created",
                "conditions": {"segment": "enterprise"}
            },
            "actions": [
                {"type": "create_task", "name": "Schedule Onboarding Call", "config": {"priority": "high", "due_days": 3}, "order": 0},
                {"type": "send_email", "name": "Welcome Email", "config": {"template": "welcome"}, "order": 1},
                {"type": "notify_slack", "name": "Notify Team", "config": {"channel": "#onboarding"}, "order": 2}
            ],
            "status": "draft",
            "tags": ["onboarding", "automation"]
        }
    })


class UpdateWorkflowRequest(BaseModel):
    """Request model for updating a workflow."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    trigger: Optional[WorkflowTrigger] = None
    actions: Optional[List[WorkflowAction]] = None
    status: Optional[WorkflowStatus] = None
    tags: Optional[List[str]] = None


class ExecuteWorkflowRequest(BaseModel):
    """Request model for manually triggering a workflow."""
    trigger_data: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "trigger_data": {
                "invoice_id": "INV-123",
                "amount": 50000,
                "client_email": "client@example.com"
            }
        }
    })


class WorkflowListResponse(BaseModel):
    """Paginated workflow list response."""
    workflows: List[Workflow]
    total: int
    page: int
    page_size: int
    total_pages: int


class WorkflowExecutionListResponse(BaseModel):
    """Paginated workflow execution list response."""
    executions: List[WorkflowExecution]
    total: int
    page: int
    page_size: int
    total_pages: int


class WorkflowStats(BaseModel):
    """Statistics for workflows."""
    total_workflows: int
    active_workflows: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time_seconds: float
    most_executed_workflow: Optional[str]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_workflows": 12,
            "active_workflows": 8,
            "total_executions": 156,
            "successful_executions": 148,
            "failed_executions": 8,
            "avg_execution_time_seconds": 12.5,
            "most_executed_workflow": "Invoice Paid → Thank You Flow"
        }
    })