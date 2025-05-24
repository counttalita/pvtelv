import { authService } from './auth'; // Assuming auth.ts exports authService

const BASE_URL = '/api'; // Adjust if your API is hosted elsewhere or needs full URL

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const token = authService.getToken();
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.append('Authorization', `Bearer ${token}`);
  }

  // Set Content-Type to application/json for relevant methods if not already set
  // and body is not FormData
  const bodyIsFormData = options.body instanceof FormData;
  if (options.body && !bodyIsFormData && !headers.has('Content-Type')) {
    if (['POST', 'PUT', 'PATCH'].includes((options.method || 'GET').toUpperCase())) {
        headers.append('Content-Type', 'application/json');
    }
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      let errorMsg = response.statusText;
      try {
        const errorData = await response.json();
        errorMsg = errorData.error || errorData.message || errorMsg;
      } catch (e) {
        // Response was not JSON, use statusText
      }
      console.error(`API Error: ${response.status} ${errorMsg} on ${endpoint}`);
      return { error: errorMsg, status: response.status };
    }

    // Handle empty responses (e.g., HTTP 204 No Content)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return { data: undefined, status: response.status };
    }
    
    // Try to parse JSON, handle cases where it might not be (though usually should be for ok responses)
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        const data: T = await response.json();
        return { data, status: response.status };
    } else {
        // Handle non-JSON responses if necessary, or treat as an error/unexpected case
        console.warn(`API Warning: Expected JSON response but got ${contentType} on ${endpoint}`);
        // For now, we attempt to provide text if it's not JSON. Adjust based on API contract.
        const textData = await response.text();
        return { data: textData as any, status: response.status }; // Cast as any if type T expects JSON
    }

  } catch (error) {
    console.error('Network or other fetch error:', error);
    const errorMessage = error instanceof Error ? error.message : 'A network error occurred.';
    return { error: errorMessage, status: 0 }; // status 0 for network errors
  }
}

export const api = {
  get: async <T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> => {
    return request<T>(endpoint, { ...options, method: 'GET' });
  },

  post: async <T>(endpoint: string, body: any, options?: RequestInit): Promise<ApiResponse<T>> => {
    return request<T>(endpoint, { 
        ...options, 
        method: 'POST', 
        body: JSON.stringify(body) 
    });
  },

  postFormData: async <T>(endpoint: string, formData: FormData, options?: RequestInit): Promise<ApiResponse<T>> => {
    // For FormData, browser sets Content-Type (multipart/form-data) automatically with boundary
    return request<T>(endpoint, { 
        ...options, 
        method: 'POST', 
        body: formData 
    });
  },

  put: async <T>(endpoint: string, body: any, options?: RequestInit): Promise<ApiResponse<T>> => {
    return request<T>(endpoint, { 
        ...options, 
        method: 'PUT', 
        body: JSON.stringify(body) 
    });
  },

  delete: async <T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> => {
    return request<T>(endpoint, { ...options, method: 'DELETE' });
  },
};
