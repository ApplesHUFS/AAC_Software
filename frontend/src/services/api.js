// api.js - 중앙화된 API 클라이언트
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// HTTP 상태 코드 상수
const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  NOT_FOUND: 404,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
};

// 요청 타임아웃 및 재시도 설정
const REQUEST_TIMEOUT = 3000000;
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000,
  retryCondition: (error) => {
    return error.name === 'TypeError' || 
           error.message.includes('fetch') ||
           error.status >= 500;
  }
};

// 에러 메시지 매핑
const ERROR_MESSAGES = {
  [HTTP_STATUS.BAD_REQUEST]: '요청이 올바르지 않습니다.',
  [HTTP_STATUS.UNAUTHORIZED]: '인증이 필요합니다.',
  [HTTP_STATUS.NOT_FOUND]: '요청한 리소스를 찾을 수 없습니다.',
  [HTTP_STATUS.UNPROCESSABLE_ENTITY]: '요청 데이터를 처리할 수 없습니다.',
  [HTTP_STATUS.INTERNAL_SERVER_ERROR]: '서버 내부 오류가 발생했습니다.',
  [HTTP_STATUS.SERVICE_UNAVAILABLE]: '서비스를 일시적으로 사용할 수 없습니다.',
  NETWORK_ERROR: '네트워크 연결을 확인해주세요.',
  TIMEOUT_ERROR: '요청 시간이 초과되었습니다.'
};

// API 클라이언트 클래스
class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  // 타임아웃이 적용된 fetch 래퍼
  async fetchWithTimeout(url, options) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        throw new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
      }
      throw error;
    }
  }

  // 지연 함수
  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 재시도 로직이 포함된 요청 실행
  async executeWithRetry(requestFn, retryCount = 0) {
    try {
      return await requestFn();
    } catch (error) {
      const shouldRetry = retryCount < RETRY_CONFIG.maxRetries && 
                         RETRY_CONFIG.retryCondition(error);
      
      if (shouldRetry) {
        console.warn(`API 요청 실패, ${retryCount + 1}번째 재시도 중:`, error.message);
        await this.delay(RETRY_CONFIG.retryDelay * (retryCount + 1));
        return this.executeWithRetry(requestFn, retryCount + 1);
      }
      
      throw error;
    }
  }

  // 응답 처리 (app.py 응답 구조에 맞춤)
  async processResponse(response) {
    let responseData;

    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        const text = await response.text();
        responseData = { 
          success: false, 
          error: `예상치 못한 응답 형식: ${text.substring(0, 100)}...` 
        };
      }
    } catch (parseError) {
      console.error('응답 파싱 오류:', parseError);
      throw new Error('서버 응답을 처리할 수 없습니다.');
    }

    if (!response.ok) {
      const errorMessage = responseData.error || 
                          ERROR_MESSAGES[response.status] || 
                          `HTTP ${response.status} 오류가 발생했습니다.`;
      
      const error = new Error(errorMessage);
      error.status = response.status;
      error.response = responseData;
      throw error;
    }

    if (responseData.success === false) {
      const errorMessage = responseData.error || '서버에서 요청을 거부했습니다.';
      const error = new Error(errorMessage);
      error.status = response.status;
      error.response = responseData;
      throw error;
    }

    return responseData;
  }

  // 기본 HTTP 요청 메서드
  async request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
    
    const config = {
      method: 'GET',
      headers: {
        ...this.defaultHeaders,
        ...options.headers
      },
      ...options
    };

    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }

    const requestFn = async () => {
      try {
        console.log(`API 요청: ${config.method} ${url}`);
        
        const response = await this.fetchWithTimeout(url, config);
        const data = await this.processResponse(response);
        
        console.log(`API 응답: ${config.method} ${url} - 성공`);
        return data;
      } catch (error) {
        console.error(`API 오류: ${config.method} ${url}`, error);
        
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
        }
        
        throw error;
      }
    };

    return this.executeWithRetry(requestFn);
  }

  // HTTP 메서드들
  async get(endpoint, options = {}) {
    if (options.params) {
      const searchParams = new URLSearchParams();
      Object.keys(options.params).forEach(key => {
        if (options.params[key] !== undefined && options.params[key] !== null) {
          searchParams.append(key, options.params[key]);
        }
      });
      
      const separator = endpoint.includes('?') ? '&' : '?';
      endpoint = `${endpoint}${separator}${searchParams.toString()}`;
      
      delete options.params;
    }

    return this.request(endpoint, { method: 'GET', ...options });
  }

  async post(endpoint, body = null, options = {}) {
    return this.request(endpoint, { method: 'POST', body, ...options });
  }

  async put(endpoint, body = null, options = {}) {
    return this.request(endpoint, { method: 'PUT', body, ...options });
  }

  async delete(endpoint, options = {}) {
    return this.request(endpoint, { method: 'DELETE', ...options });
  }

  // 헬스체크 요청
  async healthCheck() {
    try {
      const response = await this.get('/health');
      return response.success === true;
    } catch (error) {
      console.error('헬스체크 실패:', error);
      return false;
    }
  }
}

const apiClient = new ApiClient();
export default apiClient;