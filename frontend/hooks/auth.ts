import { useQuery } from "@tanstack/react-query";
import { authClient } from "@/lib/api/auth";

export function useProfile() {
  return useQuery(["auth", "profile"], () => authClient.getProfile(), { retry: 1, staleTime: 1000 * 60 * 2 });
}
