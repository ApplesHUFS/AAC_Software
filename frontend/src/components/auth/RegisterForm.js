import React, { useState } from 'react';
import { authService } from '../../services/authService';

// 회원가입 폼 컴포넌트
// 사용자 페르소나 정보를 포함한 회원가입 처리
const RegisterForm = ({ onRegisterSuccess, switchToLogin }) => {
  const [formData, setFormData] = useState({
    userId: '',
    name: '',
    age: '',
    gender: '',
    disabilityType: '',
    communicationCharacteristics: '',
    interestingTopics: [],
    password: ''
  });
  const [topicInput, setTopicInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 선택지 옵션들 - 흐름명세서에 따른 장애 유형
  const GENDER_OPTIONS = ['남성', '여성'];
  const DISABILITY_OPTIONS = ['지적장애', '자폐스펙트럼장애', '의사소통장애'];

  // 일반 폼 필드 변경 처리
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));

    // 입력 시 에러 메시지 클리어
    if (error) {
      setError('');
    }
  };

  // 관심 주제 추가 처리
  const handleAddTopic = () => {
    const trimmedTopic = topicInput.trim();
    
    if (!trimmedTopic) {
      return;
    }
    
    if (formData.interestingTopics.includes(trimmedTopic)) {
      setError('이미 추가된 관심 주제입니다.');
      return;
    }
    
    if (formData.interestingTopics.length >= 10) {
      setError('관심 주제는 최대 10개까지 추가할 수 있습니다.');
      return;
    }

    setFormData(prevData => ({
      ...prevData,
      interestingTopics: [...prevData.interestingTopics, trimmedTopic]
    }));
    setTopicInput('');
    
    // 성공적으로 추가되면 에러 클리어
    if (error) {
      setError('');
    }
  };

  // 관심 주제 제거 처리
  const handleRemoveTopic = (topicToRemove) => {
    setFormData(prevData => ({
      ...prevData,
      interestingTopics: prevData.interestingTopics.filter(topic => topic !== topicToRemove)
    }));
  };

  // 관심 주제 입력 키보드 이벤트 처리 (엔터키로 추가)
  const handleTopicKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTopic();
    }
  };

  // 폼 입력 검증
  const validateForm = () => {
    if (!formData.userId.trim()) {
      return '사용자 ID를 입력해주세요.';
    }
    
    if (formData.userId.trim().length < 3) {
      return '사용자 ID는 3글자 이상이어야 합니다.';
    }
    
    if (!formData.name.trim()) {
      return '이름을 입력해주세요.';
    }
    
    if (!formData.age || parseInt(formData.age) < 1 || parseInt(formData.age) > 100) {
      return '올바른 나이를 입력해주세요 (1-100세).';
    }
    
    if (!formData.gender) {
      return '성별을 선택해주세요.';
    }
    
    if (!formData.disabilityType) {
      return '장애 유형을 선택해주세요.';
    }
    
    if (!formData.communicationCharacteristics.trim()) {
      return '의사소통 특징을 입력해주세요.';
    }
    
    if (formData.interestingTopics.length === 0) {
      return '관심 주제를 최소 1개 이상 입력해주세요.';
    }
    
    if (!formData.password) {
      return '비밀번호를 입력해주세요.';
    }
    
    if (formData.password.length < 4) {
      return '비밀번호는 4글자 이상이어야 합니다.';
    }
    
    return null;
  };

  // 회원가입 폼 제출 처리
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // 폼 검증
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      // app.py 요구사항에 맞게 데이터 정제
      const registrationData = {
        userId: formData.userId.trim(),
        name: formData.name.trim(),
        age: parseInt(formData.age),
        gender: formData.gender,
        disabilityType: formData.disabilityType,
        communicationCharacteristics: formData.communicationCharacteristics.trim(),
        interestingTopics: formData.interestingTopics,
        password: formData.password
      };

      const response = await authService.register(registrationData);
      
      if (response.success) {
        // 회원가입 성공
        onRegisterSuccess(response.data);
      } else {
        setError(response.error || '회원가입에 실패했습니다.');
      }
    } catch (error) {
      console.error('회원가입 에러:', error);
      
      // 에러 타입별 처리
      if (error.message.includes('fetch')) {
        setError('서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.');
      } else if (error.message.includes('이미 존재')) {
        setError('이미 존재하는 사용자 ID입니다. 다른 ID를 사용해주세요.');
      } else {
        setError(error.message || '회원가입 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>회원가입</h2>
      <p>개인화된 AAC 서비스를 위해 정보를 입력해주세요.</p>
      
      <form onSubmit={handleSubmit} noValidate>
        {/* 기본 정보 */}
        <div className="form-section">
          <h4>기본 정보</h4>
          
          <div className="form-group">
            <label htmlFor="userId">사용자 ID *</label>
            <input
              type="text"
              id="userId"
              name="userId"
              value={formData.userId}
              onChange={handleChange}
              placeholder="3글자 이상의 고유한 ID를 입력하세요"
              required
              autoComplete="username"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="name">이름 *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="실명을 입력해주세요"
              required
              autoComplete="name"
              disabled={loading}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="age">나이 *</label>
              <input
                type="number"
                id="age"
                name="age"
                min="1"
                max="100"
                value={formData.age}
                onChange={handleChange}
                placeholder="나이"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="gender">성별 *</label>
              <select
                id="gender"
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                required
                disabled={loading}
              >
                <option value="">선택해주세요</option>
                {GENDER_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 장애 정보 */}
        <div className="form-section">
          <h4>장애 및 의사소통 정보</h4>
          
          <div className="form-group">
            <label htmlFor="disabilityType">장애 유형 *</label>
            <select
              id="disabilityType"
              name="disabilityType"
              value={formData.disabilityType}
              onChange={handleChange}
              required
              disabled={loading}
            >
              <option value="">선택해주세요</option>
              {DISABILITY_OPTIONS.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="communicationCharacteristics">의사소통 특징 *</label>
            <textarea
              id="communicationCharacteristics"
              name="communicationCharacteristics"
              value={formData.communicationCharacteristics}
              onChange={handleChange}
              placeholder="AAC 카드 사용이 아닌 일반적인 의사소통 시의 특징을 구체적으로 입력해주세요"
              required
              rows="3"
              disabled={loading}
            />
            <small>예: 단어 선택의 어려움, 문장 구성의 특징, 표현 방식 등</small>
          </div>
        </div>

        {/* 관심 주제 */}
        <div className="form-section">
          <h4>관심 주제</h4>
          
          <div className="form-group">
            <label>관심 주제 추가 *</label>
            <div className="topic-input-section">
              <input
                type="text"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                onKeyPress={handleTopicKeyPress}
                placeholder="관심 주제를 입력하고 추가 버튼을 클릭하세요"
                disabled={loading}
              />
              <button 
                type="button" 
                onClick={handleAddTopic}
                disabled={loading || !topicInput.trim()}
                className="secondary-button"
              >
                추가
              </button>
            </div>
            
            <div className="topic-list">
              {formData.interestingTopics.map((topic, index) => (
                <span key={index} className="topic-tag">
                  {topic}
                  <button 
                    type="button" 
                    onClick={() => handleRemoveTopic(topic)}
                    disabled={loading}
                    aria-label={`${topic} 주제 제거`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            
            {formData.interestingTopics.length === 0 && (
              <small className="form-hint">최소 1개 이상의 관심 주제를 추가해주세요.</small>
            )}
          </div>
        </div>

        {/* 비밀번호 */}
        <div className="form-section">
          <div className="form-group">
            <label htmlFor="password">비밀번호 *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="4글자 이상의 비밀번호를 입력하세요"
              required
              autoComplete="new-password"
              disabled={loading}
            />
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}
        
        {/* 회원가입 버튼 */}
        <button 
          type="submit" 
          className="primary-button"
          disabled={loading}
        >
          {loading ? '가입 중...' : '회원가입'}
        </button>
      </form>
      
      {/* 로그인 링크 */}
      <div className="auth-switch">
        <p>
          이미 계정이 있으신가요? 
          <button 
            type="button" 
            className="link-button" 
            onClick={switchToLogin}
            disabled={loading}
          >
            로그인
          </button>
        </p>
      </div>
    </div>
  );
};

export { RegisterForm };