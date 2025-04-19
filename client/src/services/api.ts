
// Mock API response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

// Mock API delay helper
const mockDelay = (ms: number = 1000) => new Promise<void>(resolve => setTimeout(resolve, ms));

export const api = {
  // Base mock fetch with delay
  async fetch<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    await mockDelay();
    return { data: {} as T, status: 200 };
  },
  
  // Generic POST helper
  async post<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.fetch<T>(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  }
};
