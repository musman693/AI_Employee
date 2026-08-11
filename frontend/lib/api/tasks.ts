import type { Task, TaskCreate, Workflow, WorkflowCreate } from "@/types/api";
import { apiClient } from "./base";

type BackendTask = Omit<Task, "status" | "assignee"> & {
  status: "todo" | "in_progress" | "in_review" | "completed" | "cancelled";
  assigned_to?: string;
  assignee?: string;
};

export const tasksApi = {
  listTasks: async () => {
    const response = await apiClient.get<{ tasks: BackendTask[] }>('/api/v1/task');
    return response.data.tasks.map(normalizeTask);
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
  createTask: async (payload: TaskCreate) => {
    const response = await apiClient.post<BackendTask>('/api/v1/task/', payload);
    return normalizeTask(response.data);
  },
  deleteTask: async (taskId: string) => apiClient.delete(`/api/v1/task/${taskId}`),
  assignTask: async (taskId: string, assignedTo: string) => {
    const response = await apiClient.post<BackendTask>(`/api/v1/task/${taskId}/assign`, { assigned_to: assignedTo });
    return normalizeTask(response.data);
  },
  listWorkflows: async () => {
    const response = await apiClient.get<{ workflows: Workflow[] }>('/api/v1/workflow');
    return response.data.workflows;
  },
  saveWorkflow: async (payload: WorkflowCreate) => {
    const response = await apiClient.post<Workflow>('/api/v1/workflow/', payload);
    return response.data;
  },
  updateWorkflow: async (id: string, payload: Partial<WorkflowCreate>) => {
    const response = await apiClient.put<Workflow>(`/api/v1/workflow/${id}`, payload);
    return response.data;
  },
  deleteWorkflow: async (id: string) => apiClient.delete(`/api/v1/workflow/${id}`),
  executeWorkflow: async (id: string) => {
    const response = await apiClient.post<{ id: string; status: string }>(`/api/v1/workflow/${id}/execute`, { trigger_data: {} });
    return response.data;
  },
};

function normalizeTask(task: BackendTask): Task { return { ...task, assignee: task.assigned_to ?? task.assignee ?? "", status: task.status === "completed" || task.status === "cancelled" ? "done" : task.status === "in_review" ? "in_progress" : task.status } as Task; }
