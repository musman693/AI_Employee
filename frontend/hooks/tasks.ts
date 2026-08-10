import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { tasksApi } from "@/lib/api/tasks";
import type { Workflow, Task } from "@/types/api";

export function useTasks() {
  return useQuery({ queryKey: ["tasks", "list"], queryFn: tasksApi.listTasks, staleTime: 1000 * 60 * 2 });
}

export function useWorkflows() {
  return useQuery({ queryKey: ["tasks", "workflows"], queryFn: tasksApi.listWorkflows, staleTime: 1000 * 60 * 5 });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: ({ taskId, payload }: { taskId: string; payload: Partial<Task> }) => tasksApi.updateTask(taskId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks", "list"] }),
  });
}

export function useSaveWorkflow() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (workflow: Workflow) => tasksApi.saveWorkflow(workflow),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tasks", "workflows"] }),
  });
}
