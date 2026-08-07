"""
test_workflow.py — Unit tests for the Workflow Automation endpoints.

Tests:
  - Create workflow (basic + with all fields)
  - List workflows (empty state + with workflows, pagination, filters)
  - Get workflow details (found + not found)
  - Update workflow
  - Delete workflow
  - Execute workflow manually
  - List workflow executions
  - Get workflow stats
  - Publish event to trigger workflows
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ── Helper: create a workflow ────────────────────────────────────────────────
def _create_workflow(
    name="Test Workflow",
    trigger_type="manual",
    status="draft",
    actions=None
):
    if actions is None:
        actions = [
            {
                "type": "send_email",
                "name": "Test Email",
                "config": {"to": "test@example.com", "subject": "Test", "body": "Hello"},
                "order": 0
            }
        ]

    payload = {
        "name": name,
        "description": "Test workflow description",
        "trigger": {
            "type": trigger_type,
            "conditions": None
        },
        "actions": actions,
        "status": status,
        "tags": ["test"],
    }
    return client.post("/api/v1/workflow/", json=payload)


# ─────────────────────────────────────────────────────────────────────────────
class TestCreateWorkflow:
    def test_create_workflow_returns_201(self):
        resp = _create_workflow("Build Automation")
        assert resp.status_code == 201

    def test_create_workflow_has_id(self):
        resp = _create_workflow("Build Automation")
        assert "id" in resp.json()
        assert resp.json()["id"].startswith("WF-")

    def test_create_workflow_with_all_fields(self):
        payload = {
            "name": "Invoice Paid Flow",
            "description": "Automated workflow for paid invoices",
            "trigger": {
                "type": "invoice.paid",
                "conditions": {"amount_gt": 10000}
            },
            "actions": [
                {"type": "create_receipt", "name": "Generate Receipt", "config": {}, "order": 0},
                {"type": "notify_sales", "name": "Notify Sales", "config": {"channel": "slack"}, "order": 1},
                {"type": "send_email", "name": "Thank You Email", "config": {"to": "{{client_email}}", "subject": "Thank you!", "body": "Thanks for payment."}, "order": 2}
            ],
            "status": "active",
            "tags": ["finance", "automation"],
        }
        resp = client.post("/api/v1/workflow/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Invoice Paid Flow"
        assert data["status"] == "active"
        assert len(data["actions"]) == 3

    def test_create_workflow_default_status(self):
        payload = {
            "name": "Default Status Workflow",
            "trigger": {"type": "manual"},
            "actions": [{"type": "send_email", "name": "Test", "config": {}}]
        }
        resp = client.post("/api/v1/workflow/", json=payload)
        assert resp.status_code == 201
        assert resp.json()["status"] == "draft"

    def test_create_workflow_name_required(self):
        resp = client.post("/api/v1/workflow/", json={})
        assert resp.status_code == 422

    def test_create_workflow_trigger_required(self):
        payload = {
            "name": "No Trigger",
            "actions": [{"type": "send_email", "name": "Test", "config": {}}]
        }
        resp = client.post("/api/v1/workflow/", json=payload)
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
class TestListWorkflows:
    def test_list_workflows_empty_returns_200(self):
        resp = client.get("/api/v1/workflow/")
        assert resp.status_code == 200

    def test_list_workflows_schema_fields(self):
        resp = client.get("/api/v1/workflow/")
        data = resp.json()
        required_fields = ["workflows", "total", "page", "page_size", "total_pages"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_list_workflows_with_workflows(self):
        # Create a few workflows
        _create_workflow("Workflow 1")
        _create_workflow("Workflow 2")
        _create_workflow("Workflow 3")

        resp = client.get("/api/v1/workflow/")
        data = resp.json()
        assert data["total"] >= 3

    def test_list_workflows_pagination(self):
        resp = client.get("/api/v1/workflow/?page=1&page_size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_list_workflows_filter_by_status(self):
        resp = client.get("/api/v1/workflow/?status=draft")
        assert resp.status_code == 200

    def test_list_workflows_filter_by_trigger_type(self):
        resp = client.get("/api/v1/workflow/?trigger_type=manual")
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
class TestGetWorkflow:
    def test_get_workflow_not_found(self):
        resp = client.get("/api/v1/workflow/WF-999")
        assert resp.status_code == 404

    def test_get_workflow_found(self):
        create_resp = _create_workflow("Get Test Workflow")
        workflow_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/workflow/{workflow_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get Test Workflow"


# ─────────────────────────────────────────────────────────────────────────────
class TestUpdateWorkflow:
    def test_update_workflow(self):
        create_resp = _create_workflow("Update Test Workflow")
        workflow_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/workflow/{workflow_id}", json={
            "name": "Updated Workflow Name",
            "status": "active",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Workflow Name"
        assert data["status"] == "active"

    def test_update_workflow_partial(self):
        create_resp = _create_workflow("Partial Update Workflow")
        workflow_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/workflow/{workflow_id}", json={
            "description": "New description"
        })
        assert resp.status_code == 200
        # Name should remain unchanged
        assert resp.json()["name"] == "Partial Update Workflow"

    def test_update_workflow_not_found(self):
        resp = client.put("/api/v1/workflow/WF-999", json={"name": "Test"})
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestDeleteWorkflow:
    def test_delete_workflow(self):
        create_resp = _create_workflow("Delete Me")
        workflow_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/workflow/{workflow_id}")
        assert resp.status_code == 204

        # Verify it's gone
        get_resp = client.get(f"/api/v1/workflow/{workflow_id}")
        assert get_resp.status_code == 404

    def test_delete_workflow_not_found(self):
        resp = client.delete("/api/v1/workflow/WF-999")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestExecuteWorkflow:
    def test_execute_workflow(self):
        create_resp = _create_workflow("Execute Me")
        workflow_id = create_resp.json()["id"]

        resp = client.post(f"/api/v1/workflow/{workflow_id}/execute", json={
            "trigger_data": {"test_key": "test_value"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["workflow_id"] == workflow_id
        assert data["status"] in ["completed", "failed", "running"]

    def test_execute_workflow_not_found(self):
        resp = client.post("/api/v1/workflow/WF-999/execute", json={})
        assert resp.status_code == 404

    def test_execute_workflow_has_execution_id(self):
        create_resp = _create_workflow("Execution ID Test")
        workflow_id = create_resp.json()["id"]

        resp = client.post(f"/api/v1/workflow/{workflow_id}/execute", json={
            "trigger_data": {}
        })
        assert resp.status_code == 200
        assert "id" in resp.json()
        assert resp.json()["id"].startswith("EXEC-")


# ─────────────────────────────────────────────────────────────────────────────
class TestListWorkflowExecutions:
    def test_list_executions_empty(self):
        create_resp = _create_workflow("Empty Executions")
        workflow_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/workflow/{workflow_id}/executions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_list_executions_after_execute(self):
        create_resp = _create_workflow("With Executions")
        workflow_id = create_resp.json()["id"]

        # Execute the workflow
        client.post(f"/api/v1/workflow/{workflow_id}/execute", json={
            "trigger_data": {}
        })

        resp = client.get(f"/api/v1/workflow/{workflow_id}/executions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_list_executions_not_found(self):
        resp = client.get("/api/v1/workflow/WF-999/executions")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestWorkflowStats:
    def test_get_stats_returns_200(self):
        resp = client.get("/api/v1/workflow/stats")
        assert resp.status_code == 200

    def test_get_stats_schema_fields(self):
        resp = client.get("/api/v1/workflow/stats")
        data = resp.json()
        required_fields = [
            "total_workflows", "active_workflows", "total_executions",
            "successful_executions", "failed_executions",
            "avg_execution_time_seconds", "most_executed_workflow"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


# ─────────────────────────────────────────────────────────────────────────────
class TestPublishEvent:
    def test_publish_event_returns_200(self):
        resp = client.post("/api/v1/workflow/events", json={
            "event_type": "invoice.paid",
            "event_data": {"invoice_id": "INV-123", "amount": 50000}
        })
        assert resp.status_code == 200

    def test_publish_event_response_structure(self):
        resp = client.post("/api/v1/workflow/events", json={
            "event_type": "task.completed",
            "event_data": {"task_id": "TASK-123"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "event_type" in data
        assert "workflows_triggered" in data
        assert "executions" in data

    def test_publish_event_triggers_matching_workflows(self):
        # Create an active workflow with manual trigger
        create_resp = _create_workflow("Event Trigger Test", trigger_type="manual", status="active")
        workflow_id = create_resp.json()["id"]

        # Publish a manual event
        resp = client.post("/api/v1/workflow/events", json={
            "event_type": "manual",
            "event_data": {"source": "test"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["event_type"] == "manual"