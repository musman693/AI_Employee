"""
workflow.py — Workflow Automation Engine API endpoints.

Endpoints:
  POST   /api/v1/workflow/                        Create a new workflow
  GET    /api/v1/workflow/                        List all workflows
  GET    /api/v1/workflow/{workflow_id}           Get workflow details
  PUT    /api/v1/workflow/{workflow_id}           Update a workflow
  DELETE /api/v1/workflow/{workflow_id}           Delete a workflow
  POST   /api/v1/workflow/{workflow_id}/execute   Manually trigger a workflow
  GET    /api/v1/workflow/{workflow_id}/executions List workflow executions
  GET    /api/v1/workflow/stats                   Get workflow statistics
  POST   /api/v1/workflow/events                  Publish an event to trigger workflows

Note: Workflows are stored in-memory. Connect to PostgreSQL for persistence.
      Actions use mock implementations; connect to real services for production.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional

from app.models.workflow_models import (
    Workflow, WorkflowExecution, WorkflowStatus,
    CreateWorkflowRequest, UpdateWorkflowRequest, ExecuteWorkflowRequest,
    WorkflowListResponse, WorkflowExecutionListResponse, WorkflowStats,
)
from app.services import workflow_engine

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Static routes MUST come before dynamic {workflow_id} routes
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# POST / — Create a new workflow
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=Workflow, status_code=201,
             summary="Workflow Automation — create a new workflow")
def create_workflow(payload: CreateWorkflowRequest):
    """
    Create a new workflow with trigger definition and action chain.
    The workflow is created in draft status by default.
    Set status to 'active' to enable automatic triggering.
    """
    workflow_data = {
        "name": payload.name,
        "description": payload.description,
        "status": payload.status,
        "trigger": payload.trigger.model_dump(),
        "actions": [action.model_dump() for action in payload.actions],
        "tags": payload.tags,
    }

    workflow = workflow_engine.create_workflow(workflow_data)
    return workflow


# ─────────────────────────────────────────────────────────────────────────────
# GET /stats — Get workflow statistics (BEFORE /{workflow_id})
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/stats", response_model=WorkflowStats,
            summary="Workflow Automation — get workflow statistics")
def get_workflow_stats():
    """
    Get summary statistics about workflows including total count,
    active workflows, execution counts, and success rates.
    """
    return workflow_engine.get_workflow_stats()


# ─────────────────────────────────────────────────────────────────────────────
# POST /events — Publish an event to trigger workflows (BEFORE /{workflow_id})
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/events",
             summary="Workflow Automation — publish event to trigger workflows")
def publish_event(event_type: str = Body(...), event_data: dict = Body(...)):
    """
    Publish an event that will trigger all matching active workflows.
    Event types include: invoice.paid, invoice.sent, task.completed, etc.
    Returns list of executions triggered by this event.
    """
    executions = workflow_engine.publish_event(event_type, event_data)
    return {
        "event_type": event_type,
        "workflows_triggered": len(executions),
        "executions": executions,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET / — List all workflows
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=WorkflowListResponse,
            summary="Workflow Automation — list all workflows")
def list_workflows(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[WorkflowStatus] = Query(None, description="Filter by status"),
    trigger_type: Optional[str] = Query(None, description="Filter by trigger type"),
):
    """
    List workflows with pagination and optional filters for status and trigger type.
    """
    workflows, total, page, page_size = workflow_engine.list_workflows(
        status=status.value if status else None,
        trigger_type=trigger_type,
        page=page,
        page_size=page_size,
    )

    return WorkflowListResponse(
        workflows=workflows,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if page_size > 0 else 0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /{workflow_id} — Get workflow details
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/{workflow_id}", response_model=Workflow,
            summary="Workflow Automation — get workflow details")
def get_workflow(workflow_id: str):
    """Get detailed information about a specific workflow by ID."""
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return workflow


# ─────────────────────────────────────────────────────────────────────────────
# PUT /{workflow_id} — Update a workflow
# ─────────────────────────────────────────────────────────────────────────────
@router.put("/{workflow_id}", response_model=Workflow,
            summary="Workflow Automation — update a workflow")
def update_workflow(workflow_id: str, payload: UpdateWorkflowRequest):
    """
    Update a workflow's name, description, trigger, actions, or status.
    Fields not provided will remain unchanged.
    """
    updates = payload.model_dump(exclude_unset=True)
    # Convert enums to values
    if "trigger" in updates and updates["trigger"] is not None:
        updates["trigger"] = updates["trigger"].model_dump()
    if "actions" in updates and updates["actions"] is not None:
        updates["actions"] = [a.model_dump() for a in updates["actions"]]

    workflow = workflow_engine.update_workflow(workflow_id, updates)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return workflow


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /{workflow_id} — Delete a workflow
# ─────────────────────────────────────────────────────────────────────────────
@router.delete("/{workflow_id}", status_code=204,
               summary="Workflow Automation — delete a workflow")
def delete_workflow(workflow_id: str):
    """Delete a workflow by ID. This action cannot be undone."""
    if not workflow_engine.delete_workflow(workflow_id):
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")


# ─────────────────────────────────────────────────────────────────────────────
# POST /{workflow_id}/execute — Manually trigger a workflow
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/{workflow_id}/execute", response_model=WorkflowExecution,
             summary="Workflow Automation — manually trigger a workflow")
def execute_workflow(workflow_id: str, payload: ExecuteWorkflowRequest):
    """
    Manually trigger a workflow execution with the provided trigger data.
    Useful for testing workflows or triggering them from external systems.
    """
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")

    execution = workflow_engine.execute_workflow(
        workflow,
        payload.trigger_data,
        triggered_by="manual"
    )
    return execution


# ─────────────────────────────────────────────────────────────────────────────
# GET /{workflow_id}/executions — List workflow executions
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/{workflow_id}/executions", response_model=WorkflowExecutionListResponse,
            summary="Workflow Automation — list workflow executions")
def list_workflow_executions(
    workflow_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by execution status"),
):
    """
    List execution history for a specific workflow with pagination.
    """
    # Verify workflow exists
    if not workflow_engine.get_workflow(workflow_id):
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")

    executions, total, page, page_size = workflow_engine.list_executions(
        workflow_id=workflow_id,
        status=status,
        page=page,
        page_size=page_size,
    )

    return WorkflowExecutionListResponse(
        executions=executions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if page_size > 0 else 0,
    )
