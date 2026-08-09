import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "@/lib/api/tasks";
import type { Workflow, Task } from "@/types/api";

export function useTasks() {
  return useQuery(["tasks", "list"], tasksApi.listTasks, { staleTime: 1000 * 60 * 2 });
}

export function useWorkflows() {
  return useQuery(["tasks", "workflows"], tasksApi.listWorkflows, { staleTime: 1000 * 60 * 5 });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  return useMutation(({ taskId, payload }: { taskId: string; payload: Partial<Task> }) => tasksApi.updateTask(taskId, payload), {
    onSuccess: () => queryClient.invalidateQueries(["tasks", "list"]),
  });
}

export function useSaveWorkflow() {
  const queryClient = useQueryClient();
  return useMutation((workflow: Workflow) => tasksApi.saveWorkflow(workflow), {
    onSuccess: () => queryClient.invalidateQueries(["tasks", "workflows"]),
  });
}
