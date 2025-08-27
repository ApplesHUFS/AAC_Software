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

  const GENDER_OPTIONS = ['남성', '여성'];
  const DISABILITY_OPTIONS = ['지적장애', '자폐스펙트럼장애', '의사소통장애'];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleAddTopic = () => {
    if (topicInput.trim() && !formData.interestingTopics.includes(topicInput.trim())) {
      setFormData({
        ...formData,
        interestingTopics: [...formData.interestingTopics, topicInput.trim()]
      });
      setTopicInput('');
    }
  };

  const handleRemoveTopic = (topicToRemove) => {
    setFormData({
      ...formData,
      interestingTopics: formData.interestingTopics.filter(topic => topic !== topicToRemove)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.interestingTopics.length === 0) {
      setError('관심 주제를 최소 1개 이상 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      const response = await authService.register(formData);
      if (response.success) {
        onRegisterSuccess(response.data);
      }
    } catch (error) {
      setError(error.message || '회원가입에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>회원가입</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="userId">사용자 ID</label>
          <input
            type="text"
            id="userId"
            name="userId"
            value={formData.userId}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="name">이름</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="age">나이</label>
          <input
            type="number"
            id="age"
            name="age"
            min="1"
            max="100"
            value={formData.age}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="gender">성별</label>
          <select
            id="gender"
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            required
          >
            <option value="">선택해주세요</option>
            {GENDER_OPTIONS.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="disabilityType">장애 유형</label>
          <select
            id="disabilityType"
            name="disabilityType"
            value={formData.disabilityType}
            onChange={handleChange}
            required
          >
            <option value="">선택해주세요</option>
            {DISABILITY_OPTIONS.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="communicationCharacteristics">의사소통 특징</label>
          <textarea
            id="communicationCharacteristics"
            name="communicationCharacteristics"
            value={formData.communicationCharacteristics}
            onChange={handleChange}
            placeholder="AAC 카드 사용이 아닌 일반적인 의사소통 시의 특징을 입력해주세요"
            required
          />
        </div>

        <div className="form-group">
          <label>관심 주제</label>
          <div className="topic-input-section">
            <input
              type="text"
              value={topicInput}
              onChange={(e) => setTopicInput(e.target.value)}
              placeholder="관심 주제를 입력하고 추가 버튼을 클릭하세요"
            />
            <button type="button" onClick={handleAddTopic}>추가</button>
          </div>
          
          <div className="topic-list">
            {formData.interestingTopics.map((topic, index) => (
              <span key={index} className="topic-tag">
                {topic}
                <button type="button" onClick={() => handleRemoveTopic(topic)}>×</button>
              </span>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="password">비밀번호</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>

        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" disabled={loading}>
          {loading ? '가입 중...' : '회원가입'}
        </button>
      </form>
      
      <p>
        이미 계정이 있으신가요? 
        <button type="button" className="link-button" onClick={switchToLogin}>
          로그인
        </button>
      </p>
    </div>
  );
};

export { RegisterForm };