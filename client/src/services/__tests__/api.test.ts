import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { api, ApiResponse } from '../api'; // Adjust path as necessary
import { authService } from '../auth'; // For mocking getToken

// Mock the authService
vi.mock('../auth', () => ({
  authService: {
    getToken: vi.fn(),
  },
}));

describe('API Service', () => {
  const mockBaseUrl = '/api'; // Should match BASE_URL in api.ts

  beforeEach(() => {
    // Reset mocks before each test
    vi.resetAllMocks();
    global.fetch = vi.fn(); // Mock global fetch
  });

  afterEach(() => {
    // Clean up the mock to ensure it's not used in other test files
    vi.restoreAllMocks();
  });

  describe('api.get', () => {
    it('should make a GET request and return successful JSON response', async () => {
      const mockData = { message: 'Success!' };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
        headers: new Headers({ 'Content-Type': 'application/json' }),
      });

      const response: ApiResponse<typeof mockData> = await api.get('/test-get');

      expect(fetch).toHaveBeenCalledWith(`${mockBaseUrl}/test-get`, expect.objectContaining({ method: 'GET' }));
      expect(response.data).toEqual(mockData);
      expect(response.status).toBe(200);
      expect(response.error).toBeUndefined();
    });

    it('should handle API error for GET request', async () => {
      const mockError = { error: 'Not found' };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => mockError,
        statusText: 'Not Found',
        headers: new Headers({ 'Content-Type': 'application/json' }),
      });

      const response = await api.get('/test-get-error');

      expect(response.error).toBe('Not found');
      expect(response.status).toBe(404);
      expect(response.data).toBeUndefined();
    });
    
    it('should handle non-JSON API error for GET request', async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => { throw new Error("Not JSON"); }, // Simulate non-JSON error response
        statusText: 'Internal Server Error',
        headers: new Headers(),
      });

      const response = await api.get('/test-get-non-json-error');
      expect(response.error).toBe('Internal Server Error');
      expect(response.status).toBe(500);
    });


    it('should handle network error for GET request', async () => {
      (fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(new Error('Network failed'));

      const response = await api.get('/test-get-network-error');

      expect(response.error).toBe('Network failed');
      expect(response.status).toBe(0); // As per implementation
      expect(response.data).toBeUndefined();
    });

    it('should include Authorization header if token exists for GET', async () => {
      (authService.getToken as ReturnType<typeof vi.fn>).mockReturnValueOnce('fake-token-123');
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers({ 'Content-Type': 'application/json' }),
      });

      await api.get('/test-auth-get');

      expect(fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/test-auth-get`,
        expect.objectContaining({
          headers: expect.objectContaining(new Headers({ 'Authorization': 'Bearer fake-token-123' })),
        })
      );
    });
    
    it('should handle 204 No Content for GET request', async () => {
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => null, // json might not be called or return null
        headers: new Headers({ 'content-length': '0' }), 
      });

      const response = await api.get('/test-get-204');
      expect(response.status).toBe(204);
      expect(response.data).toBeUndefined();
      expect(response.error).toBeUndefined();
    });
  });

  describe('api.post', () => {
    const postData = { key: 'value' };

    it('should make a POST request with JSON body and return successful response', async () => {
      const mockResponseData = { id: 1, ...postData };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponseData,
        headers: new Headers({ 'Content-Type': 'application/json' }),
      });

      const response = await api.post('/test-post', postData);

      expect(fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/test-post`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
          headers: expect.objectContaining(new Headers({ 'Content-Type': 'application/json' })),
        })
      );
      expect(response.data).toEqual(mockResponseData);
      expect(response.status).toBe(201);
    });

    it('should include Authorization header if token exists for POST', async () => {
      (authService.getToken as ReturnType<typeof vi.fn>).mockReturnValueOnce('secure-token-456');
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers({ 'Content-Type': 'application/json' }),
      });

      await api.post('/test-auth-post', postData);

      expect(fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/test-auth-post`,
        expect.objectContaining({
          headers: expect.objectContaining(new Headers({ 
            'Content-Type': 'application/json',
            'Authorization': 'Bearer secure-token-456' 
          })),
        })
      );
    });
  });
  
  describe('api.postFormData', () => {
    it('should make a POST request with FormData body', async () => {
      const formData = new FormData();
      formData.append('field', 'value');
      
      const mockResponseData = { message: 'FormData received' };
      (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponseData,
        headers: new Headers({ 'Content-Type': 'application/json' }), // Response can be JSON
      });

      const response = await api.postFormData('/test-formdata', formData);

      expect(fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/test-formdata`,
        expect.objectContaining({
          method: 'POST',
          body: formData,
          // Content-Type for FormData is set by browser, so not explicitly in headers here
        })
      );
      // Check that Content-Type is NOT 'application/json' in the request headers
      const fetchCallArgs = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][1];
      const requestHeaders = fetchCallArgs.headers as Headers;
      expect(requestHeaders.has('Content-Type')).toBe(false); // Or check it's multipart/form-data if browser mock sets it
      
      expect(response.data).toEqual(mockResponseData);
      expect(response.status).toBe(200);
    });
  });

  // Basic tests for PUT and DELETE can follow similar patterns to GET/POST
  describe('api.put', () => {
    it('should make a PUT request', async () => {
        const putData = { message: 'update' };
        (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
            ok: true, status: 200, json: async () => putData, headers: new Headers({'Content-Type': 'application/json'})
        });
        const response = await api.put('/test-put/1', putData);
        expect(fetch).toHaveBeenCalledWith(`${mockBaseUrl}/test-put/1`, expect.objectContaining({method: 'PUT', body: JSON.stringify(putData)}));
        expect(response.data).toEqual(putData);
    });
  });

  describe('api.delete', () => {
    it('should make a DELETE request', async () => {
        (fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
            ok: true, status: 204, headers: new Headers({'content-length': '0'}) // 204 No Content
        });
        const response = await api.delete('/test-delete/1');
        expect(fetch).toHaveBeenCalledWith(`${mockBaseUrl}/test-delete/1`, expect.objectContaining({method: 'DELETE'}));
        expect(response.status).toBe(204);
        expect(response.data).toBeUndefined();
    });
  });

});
