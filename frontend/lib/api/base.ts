import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { getSession } from "next-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || "";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

let inMemoryRefreshToken: string | null = null;
let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

export function setClientTokens(accessToken: string | null, refreshToken?: string | null) {
  if (accessToken) {
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
    if (typeof window !== "undefined") window.localStorage.setItem("ai_employee_access_token", accessToken);
  } else {
    delete apiClient.defaults.headers.common["Authorization"];
    if (typeof window !== "undefined") window.localStorage.removeItem("ai_employee_access_token");
  }
  if (typeof window !== "undefined") {
    if (refreshToken) window.localStorage.setItem("ai_employee_refresh_token", refreshToken);
    else window.localStorage.removeItem("ai_employee_refresh_token");
  }
  inMemoryRefreshToken = refreshToken ?? null;
}

export function clearClientTokens() {
  setClientTokens(null, null);
}

async function refreshAccessToken(): Promise<string | null> {
  if (isRefreshing && refreshPromise) return refreshPromise;
  const refreshToken = inMemoryRefreshToken ?? (typeof window !== "undefined" ? window.localStorage.getItem("ai_employee_refresh_token") : null);
  if (!refreshToken) return null;

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const resp = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken }, { withCredentials: true });
      const data = resp.data ?? {};
      const newAccess = data.access_token ?? data.token ?? data.accessToken ?? null;
      const newRefresh = data.refresh_token ?? data.refreshToken ?? null;
      if (newAccess) {
        setClientTokens(newAccess, newRefresh ?? refreshToken);
        return newAccess;
      }
      return null;
    } catch (e) {
      clearClientTokens();
      return null;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// Attach Authorization header using NextAuth session token when available,
// fallback to localStorage for compatibility with older flows.
apiClient.interceptors.request.use(async (config: AxiosRequestConfig) => {
  try {
    // Prefer explicit header already set
    if (config.headers && (config.headers as any).Authorization) return config;

    // Client-side: try NextAuth session then localStorage
    if (typeof window !== "undefined") {
      try {
        const session = await getSession();
        const token = (session as any)?.accessToken ?? window.localStorage.getItem("ai_employee_access_token");
        if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
      } catch (e) {
        // ignore
      }
    } else {
      // Server-side: use default Authorization if present
      const defaultAuth = (apiClient.defaults.headers.common as any)["Authorization"];
      if (defaultAuth && config.headers) config.headers.Authorization = defaultAuth;
    }
  } catch (err) {
    // ignore
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = (error.config as AxiosRequestConfig & { _retry?: boolean }) ?? {};
    const status = error.response?.status;
    const message = (error as any)?.response?.data?.detail || error.message || "Unexpected API error";

    // Attempt refresh once on 401
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const newAccess = await refreshAccessToken();
      if (newAccess) {
        if (!originalRequest.headers) originalRequest.headers = {};
        (originalRequest.headers as any).Authorization = `Bearer ${newAccess}`;
        try {
          return await axios(originalRequest);
        } catch (retryErr) {
          return Promise.reject(retryErr);
        }
      }
    }

    return Promise.reject(new Error(message));
  }
);

export default apiClient;
