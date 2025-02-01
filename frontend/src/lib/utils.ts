import axios from "axios";
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { NEXT_PUBLIC_API_URL } from "./constants";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const api = axios.create({
  baseURL: NEXT_PUBLIC_API_URL,
  maxRedirects: 5, // Allow up to 5 redirects
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to ensure HTTPS
api.interceptors.request.use((config) => {
  // Ensure the URL uses HTTPS
  if (config.url) {
    config.url = config.url.replace('http://', 'https://');
  }
  return config;
});

// Add response interceptor to handle redirects
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 307) {
      const redirectUrl = error.response.headers.location;
      if (redirectUrl) {
        // Ensure redirect URL uses HTTPS
        const httpsRedirectUrl = redirectUrl.replace('http://', 'https://');
        // Make a new request to the redirect URL
        return api.post(httpsRedirectUrl, error.config?.data, {
          headers: error.config?.headers
        });
      }
    }
    return Promise.reject(error);
  }
);