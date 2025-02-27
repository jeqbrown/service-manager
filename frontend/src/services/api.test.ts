import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import api from './api';

describe('API Service', () => {
  let mockAxios: MockAdapter;

  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Create a fresh mock adapter
    mockAxios = new MockAdapter(api);
  });

  afterEach(() => {
    mockAxios.restore();
  });

  describe('Request Interceptor', () => {
    test('adds authorization header when token exists', async () => {
      const token = 'test-token';
      localStorage.setItem('token', token);

      mockAxios.onGet('/test').reply(config => {
        expect(config.headers?.Authorization).toBe(`Bearer ${token}`);
        return [200, {}];
      });

      await api.get('/test');
    });

    test('does not add authorization header when token is missing', async () => {
      mockAxios.onGet('/test').reply(config => {
        expect(config.headers?.Authorization).toBeUndefined();
        return [200, {}];
      });

      await api.get('/test');
    });
  });

  describe('Response Interceptor', () => {
    test('handles successful responses', async () => {
      const responseData = { data: 'test' };
      mockAxios.onGet('/test').reply(200, responseData);

      const response = await api.get('/test');
      expect(response.data).toEqual(responseData);
    });

    test('redirects to login on 401 unauthorized', async () => {
      // Mock window.location.href
      const originalLocation = window.location;
      delete window.location;
      window.location = { ...originalLocation, href: '' };

      mockAxios.onGet('/test').reply(401);
      
      try {
        await api.get('/test');
      } catch (error) {
        expect(localStorage.getItem('token')).toBeNull();
        expect(window.location.href).toBe('/login');
      }

      // Restore window.location
      window.location = originalLocation;
    });

    test('handles network errors', async () => {
      mockAxios.onGet('/test').networkError();

      try {
        await api.get('/test');
      } catch (error) {
        expect(error).toBeTruthy();
      }
    });
  });

  describe('API Base Configuration', () => {
    test('uses correct base URL from environment', () => {
      const originalEnv = process.env;
      process.env.REACT_APP_API_URL = 'http://test-api.com';

      // Re-import api to get new baseURL
      jest.resetModules();
      const newApi = require('./api').default;

      expect(newApi.defaults.baseURL).toBe('http://test-api.com');

      // Restore original env
      process.env = originalEnv;
    });

    test('uses default base URL when environment variable is not set', () => {
      const originalEnv = process.env;
      delete process.env.REACT_APP_API_URL;

      // Re-import api to get new baseURL
      jest.resetModules();
      const newApi = require('./api').default;

      expect(newApi.defaults.baseURL).toBe('http://localhost:8000/api/v1');

      // Restore original env
      process.env = originalEnv;
    });
  });

  describe('Common API Operations', () => {
    test('handles GET requests with query parameters', async () => {
      mockAxios.onGet('/test', { params: { id: 1 } }).reply(200, { data: 'test' });

      const response = await api.get('/test', { params: { id: 1 } });
      expect(response.data).toEqual({ data: 'test' });
    });

    test('handles POST requests with data', async () => {
      const postData = { name: 'test' };
      mockAxios.onPost('/test', postData).reply(201, { id: 1, ...postData });

      const response = await api.post('/test', postData);
      expect(response.data).toEqual({ id: 1, ...postData });
    });

    test('handles request cancellation', async () => {
      const controller = new AbortController();
      mockAxios.onGet('/test').reply(200, { data: 'test' });

      const promise = api.get('/test', { signal: controller.signal });
      controller.abort();

      try {
        await promise;
      } catch (error) {
        expect(axios.isCancel(error)).toBe(true);
      }
    });
  });
});