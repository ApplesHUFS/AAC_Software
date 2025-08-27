// React proxy를 사용하므로 상대 경로로 설정
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'http://localhost:8000'  // 프로덕션에서는 직접 백엔드 주소
  : '';  // 개발환경에서는 proxy 사용

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { method: 'GET', ...options });
  }

  post(endpoint, body = {}, options = {}) {
    return this.request(endpoint, { method: 'POST', body, ...options });
  }

  put(endpoint, body = {}, options = {}) {
    return this.request(endpoint, { method: 'PUT', body, ...options });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { method: 'DELETE', ...options });
  }
}

const apiClient = new ApiClient();
export default apiClient;
