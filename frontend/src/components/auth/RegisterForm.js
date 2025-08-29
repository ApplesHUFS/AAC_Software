// RegisterForm.js - 백엔드 검증에 의존하는 간소화된 회원가입 폼
import React, { useState } from 'react';
import { authService } from '../../services/authService';

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

  // 선택지 옵션들
  const GENDER_OPTIONS = ['남성', '여성'];
  const DISABILITY_OPTIONS = ['지적장애', '자폐스펙트럼장애', '의사소통장애'];

  // 일반 폼 필드 변경 처리
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));

    if (error) {
      setError('');
    }
  };

  // 관심 주제 추가 처리
  const handleAddTopic = () => {
    const trimmedTopic = topicInput.trim();
    
    if (!trimmedTopic || formData.interestingTopics.includes(trimmedTopic)) {
      return;
    }

    setFormData(prevData => ({
      ...prevData,
      interestingTopics: [...prevData.interestingTopics, trimmedTopic]
    }));
    setTopicInput('');
  };

  // 관심 주제 제거 처리
  const handleRemoveTopic = (topicToRemove) => {
    setFormData(prevData => ({
      ...prevData,
      interestingTopics: prevData.interestingTopics.filter(topic => topic !== topicToRemove)
    }));
  };

  // 관심 주제 입력 키보드 이벤트 처리
  const handleTopicKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTopic();
    }
  };

  // 회원가입 폼 제출 처리 (백엔드에서 모든 검증 수행)
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
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
        onRegisterSuccess(response.data);
      } else {
        setError(response.error || '회원가입에 실패했습니다.');
      }
    } catch (error) {
      console.error('회원가입 에러:', error);
      setError(error.message || '회원가입 중 오류가 발생했습니다.');
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
              placeholder="사용자 ID를 입력하세요"
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
              placeholder="이름을 입력해주세요"
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
              placeholder="AAC 카드 사용이 아닌 일반적인 의사소통 시의 특징을 입력해주세요"
              required
              rows="3"
              disabled={loading}
            />
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
                placeholder="관심 주제를 입력하세요"
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
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
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
              placeholder="비밀번호를 입력하세요"
              required
              autoComplete="new-password"
              disabled={loading}
            />
          </div>
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}
        
        <button 
          type="submit" 
          className="primary-button"
          disabled={loading}
        >
          {loading ? '가입 중...' : '회원가입'}
        </button>
      </form>
      
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