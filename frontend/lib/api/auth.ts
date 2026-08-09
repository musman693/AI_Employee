import type { SignInPayload, SignUpPayload, UserProfile } from "@/types/api";
import { apiClient } from "./base";

export const authClient = {
  signIn: async (data: SignInPayload) => {
    const response = await apiClient.post<UserProfile>("/auth/login", data);
    return response.data;
  },

  signup: async (data: SignUpPayload) => {
    const response = await apiClient.post<{ message: string }>("/auth/signup", data);
    return response.data;
  },

  requestPasswordReset: async (email: string) => {
    const response = await apiClient.post<{ message: string }>("/auth/forgot-password", { email });
    return response.data;
  },

  resetPassword: async (token: string, password: string) => {
    const response = await apiClient.post<{ message: string }>("/auth/reset-password", { token, password });
    return response.data;
  },

  verifyOtp: async (otp: string) => {
    const response = await apiClient.post<{ verified: boolean }>("/auth/verify-otp", { otp });
    return response.data;
  },

  getProfile: async () => {
    const response = await apiClient.get<UserProfile>("/auth/profile");
    return response.data;
  },
};
