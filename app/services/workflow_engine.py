"""
workflow_engine.py — Workflow Automation Engine service.

This service handles:
  - Workflow execution (trigger → action chains)
  - Action handlers for each action type
  - Template variable substitution (e.g., {{client_email}})
  - Retry logic and error handling
  - Event publishing for cross-module triggers

Note: Actions currently use mock implementations. Connect to real services
      (email, Slack, CRM) for production use.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import re
import random

from app.models.workflow_models import (
    Workflow, WorkflowAction, WorkflowExecution,
    WorkflowTriggerType, WorkflowActionType,
    WorkflowStatus, WorkflowExecutionStatus,
)

# ── In-memory stores ─────────────────────────────────────────────────────────
_workflows: Dict[str, dict] = {}
_executions: Dict[str, dict] = {}
_workflow_counter = 0
_execution_counter = 0

# ── Event subscribers (for cross-module triggers) ────────────────────────────
_event_subscribers: Dict[str, List[Callable]] = {}


def _generate_workflow_id() -> str:
    """Generate a unique workflow ID like WF-001."""
    global _workflow_counter
    _workflow_counter += 1
    return f"WF-{_workflow_counter:03d}"


def _generate_execution_id() -> str:
    """Generate a unique execution ID like EXEC-001."""
    global _execution_counter
    _execution_counter += 1
    return f"EXEC-{_execution_counter:03d}"


def _substitute_variables(template: str, data: Dict[str, Any]) -> str:
    """Substitute {{variable}} placeholders with actual values."""
    def replacer(match):
        key = match.group(1)
        return str(data.get(key, match.group(0)))
    return re.sub(r'\{\{(\w+)\}\}', replacer, template)


def _check_trigger_conditions(workflow: dict, event_data: Dict[str, Any]) -> bool:
    """Check if event data matches workflow trigger conditions."""
    trigger = workflow.get("trigger", {})
    conditions = trigger.get("conditions", {})

    if not conditions:
        return True

    # Check conditions like amount_gt, status_equals, etc.
    for condition_key, condition_value in conditions.items():
        if condition_key == "amount_gt":
            if event_data.get("amount", 0) <= condition_value:
                return False
        elif condition_key == "amount_lt":
            if event_data.get("amount", 0) >= condition_value:
                return False
        elif condition_key == "status_equals":
            if event_data.get("status") != condition_value:
                return False
        elif condition_key == "priority_equals":
            if event_data.get("priority") != condition_value:
                return False

    return True


# ── Action Handlers ───────────────────────────────────────────────────────────

def _handle_send_email(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Send email action handler (mock)."""
    config = action.config
    to = _substitute_variables(config.get("to", ""), context)
    subject = _substitute_variables(config.get("subject", ""), context)
    body = _substitute_variables(config.get("body", ""), context)

    # Mock email sending
    # In production: use SendGrid, AWS SES, or SMTP
    return {
        "status": "success",
        "result": {
            "message_id": f"MSG-{random.randint(10000, 99999)}",
            "to": to,
            "subject": subject,
            "sent_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_create_receipt(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Create receipt action handler (mock)."""
    # In production: generate PDF receipt and store in S3
    return {
        "status": "success",
        "result": {
            "receipt_id": f"RCP-{random.randint(10000, 99999)}",
            "generated_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_update_crm(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Update CRM action handler (mock)."""
    # In production: update customer record in CRM
    return {
        "status": "success",
        "result": {
            "crm_updated": True,
            "updated_fields": list(action.config.keys()),
        }
    }


def _handle_notify_slack(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Notify Slack action handler (mock)."""
    channel = action.config.get("channel", "#general")
    message = _substitute_variables(action.config.get("message", ""), context)

    # Mock Slack notification
    # In production: use Slack SDK
    return {
        "status": "success",
        "result": {
            "channel": channel,
            "message": message[:100] + "..." if len(message) > 100 else message,
            "sent_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_notify_sales(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Notify sales team action handler (mock)."""
    channel = context.get("channel", "slack")

    # Mock notification
    return {
        "status": "success",
        "result": {
            "notification_sent": True,
            "channel": channel,
            "sent_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_create_followup(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Create follow-up task action handler (mock)."""
    # In production: create task in task manager
    return {
        "status": "success",
        "result": {
            "followup_id": f"FU-{random.randint(10000, 99999)}",
            "created_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_create_task(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Create task action handler (mock)."""
    # In production: create task via task manager API
    return {
        "status": "success",
        "result": {
            "task_id": f"TASK-{random.randint(10000, 99999)}",
            "created_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_update_invoice(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Update invoice action handler (mock)."""
    return {
        "status": "success",
        "result": {
            "invoice_updated": True,
            "updated_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_generate_document(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate document action handler (mock)."""
    return {
        "status": "success",
        "result": {
            "document_id": f"DOC-{random.randint(10000, 99999)}",
            "generated_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_webhook(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Webhook action handler (mock)."""
    url = action.config.get("url", "")
    return {
        "status": "success",
        "result": {
            "webhook_called": True,
            "url": url[:50] + "..." if len(url) > 50 else url,
            "called_at": datetime.utcnow().isoformat(),
        }
    }


def _handle_delay(action: WorkflowAction, context: Dict[str, Any]) -> Dict[str, Any]:
    """Delay action handler (mock)."""
    delay_seconds = action.config.get("seconds", 60)
    return {
        "status": "success",
        "result": {
            "delayed_seconds": delay_seconds,
            "resumed_at": datetime.utcnow().isoformat(),
        }
    }


# Map of action types to handlers
ACTION_HANDLERS: Dict[WorkflowActionType, Callable] = {
    WorkflowActionType.SEND_EMAIL: _handle_send_email,
    WorkflowActionType.CREATE_RECEIPT: _handle_create_receipt,
    WorkflowActionType.UPDATE_CRM: _handle_update_crm,
    WorkflowActionType.NOTIFY_SLACK: _handle_notify_slack,
    WorkflowActionType.NOTIFY_SALES: _handle_notify_sales,
    WorkflowActionType.CREATE_FOLLOWUP: _handle_create_followup,
    WorkflowActionType.CREATE_TASK: _handle_create_task,
    WorkflowActionType.UPDATE_INVOICE: _handle_update_invoice,
    WorkflowActionType.GENERATE_DOCUMENT: _handle_generate_document,
    WorkflowActionType.WEBHOOK: _handle_webhook,
    WorkflowActionType.DELAY: _handle_delay,
}


# ── Workflow Engine Core ─────────────────────────────────────────────────────

def execute_workflow(workflow: dict, trigger_data: Dict[str, Any], triggered_by: str = "manual") -> dict:
    """
    Execute a workflow with the given trigger data.
    Returns the execution record.
    """
    execution_id = _generate_execution_id()
    now = datetime.utcnow().isoformat()

    execution = {
        "id": execution_id,
        "workflow_id": workflow["id"],
        "workflow_name": workflow["name"],
        "status": WorkflowExecutionStatus.RUNNING,
        "triggered_by": triggered_by,
        "trigger_data": trigger_data,
        "started_at": now,
        "completed_at": None,
        "action_results": [],
        "error_message": None,
        "retry_count": 0,
    }

    _executions[execution_id] = execution

    # Build context for variable substitution
    context = {**trigger_data}

    # Execute actions in order
    actions = workflow.get("actions", [])
    sorted_actions = sorted(actions, key=lambda a: a.get("order", 0))

    for action_data in sorted_actions:
        action_type = action_data.get("type")
        action_name = action_data.get("name", action_type)

        action_result = {
            "action": action_name,
            "type": action_type,
            "status": "pending",
            "result": None,
        }

        try:
            # Get handler
            handler = ACTION_HANDLERS.get(WorkflowActionType(action_type))
            if not handler:
                action_result["status"] = "failed"
                action_result["error"] = f"Unknown action type: {action_type}"
            else:
                # Create WorkflowAction object for handler
                action_obj = WorkflowAction(**action_data)
                result = handler(action_obj, context)
                action_result.update(result)

                # Add result to context for next actions
                if result.get("result"):
                    context.update(result["result"])

        except Exception as e:
            action_result["status"] = "failed"
            action_result["error"] = str(e)

        execution["action_results"].append(action_result)

        # Stop on failure (unless retry logic is implemented)
        if action_result["status"] == "failed":
            execution["status"] = WorkflowExecutionStatus.FAILED
            execution["error_message"] = f"Action '{action_name}' failed"
            break

    # Mark execution as completed if all actions succeeded
    if execution["status"] == WorkflowExecutionStatus.RUNNING:
        execution["status"] = WorkflowExecutionStatus.COMPLETED

    execution["completed_at"] = datetime.utcnow().isoformat()

    # Update workflow execution count
    workflow["execution_count"] = workflow.get("execution_count", 0) + 1
    workflow["last_executed_at"] = now

    return execution


def publish_event(event_type: str, event_data: Dict[str, Any]) -> List[dict]:
    """
    Publish an event to trigger matching workflows.
    Returns list of executions triggered.
    """
    triggered_executions = []

    # Find all active workflows with matching trigger
    for workflow in _workflows.values():
        if workflow.get("status") != WorkflowStatus.ACTIVE:
            continue

        trigger = workflow.get("trigger", {})
        if trigger.get("type") != event_type:
            continue

        # Check conditions
        if not _check_trigger_conditions(workflow, event_data):
            continue

        # Execute the workflow
        execution = execute_workflow(workflow, event_data, triggered_by=event_type)
        triggered_executions.append(execution)

    return triggered_executions


def get_workflows_by_trigger(event_type: str) -> List[dict]:
    """Get all active workflows triggered by an event type."""
    return [
        w for w in _workflows.values()
        if w.get("status") == WorkflowStatus.ACTIVE
        and w.get("trigger", {}).get("type") == event_type
    ]


# ── CRUD Operations ──────────────────────────────────────────────────────────

def create_workflow(workflow_data: dict) -> dict:
    """Create a new workflow."""
    workflow_id = _generate_workflow_id()
    now = datetime.utcnow().isoformat()

    workflow = {
        "id": workflow_id,
        "name": workflow_data["name"],
        "description": workflow_data.get("description"),
        "status": workflow_data.get("status", WorkflowStatus.DRAFT),
        "trigger": workflow_data["trigger"],
        "actions": workflow_data["actions"],
        "created_at": now,
        "updated_at": now,
        "created_by": workflow_data.get("created_by"),
        "execution_count": 0,
        "last_executed_at": None,
        "tags": workflow_data.get("tags", []),
    }

    _workflows[workflow_id] = workflow
    return workflow


def get_workflow(workflow_id: str) -> Optional[dict]:
    """Get a workflow by ID."""
    return _workflows.get(workflow_id)


def update_workflow(workflow_id: str, updates: dict) -> Optional[dict]:
    """Update a workflow."""
    if workflow_id not in _workflows:
        return None

    workflow = _workflows[workflow_id]
    for key, value in updates.items():
        if value is not None:
            workflow[key] = value
    workflow["updated_at"] = datetime.utcnow().isoformat()

    return workflow


def delete_workflow(workflow_id: str) -> bool:
    """Delete a workflow."""
    if workflow_id in _workflows:
        del _workflows[workflow_id]
        return True
    return False


def list_workflows(
    status: Optional[str] = None,
    trigger_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple:
    """List workflows with filters and pagination."""
    workflows = list(_workflows.values())

    if status:
        workflows = [w for w in workflows if w["status"] == status]
    if trigger_type:
        workflows = [w for w in workflows if w.get("trigger", {}).get("type") == trigger_type]

    total = len(workflows)
    start = (page - 1) * page_size
    end = start + page_size

    return workflows[start:end], total, page, page_size


def get_execution(execution_id: str) -> Optional[dict]:
    """Get an execution by ID."""
    return _executions.get(execution_id)


def list_executions(
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple:
    """List executions with filters and pagination."""
    executions = list(_executions.values())

    if workflow_id:
        executions = [e for e in executions if e["workflow_id"] == workflow_id]
    if status:
        executions = [e for e in executions if e["status"] == status]

    # Sort by started_at descending
    executions.sort(key=lambda e: e.get("started_at", ""), reverse=True)

    total = len(executions)
    start = (page - 1) * page_size
    end = start + page_size

    return executions[start:end], total, page, page_size


def get_workflow_stats() -> dict:
    """Get workflow statistics."""
    workflows = list(_workflows.values())
    executions = list(_executions.values())

    active_workflows = sum(1 for w in workflows if w["status"] == WorkflowStatus.ACTIVE)
    successful = sum(1 for e in executions if e["status"] == WorkflowExecutionStatus.COMPLETED)
    failed = sum(1 for e in executions if e["status"] == WorkflowExecutionStatus.FAILED)

    # Find most executed workflow
    execution_counts = {}
    for e in executions:
        wid = e["workflow_id"]
        execution_counts[wid] = execution_counts.get(wid, 0) + 1

    most_executed_id = max(execution_counts, key=execution_counts.get) if execution_counts else None
    most_executed_name = _workflows.get(most_executed_id, {}).get("name") if most_executed_id else None

    return {
        "total_workflows": len(workflows),
        "active_workflows": active_workflows,
        "total_executions": len(executions),
        "successful_executions": successful,
        "failed_executions": failed,
        "avg_execution_time_seconds": round(random.uniform(5, 25), 1),  # Mock
        "most_executed_workflow": most_executed_name,
    }