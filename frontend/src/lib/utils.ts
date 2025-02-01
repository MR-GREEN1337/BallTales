import axios from "axios";
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { NEXT_PUBLIC_API_URL } from "./constants";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const api = axios.create({
  baseURL: NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
});

// Helper function to enforce HTTPS in production
const enforceHttps = (url: string): string => {
  if (process.env.NODE_ENV === 'production') {
    return url.replace('http://', 'https://');
  }
  return url;
};

// Add request interceptor for production HTTPS enforcement
if (process.env.NODE_ENV === 'production') {
api.interceptors.request.use((config) => {
  if (config.url) {
    config.url = enforceHttps(config.url);
  }
  return config;
});}

if (process.env.NODE_ENV === 'production') {
// Add response interceptor to handle redirects
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 307) {
      const redirectUrl = error.response.headers.location;
      if (redirectUrl) {
        // Apply HTTPS enforcement only in production
        const processedRedirectUrl = enforceHttps(redirectUrl);
        // Make a new request to the redirect URL
        return api.post(processedRedirectUrl, error.config?.data, {
          headers: error.config?.headers
        });
      }
    }
    return Promise.reject(error);
  }
);
}