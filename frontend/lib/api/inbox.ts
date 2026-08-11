import type { ConversationThread, ThreadReply, DraftRequest } from "@/types/api";
import { apiClient } from "./base";

export const inboxApi = {
  listThreads: async () => {
    const response = await apiClient.get<ConversationThread[]>('/inbox/threads');
    return response.data;
  },
  getThread: async (threadId: string) => {
    const response = await apiClient.get<ConversationThread>(`/inbox/threads/${threadId}`);
    return response.data;
  },
  sendReply: async (threadId: string, payload: ThreadReply) => {
    const response = await apiClient.post(`/inbox/threads/${threadId}/reply`, payload);
    return response.data;
  },
  summarizeThread: async (threadId: string) => {
    const thread = await inboxApi.getThread(threadId);
    const response = await apiClient.post<{ summary: string }>(`/communications/email/summarize`, { messages: thread.messages.map((message) => message.text) });
    return response.data;
  },
  classifyThread: async (threadId: string) => {
    const response = await apiClient.post<{ category: string }>(`/inbox/threads/${threadId}/classify`, {});
    return response.data;
  },
  createDraft: async (payload: DraftRequest) => {
    const response = await apiClient.post<{ subject: string; body: string }>('/communications/email/draft', { instruction: `${payload.prompt} Subject: ${payload.subject}` });
    return { draft: response.data.body };
  },
};
