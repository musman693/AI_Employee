import type { Task, Workflow } from "@/types/api";
import { apiClient } from "./base";

type BackendTask = Omit<Task, "status" | "assignee"> & {
  status: "todo" | "in_progress" | "in_review" | "completed" | "cancelled";
  assigned_to?: string;
  assignee?: string;
};

export const tasksApi = {
  listTasks: async () => {
    const response = await apiClient.get<{ tasks: BackendTask[] }>('/api/v1/task');
    return response.data.tasks.map((task) => ({
      ...task,
      assignee: task.assigned_to ?? task.assignee ?? "",
      status: task.status === "completed" || task.status === "cancelled" ? "done" : task.status === "in_review" ? "in_progress" : task.status,
    })) as Task[];
  },
  updateTask: async (taskId: string, payload: Partial<Task>) => {
    if (payload.status) {
      const backendStatus = payload.status === "done" ? "completed" : payload.status;
      const response = await apiClient.patch<Task>(`/api/v1/task/${taskId}/status`, { status: backendStatus });
      return { ...response.data, status: payload.status };
    }
    const response = await apiClient.put<Task>(`/api/v1/task/${taskId}`, payload);
    return response.data;
  },
  listWorkflows: async () => {
    const response = await apiClient.get<{ workflows: Workflow[] }>('/api/v1/workflow');
    return response.data.workflows;
  },
  saveWorkflow: async (payload: Workflow) => {
    const actions = (payload.actions as unknown[]).map((action, index) => {
      const item = typeof action === "string" ? { type: action, payload: {} } : action as { type?: string; payload?: Record<string, unknown> };
      return { type: item.type ?? "create_task", name: item.type ?? `Action ${index + 1}`, config: item.payload ?? {}, order: index };
    });
    const response = await apiClient.post<Workflow>('/api/v1/workflow', {
      name: payload.name,
      trigger: { type: payload.trigger, conditions: {} },
      actions,
    });
    return response.data;
  },
};
