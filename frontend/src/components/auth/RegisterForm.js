// src/components/auth/RegisterForm.js
import React, { useState } from 'react';
import { authService } from '../../services/authService';

// 선택지 옵션들
const GENDER_OPTIONS = ['남성', '여성'];
const DISABILITY_OPTIONS = ['지적장애', '자폐스펙트럼장애', '의사소통장애'];

const RegisterForm = ({ onRegisterSuccess, switchToLogin }) => {
  const [formData, setFormData] = useState({
    userId: '',
    name: '',
    age: '',
    gender: '',
    disabilityType: '',
    communicationCharacteristics: '',
    interestingTopics: [],
    password: '',
    confirmPassword: ''
  });
  const [topicInput, setTopicInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 폼 입력 변경 처리
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  // 관심 주제 추가
  const handleAddTopic = () => {
    const topic = topicInput.trim();
    
    if (!topic) return;
    
    if (formData.interestingTopics.includes(topic)) {
      setError('이미 추가된 관심 주제입니다.');
      return;
    }

    setFormData(prev => ({
      ...prev,
      interestingTopics: [...prev.interestingTopics, topic]
    }));
    setTopicInput('');
    setError('');
  };

  // 관심 주제 제거
  const handleRemoveTopic = (topicToRemove) => {
    setFormData(prev => ({
      ...prev,
      interestingTopics: prev.interestingTopics.filter(topic => topic !== topicToRemove)
    }));
  };

  // 엔터키로 주제 추가
  const handleTopicKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTopic();
    }
  };

  // 폼 유효성 검증
  const validateForm = () => {
    if (!formData.userId.trim()) return '사용자 ID를 입력해주세요.';
    if (formData.userId.length < 3) return '사용자 ID는 3글자 이상이어야 합니다.';
    if (!formData.name.trim()) return '이름을 입력해주세요.';
    if (!formData.age || formData.age < 1 || formData.age > 100) return '나이는 1~100세 사이로 입력해주세요.';
    if (!formData.gender) return '성별을 선택해주세요.';
    if (!formData.disabilityType) return '장애 유형을 선택해주세요.';
    if (!formData.communicationCharacteristics.trim()) return '의사소통 특징을 입력해주세요.';
    if (formData.interestingTopics.length === 0) return '관심 주제를 최소 1개 이상 입력해주세요.';
    if (!formData.password) return '비밀번호를 입력해주세요.';
    if (formData.password.length < 6) return '비밀번호는 6글자 이상이어야 합니다.';
    if (formData.password !== formData.confirmPassword) return '비밀번호가 일치하지 않습니다.';
    
    return null;
  };

  // 회원가입 제출
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');

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
        onRegisterSuccess();
      } else {
        setError(response.error || '회원가입에 실패했습니다.');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form partner-form">
      <h2>
        <img src="/images/logo_black.png" alt="로고" width="32" height="32" />
        회원가입
      </h2>
      <p className="form-description">소통이(AAC 사용자)를 위한 새 계정 만들기</p>
      
      <form onSubmit={handleSubmit}>
        {/* 계정 정보 */}
        <div className="form-section">
          <h4>
            <img src="/images/account_info.png" alt="로고" width="20" height="20" className="section-icon" />
            계정 정보
          </h4>
          
          <div className="form-group">
            <label htmlFor="userId">
              사용자 ID *
            </label>
            <input
              type="text"
              id="userId"
              name="userId"
              value={formData.userId}
              onChange={handleChange}
              placeholder="로그인에 사용할 ID를 입력하세요 (3글자 이상)"
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">
                비밀번호 *
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="비밀번호 (6글자 이상)"
                disabled={loading}
                autoComplete="new-password"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">
                비밀번호 확인 *
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="비밀번호 재입력"
                disabled={loading}
                autoComplete="new-password"
              />
            </div>
          </div>
        </div>

        {/* 소통이 기본 정보 */}
        <div className="form-section">
          <h4>
            <img src="/images/basic_info.png" alt="로고" width="20" height="20" className="section-icon" />
            소통이(AAC 사용자) 기본 정보
          </h4>
          
          <div className="form-group">
            <label htmlFor="name">이름 또는 닉네임 *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="소통이(AAC 사용자)의 이름이나 닉네임을 입력해주세요"
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
                disabled={loading}
              >
                <option value="">성별 선택</option>
                {GENDER_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 의사소통 정보 */}
        <div className="form-section">
          <h4>
            <img src="/images/communication_info.png" alt="로고" width="20" height="20" className="section-icon" />
            의사소통 정보
          </h4>
          
          <div className="form-group">
            <label htmlFor="disabilityType">장애 유형 *</label>
            <select
              id="disabilityType"
              name="disabilityType"
              value={formData.disabilityType}
              onChange={handleChange}
              disabled={loading}
            >
              <option value="">장애 유형 선택</option>
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
              placeholder="AAC 카드 외에 평소 사용하는 의사소통 방법을 알려주세요.
              예) 간단한 단어나 소리로 의사표현 (응, 아니야, 엄마 등)"
              rows="3"
              disabled={loading}
            />
          </div>
        </div>

        {/* 관심 주제 */}
        <div className="form-section">
          <h4>
            <img src="/images/interest_info.png" alt="로고" width="20" height="20" className="section-icon" />
            관심 주제 *
          </h4>
          
          <div className="form-group">
            <div className="topic-input-section">
              <input
                type="text"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                onKeyPress={handleTopicKeyPress}
                placeholder="예) 음식, 동물, 스포츠..."
                disabled={loading}
              />
              <button 
                type="button" 
                onClick={handleAddTopic}
                disabled={loading || !topicInput.trim()}
                className="secondary-button add-topic-btn"
              >
                추가
              </button>
            </div>
            
            {formData.interestingTopics.length > 0 && (
              <div className="topic-list">
                {formData.interestingTopics.map((topic, index) => (
                  <span key={index} className="topic-tag partner-topic">
                    {topic}
                    <button 
                      type="button" 
                      onClick={() => handleRemoveTopic(topic)}
                      disabled={loading}
                      className="topic-remove"
                    >
                      X
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="error-message partner-error">
            <img src="/images/logo_red.png" alt="로고" width="16" height="16" className="error-icon" />
            {error}
          </div>
        )}
        
        {/* 회원가입 버튼 */}
        <button type="submit" className="primary-button partner-button" disabled={loading}>
          {loading ? '회원가입 중...' : '계정 만들기'}
        </button>
      </form>
      
      {/* 로그인 전환 */}
      <div className="auth-switch">
        <p>
          이미 계정이 있으신가요?  
          <button 
            type="button" 
            className="link-button partner-link" 
            onClick={switchToLogin}
            disabled={loading}
          >
            로그인하기
          </button>
        </p>
      </div>
    </div>
  );
};

export default RegisterForm;