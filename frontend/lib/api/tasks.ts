import type { Task, Workflow } from "@/types/api";
import { apiClient } from "./base";

export const tasksApi = {
  listTasks: async () => {
    const response = await apiClient.get<Task[]>('/tasks');
    return response.data;
  },
  updateTask: async (taskId: string, payload: Partial<Task>) => {
    const response = await apiClient.put<Task>(`/tasks/${taskId}`, payload);
    return response.data;
  },
  listWorkflows: async () => {
    const response = await apiClient.get<Workflow[]>('/workflows');
    return response.data;
  },
  saveWorkflow: async (payload: Workflow) => {
    const response = await apiClient.post<Workflow>('/workflows', payload);
    return response.data;
  },
};
