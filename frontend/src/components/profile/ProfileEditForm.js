// src/components/profile/ProfileEditForm.js
import React, { useState } from 'react';
import { authService } from '../../services/authService';

// 선택지 옵션들
const GENDER_OPTIONS = ['남성', '여성'];
const DISABILITY_OPTIONS = ['지적장애', '자폐스펙트럼장애', '의사소통장애'];

const ProfileEditForm = ({ user, onProfileUpdated, onCancel }) => {
  const [formData, setFormData] = useState({
    name: user.name || '',
    age: user.age || '',
    gender: user.gender || '',
    disabilityType: user.disabilityType || '',
    communicationCharacteristics: user.communicationCharacteristics || '',
    interestingTopics: [...(user.interestingTopics || [])]
  });
  const [topicInput, setTopicInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError('');
    if (success) setSuccess('');
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

  const handleTopicKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTopic();
    }
  };

  // 변경사항 확인
  const hasChanges = () => {
    return (
      formData.name !== user.name ||
      formData.age !== user.age ||
      formData.gender !== user.gender ||
      formData.disabilityType !== user.disabilityType ||
      formData.communicationCharacteristics !== user.communicationCharacteristics ||
      JSON.stringify(formData.interestingTopics.sort()) !== JSON.stringify((user.interestingTopics || []).sort())
    );
  };

  // 유효성 검증
  const validateForm = () => {
    if (!formData.name.trim()) return '이름을 입력해주세요.';
    if (!formData.age || formData.age < 1 || formData.age > 100) return '나이는 1~100세 사이로 입력해주세요.';
    if (!formData.gender) return '성별을 선택해주세요.';
    if (!formData.disabilityType) return '장애 유형을 선택해주세요.';
    if (!formData.communicationCharacteristics.trim()) return '의사소통 특징을 입력해주세요.';
    if (formData.interestingTopics.length === 0) return '관심 주제를 최소 1개 이상 입력해주세요.';
    
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    if (!hasChanges()) {
      setError('변경된 내용이 없습니다.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const updateData = {
        name: formData.name.trim(),
        age: parseInt(formData.age),
        gender: formData.gender,
        disabilityType: formData.disabilityType,
        communicationCharacteristics: formData.communicationCharacteristics.trim(),
        interestingTopics: formData.interestingTopics
      };

      const response = await authService.updateProfile(user.userId, updateData);
      
      if (response.success) {
        setSuccess('프로필이 성공적으로 업데이트되었습니다.');
        
        // 업데이트된 사용자 정보 생성
        const updatedUser = {
          ...user,
          ...updateData
        };
        
        setTimeout(() => {
          onProfileUpdated(updatedUser);
        }, 1500);
      } else {
        setError(response.error || '프로필 업데이트에 실패했습니다.');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-edit-form">
      <div className="form-header">
        <h2>프로필 편집</h2>
        <p>개인화된 서비스 제공을 위한 정보를 수정할 수 있습니다.</p>
      </div>
      
      <form onSubmit={handleSubmit}>
        {/* 기본 정보 */}
        <div className="form-section">
          <h4>기본 정보</h4>
          
          <div className="form-group">
            <label htmlFor="name">이름 *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="이름을 입력해주세요"
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
                <option value="">선택해주세요</option>
                {GENDER_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 장애 및 의사소통 정보 */}
        <div className="form-section">
          <h4>의사소통 정보</h4>
          
          <div className="form-group">
            <label htmlFor="disabilityType">장애 유형 *</label>
            <select
              id="disabilityType"
              name="disabilityType"
              value={formData.disabilityType}
              onChange={handleChange}
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
              rows="3"
              disabled={loading}
            />
          </div>
        </div>

        {/* 관심 주제 */}
        <div className="form-section">
          <h4>관심 주제 *</h4>
          
          <div className="form-group">
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
            
            {formData.interestingTopics.length > 0 && (
              <div className="topic-list">
                {formData.interestingTopics.map((topic, index) => (
                  <span key={index} className="topic-tag">
                    {topic}
                    <button 
                      type="button" 
                      onClick={() => handleRemoveTopic(topic)}
                      disabled={loading}
                      className="topic-remove"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 메시지 */}
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        {/* 액션 버튼 */}
        <div className="form-actions">
          <button 
            type="button" 
            className="secondary-button" 
            onClick={onCancel}
            disabled={loading}
          >
            취소
          </button>
          <button 
            type="submit" 
            className="primary-button" 
            disabled={loading || !hasChanges()}
          >
            {loading ? '저장 중...' : '변경사항 저장'}
          </button>
        </div>

        {/* 변경 사항 알림 */}
        {hasChanges() && !loading && (
          <div className="changes-notice">
            변경된 내용이 있습니다. 저장하시겠습니까?
          </div>
        )}
      </form>
    </div>
  );
};

export default ProfileEditForm;