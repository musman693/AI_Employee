import { beforeEach, describe, expect, it, vi } from "vitest";

const { get, post, patch, put, del } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), patch: vi.fn(), put: vi.fn(), del: vi.fn() }));
vi.mock("@/lib/api/base", () => ({ apiClient: { get, post, patch, put, delete: del } }));

import { tasksApi } from "../tasks";

const backendTask = { id: "TASK-1", title: "Ship dashboard", description: null, priority: "high", status: "completed", assigned_to: "dev@example.com", due_date: "2026-08-20", project: "OS", tags: [], progress_percent: 100, ai_suggestions: null, ai_reminder_enabled: true };

describe("tasksApi", () => {
  beforeEach(() => { get.mockReset(); post.mockReset(); patch.mockReset(); put.mockReset(); del.mockReset(); });

  it("normalizes backend status and assignee", async () => {
    get.mockResolvedValue({ data: { tasks: [backendTask] } });
    const tasks = await tasksApi.listTasks();
    expect(tasks[0]).toMatchObject({ status: "done", assignee: "dev@example.com", priority: "high" });
  });

  it("maps completed UI status to the backend enum", async () => {
    patch.mockResolvedValue({ data: backendTask });
    await tasksApi.updateTask("TASK-1", { status: "done" });
    expect(patch).toHaveBeenCalledWith("/api/v1/task/TASK-1/status", { status: "completed" });
  });
});
