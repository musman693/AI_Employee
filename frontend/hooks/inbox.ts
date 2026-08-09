import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { inboxApi } from "@/lib/api/inbox";
import type { ThreadReply, DraftRequest } from "@/types/api";

export function useInboxThreads() {
  return useQuery(["inbox", "threads"], inboxApi.listThreads, { staleTime: 1000 * 60 * 1 });
}

export function useThread(threadId: string) {
  return useQuery(["inbox", "thread", threadId], () => inboxApi.getThread(threadId), { enabled: Boolean(threadId), staleTime: 1000 * 60 * 1 });
}

export function useSendReply() {
  const queryClient = useQueryClient();
  return useMutation(({ threadId, payload }: { threadId: string; payload: ThreadReply }) => inboxApi.sendReply(threadId, payload), {
    onSuccess: (_, variables) => queryClient.invalidateQueries(["inbox", "thread", variables.threadId]),
  });
}

export function useCreateDraft() {
  const queryClient = useQueryClient();
  return useMutation((payload: DraftRequest) => inboxApi.createDraft(payload), {
    onSuccess: () => queryClient.invalidateQueries(["inbox", "threads"]),
  });
}
