import type { SignInPayload, SignUpPayload, UserProfile } from "@/types/api";
import { apiClient } from "./base";

export const authClient = {
  signIn: async (data: SignInPayload) => {
    const response = await apiClient.post<UserProfile>("/auth-service/login", data);
    return response.data;
  },

  signup: async (data: SignUpPayload) => {
    const response = await apiClient.post<{ message: string }>("/auth-service/register", data);
    return response.data;
  },

  requestPasswordReset: async (email: string) => {
    const response = await apiClient.post<{ message: string }>("/auth-service/forgot-password", { email });
    return response.data;
  },

  resetPassword: async (token: string, password: string) => {
    const response = await apiClient.post<{ message: string }>("/auth-service/reset-password", { token, password });
    return response.data;
  },

  verifyOtp: async (otp: string) => {
    const response = await apiClient.post<{ verified: boolean }>("/auth-service/verify-otp", { otp });
    return response.data;
  },

  getProfile: async () => {
    const response = await apiClient.get<UserProfile>("/auth-service/profile");
    return response.data;
  },
};
