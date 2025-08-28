/**
 * API 클라이언트
 * app.py 백엔드와의 HTTP 통신을 담당하는 중앙화된 클라이언트
 */

// 백엔드 서버 주소 (환경에 따라 설정)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * HTTP 상태 코드 상수
 */
const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
};

/**
 * 요청 타임아웃 설정 (밀리초)
 */
const REQUEST_TIMEOUT = 30000; // 30초

/**
 * 재시도 설정
 */
const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000, // 1초
  retryCondition: (error) => {
    // 네트워크 오류나 일시적 서버 오류인 경우 재시도
    return error.name === 'TypeError' || 
           error.message.includes('fetch') ||
           error.status >= 500;
  }
};

/**
 * 에러 메시지 매핑
 */
const ERROR_MESSAGES = {
  [HTTP_STATUS.BAD_REQUEST]: '요청이 올바르지 않습니다.',
  [HTTP_STATUS.UNAUTHORIZED]: '인증이 필요합니다.',
  [HTTP_STATUS.FORBIDDEN]: '접근 권한이 없습니다.',
  [HTTP_STATUS.NOT_FOUND]: '요청한 리소스를 찾을 수 없습니다.',
  [HTTP_STATUS.CONFLICT]: '요청이 현재 상태와 충돌합니다.',
  [HTTP_STATUS.UNPROCESSABLE_ENTITY]: '요청 데이터를 처리할 수 없습니다.',
  [HTTP_STATUS.INTERNAL_SERVER_ERROR]: '서버 내부 오류가 발생했습니다.',
  [HTTP_STATUS.SERVICE_UNAVAILABLE]: '서비스를 일시적으로 사용할 수 없습니다.',
  NETWORK_ERROR: '네트워크 연결을 확인해주세요.',
  TIMEOUT_ERROR: '요청 시간이 초과되었습니다.',
  PARSE_ERROR: '서버 응답을 처리할 수 없습니다.'
};

/**
 * API 클라이언트 클래스
 */
class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  /**
   * 타임아웃이 적용된 fetch 래퍼
   * @param {string} url - 요청 URL
   * @param {Object} options - fetch 옵션
   * @returns {Promise<Response>} fetch Response
   */
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

  /**
   * 지연 함수 (재시도 간격)
   * @param {number} ms - 지연 시간 (밀리초)
   * @returns {Promise<void>}
   */
  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 재시도 로직이 포함된 요청 실행
   * @param {Function} requestFn - 요청 함수
   * @param {number} retryCount - 현재 재시도 횟수
   * @returns {Promise<any>} 요청 결과
   */
  async executeWithRetry(requestFn, retryCount = 0) {
    try {
      return await requestFn();
    } catch (error) {
      const shouldRetry = retryCount < RETRY_CONFIG.maxRetries && 
                         RETRY_CONFIG.retryCondition(error);
      
      if (shouldRetry) {
        console.warn(`API 요청 실패, ${retryCount + 1}번째 재시도 중:`, error.message);
        await this.delay(RETRY_CONFIG.retryDelay * (retryCount + 1)); // 지수 백오프
        return this.executeWithRetry(requestFn, retryCount + 1);
      }
      
      throw error;
    }
  }

  /**
   * 응답 처리 (app.py 응답 구조에 맞춤)
   * @param {Response} response - fetch Response 객체
   * @returns {Promise<Object>} 파싱된 응답 데이터
   */
  async processResponse(response) {
    let responseData;

    // Content-Type 확인
    const contentType = response.headers.get('content-type');
    
    try {
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        // JSON이 아닌 경우 텍스트로 처리
        const text = await response.text();
        responseData = { 
          success: false, 
          error: `예상치 못한 응답 형식: ${text.substring(0, 100)}...` 
        };
      }
    } catch (parseError) {
      console.error('응답 파싱 오류:', parseError);
      throw new Error(ERROR_MESSAGES.PARSE_ERROR);
    }

    // app.py 응답 구조 검증
    if (typeof responseData !== 'object' || responseData === null) {
      throw new Error('올바르지 않은 서버 응답 구조입니다.');
    }

    // HTTP 상태 코드별 처리
    if (!response.ok) {
      const errorMessage = responseData.error || 
                          ERROR_MESSAGES[response.status] || 
                          `HTTP ${response.status} 오류가 발생했습니다.`;
      
      const error = new Error(errorMessage);
      error.status = response.status;
      error.response = responseData;
      throw error;
    }

    // app.py는 success 필드로 성공/실패를 표시
    if (responseData.success === false) {
      const errorMessage = responseData.error || '서버에서 요청을 거부했습니다.';
      const error = new Error(errorMessage);
      error.status = response.status;
      error.response = responseData;
      throw error;
    }

    return responseData;
  }

  /**
   * 기본 HTTP 요청 메서드
   * @param {string} endpoint - API 엔드포인트
   * @param {Object} options - 요청 옵션
   * @returns {Promise<Object>} API 응답
   */
  async request(endpoint, options = {}) {
    // URL 구성
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
    
    // 요청 설정 구성
    const config = {
      method: 'GET',
      headers: {
        ...this.defaultHeaders,
        ...options.headers
      },
      ...options
    };

    // 요청 본문 처리
    if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
      config.body = JSON.stringify(config.body);
    }

    // 요청 함수 정의
    const requestFn = async () => {
      try {
        console.log(`API 요청: ${config.method} ${url}`);
        
        const response = await this.fetchWithTimeout(url, config);
        const data = await this.processResponse(response);
        
        console.log(`API 응답: ${config.method} ${url} - 성공`);
        return data;
      } catch (error) {
        console.error(`API 오류: ${config.method} ${url}`, error);
        
        // 네트워크 오류 처리
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
        }
        
        throw error;
      }
    };

    // 재시도 로직과 함께 요청 실행
    return this.executeWithRetry(requestFn);
  }

  /**
   * GET 요청
   * @param {string} endpoint - API 엔드포인트
   * @param {Object} options - 요청 옵션
   * @returns {Promise<Object>} API 응답
   */
  async get(endpoint, options = {}) {
    // 쿼리 파라미터 처리
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

    return this.request(endpoint, { 
      method: 'GET', 
      ...options 
    });
  }

  /**
   * POST 요청
   * @param {string} endpoint - API 엔드포인트
   * @param {any} body - 요청 본문
   * @param {Object} options - 요청 옵션
   * @returns {Promise<Object>} API 응답
   */
  async post(endpoint, body = null, options = {}) {
    return this.request(endpoint, { 
      method: 'POST', 
      body, 
      ...options 
    });
  }

  /**
   * PUT 요청
   * @param {string} endpoint - API 엔드포인트
   * @param {any} body - 요청 본문
   * @param {Object} options - 요청 옵션
   * @returns {Promise<Object>} API 응답
   */
  async put(endpoint, body = null, options = {}) {
    return this.request(endpoint, { 
      method: 'PUT', 
      body, 
      ...options 
    });
  }

  /**
   * DELETE 요청
   * @param {string} endpoint - API 엔드포인트
   * @param {Object} options - 요청 옵션
   * @returns {Promise<Object>} API 응답
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { 
      method: 'DELETE', 
      ...options 
    });
  }

  /**
   * PATCH 요청
   * @param {string} endpoint - API 엔드포인트
   * @param {any} body - 요청 본문
   * @param {Object} options - 요청 옵션
   * @returns {Promise<Object>} API 응답
   */
  async patch(endpoint, body = null, options = {}) {
    return this.request(endpoint, { 
      method: 'PATCH', 
      body, 
      ...options 
    });
  }

  /**
   * 헬스체크 요청
   * @returns {Promise<boolean>} 서버 상태
   */
  async healthCheck() {
    try {
      const response = await this.get('/health');
      return response.success === true;
    } catch (error) {
      console.error('헬스체크 실패:', error);
      return false;
    }
  }

  /**
   * 기본 URL 설정
   * @param {string} baseURL - 새로운 기본 URL
   */
  setBaseURL(baseURL) {
    this.baseURL = baseURL;
  }

  /**
   * 기본 헤더 설정
   * @param {Object} headers - 설정할 헤더
   */
  setDefaultHeaders(headers) {
    this.defaultHeaders = { ...this.defaultHeaders, ...headers };
  }

  /**
   * 인증 토큰 설정 (향후 JWT 사용 시)
   * @param {string} token - 인증 토큰
   */
  setAuthToken(token) {
    if (token) {
      this.setDefaultHeaders({ 'Authorization': `Bearer ${token}` });
    } else {
      delete this.defaultHeaders['Authorization'];
    }
  }

  /**
   * 요청 인터셉터 (요청 전 처리)
   * @param {Function} interceptor - 인터셉터 함수
   */
  addRequestInterceptor(interceptor) {
    // 향후 구현 예정
    console.warn('요청 인터셉터는 아직 구현되지 않았습니다.');
  }

  /**
   * 응답 인터셉터 (응답 후 처리)
   * @param {Function} interceptor - 인터셉터 함수
   */
  addResponseInterceptor(interceptor) {
    // 향후 구현 예정
    console.warn('응답 인터셉터는 아직 구현되지 않았습니다.');
  }

  /**
   * 디버그 모드 설정
   * @param {boolean} enabled - 디버그 모드 활성화 여부
   */
  setDebugMode(enabled) {
    this.debugMode = enabled;
    if (enabled) {
      console.log('API 클라이언트 디버그 모드가 활성화되었습니다.');
    }
  }

  /**
   * 현재 설정 정보 조회
   * @returns {Object} 현재 API 클라이언트 설정
   */
  getConfig() {
    return {
      baseURL: this.baseURL,
      defaultHeaders: { ...this.defaultHeaders },
      timeout: REQUEST_TIMEOUT,
      retryConfig: { ...RETRY_CONFIG }
    };
  }
}

// API 클라이언트 인스턴스 생성 및 내보내기
const apiClient = new ApiClient();

// 개발 환경에서 디버그 정보 출력
if (process.env.NODE_ENV === 'development') {
  console.log('API 클라이언트 초기화됨:', apiClient.getConfig());
  apiClient.setDebugMode(true);
}

export default apiClient;