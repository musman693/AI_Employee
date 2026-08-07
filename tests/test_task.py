"""
test_task.py — Unit tests for the AI Task Manager endpoints.

Tests:
  - Create task (basic + with all fields)
  - List tasks (empty state + with tasks, pagination, filters)
  - Get task details (found + not found)
  - Update task
  - Update task status/progress
  - Delete task
  - Assign task
  - Get my tasks
  - Get overdue tasks
  - Get task summary
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import date, timedelta

client = TestClient(app)

# ── Helper: create a task ─────────────────────────────────────────────────────
def _create_task(title="Test Task", priority="medium", due_date=None, assigned_to=None):
    payload = {"title": title, "priority": priority}
    if due_date:
        payload["due_date"] = due_date
    if assigned_to:
        payload["assigned_to"] = assigned_to
    return client.post("/api/v1/task/", json=payload)


# ─────────────────────────────────────────────────────────────────────────────
class TestCreateTask:
    def test_create_task_returns_201(self):
        resp = _create_task("Build AI Feature")
        assert resp.status_code == 201

    def test_create_task_has_id(self):
        resp = _create_task("Build AI Feature")
        assert "id" in resp.json()
        assert resp.json()["id"].startswith("TASK-")

    def test_create_task_with_all_fields(self):
        future_date = (date.today() + timedelta(days=30)).isoformat()
        payload = {
            "title": "Complete Project",
            "description": "Finish all deliverables",
            "priority": "high",
            "assigned_to": "developer@example.com",
            "due_date": future_date,
            "estimated_hours": 40.0,
            "tags": ["backend", "urgent"],
            "project": "AI Employee OS",
            "ai_reminder_enabled": True,
        }
        resp = client.post("/api/v1/task/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Complete Project"
        assert data["priority"] == "high"
        assert data["assigned_to"] == "developer@example.com"
        assert data["tags"] == ["backend", "urgent"]
        assert data["ai_reminder_enabled"] is True

    def test_create_task_default_values(self):
        resp = _create_task("Simple Task")
        data = resp.json()
        assert data["status"] == "todo"
        assert data["priority"] == "medium"
        assert data["progress_percent"] == 0

    def test_create_task_title_required(self):
        resp = client.post("/api/v1/task/", json={})
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
class TestListTasks:
    def test_list_tasks_empty_returns_200(self):
        resp = client.get("/api/v1/task/")
        assert resp.status_code == 200

    def test_list_tasks_schema_fields(self):
        resp = client.get("/api/v1/task/")
        data = resp.json()
        required_fields = ["tasks", "total", "page", "page_size", "total_pages"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_list_tasks_with_tasks(self):
        # Create a few tasks
        _create_task("Task 1")
        _create_task("Task 2")
        _create_task("Task 3")

        resp = client.get("/api/v1/task/")
        data = resp.json()
        assert data["total"] >= 3
        assert len(data["tasks"]) >= 3

    def test_list_tasks_pagination(self):
        resp = client.get("/api/v1/task/?page=1&page_size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_list_tasks_filter_by_status(self):
        resp = client.get("/api/v1/task/?status=todo")
        assert resp.status_code == 200

    def test_list_tasks_filter_by_priority(self):
        resp = client.get("/api/v1/task/?priority=high")
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
class TestGetTask:
    def test_get_task_not_found(self):
        resp = client.get("/api/v1/task/TASK-999")
        assert resp.status_code == 404

    def test_get_task_found(self):
        create_resp = _create_task("Get Test Task")
        task_id = create_resp.json()["id"]
        resp = client.get(f"/api/v1/task/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Get Test Task"


# ─────────────────────────────────────────────────────────────────────────────
class TestUpdateTask:
    def test_update_task(self):
        create_resp = _create_task("Update Test Task")
        task_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/task/{task_id}", json={
            "title": "Updated Task Title",
            "priority": "urgent",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Task Title"
        assert data["priority"] == "urgent"

    def test_update_task_partial(self):
        create_resp = _create_task("Partial Update Task")
        task_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/task/{task_id}", json={
            "description": "New description"
        })
        assert resp.status_code == 200
        # Title should remain unchanged
        assert resp.json()["title"] == "Partial Update Task"

    def test_update_task_not_found(self):
        resp = client.put("/api/v1/task/TASK-999", json={"title": "Test"})
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestUpdateTaskStatus:
    def test_update_status(self):
        create_resp = _create_task("Status Update Task")
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/task/{task_id}/status", json={
            "status": "in_progress",
            "progress_percent": 50,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "in_progress"
        assert data["progress_percent"] == 50

    def test_update_status_to_completed(self):
        create_resp = _create_task("Complete Me")
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/task/{task_id}/status", json={
            "status": "completed",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "completed"
        assert data["progress_percent"] == 100
        assert data["completed_at"] is not None

    def test_update_status_invalid_progress(self):
        create_resp = _create_task("Invalid Progress")
        task_id = create_resp.json()["id"]

        resp = client.patch(f"/api/v1/task/{task_id}/status", json={
            "progress_percent": 150  # Invalid: > 100
        })
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
class TestDeleteTask:
    def test_delete_task(self):
        create_resp = _create_task("Delete Me")
        task_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/task/{task_id}")
        assert resp.status_code == 204

        # Verify it's gone
        get_resp = client.get(f"/api/v1/task/{task_id}")
        assert get_resp.status_code == 404

    def test_delete_task_not_found(self):
        resp = client.delete("/api/v1/task/TASK-999")
        assert resp.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
class TestAssignTask:
    def test_assign_task(self):
        create_resp = _create_task("Assign Me")
        task_id = create_resp.json()["id"]

        resp = client.post(f"/api/v1/task/{task_id}/assign", json={
            "assigned_to": "developer@example.com",
            "assigned_by": "manager@example.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["assigned_to"] == "developer@example.com"
        assert data["assigned_by"] == "manager@example.com"

    def test_assign_task_missing_assigned_to(self):
        create_resp = _create_task("Assign Me")
        task_id = create_resp.json()["id"]

        resp = client.post(f"/api/v1/task/{task_id}/assign", json={})
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
class TestMyTasks:
    def test_get_my_tasks(self):
        # Create a task assigned to a user
        _create_task("My Task", assigned_to="user@example.com")

        resp = client.get("/api/v1/task/my-tasks?user_email=user@example.com")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_get_my_tasks_missing_email(self):
        resp = client.get("/api/v1/task/my-tasks")
        assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
class TestOverdueTasks:
    def test_get_overdue_tasks(self):
        # Create a task with a past due date
        past_date = (date.today() - timedelta(days=7)).isoformat()
        _create_task("Overdue Task", due_date=past_date)

        resp = client.get("/api/v1/task/overdue")
        assert resp.status_code == 200
        data = resp.json()
        # Should include the overdue task
        assert data["total"] >= 1

    def test_get_overdue_tasks_empty(self):
        resp = client.get("/api/v1/task/overdue")
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
class TestTaskSummary:
    def test_get_summary(self):
        resp = client.get("/api/v1/task/summary")
        assert resp.status_code == 200

    def test_get_summary_schema_fields(self):
        resp = client.get("/api/v1/task/summary")
        data = resp.json()
        required_fields = [
            "total_tasks", "completed_tasks", "in_progress_tasks",
            "overdue_tasks", "my_tasks", "high_priority_pending"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_get_summary_with_user_filter(self):
        resp = client.get("/api/v1/task/summary?user_email=user@example.com")
        assert resp.status_code == 200