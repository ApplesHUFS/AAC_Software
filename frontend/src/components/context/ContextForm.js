// frontend\src\components\context\ContextForm.js
import React, { useState } from 'react';
import { contextService } from '../../services/contextService';

const ContextForm = ({ userId, onContextCreated }) => {
  const [formData, setFormData] = useState({
    place: '',
    interactionPartner: '',
    currentActivity: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 자주 사용되는 예시들
  const PLACE_EXAMPLES = [
    '집', '학교', '병원', '카페', '식당', '공원', '마트', '도서관', '직장', '친구 집'
  ];

  const PARTNER_EXAMPLES = [
    '엄마', '아빠', '형/누나/언니/오빠', '친구', '선생님', '의사', '간호사', '점원', '동료'
  ];

  const ACTIVITY_EXAMPLES = [
    '식사', '공부', '놀이', '치료', '쇼핑', '산책', '운동', '독서', '영화 시청', '게임'
  ];

  // 폼 입력 필드 변경 처리
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

  // 예시 텍스트 클릭으로 자동 입력
  const handleExampleClick = (fieldName, value) => {
    setFormData(prevData => ({
      ...prevData,
      [fieldName]: value
    }));
  };

  // 컨텍스트 생성 폼 제출 처리 (백엔드에서 모든 검증 수행)
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const contextData = {
        userId,
        place: formData.place.trim(),
        interactionPartner: formData.interactionPartner.trim(),
        currentActivity: formData.currentActivity.trim() || ''
      };

      const response = await contextService.createContext(contextData);
      
      if (response.success) {
        onContextCreated(response.data);
      } else {
        setError(response.error || '컨텍스트 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('컨텍스트 생성 에러:', error);
      setError(error.message || '컨텍스트 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="context-form">
      <div className="context-header">
        <h2>대화 상황 입력</h2>
        <p>
          현재 상황을 입력해주세요. 이 정보는 당신의 관심사와 함께 
          가장 적절한 AAC 카드를 추천하는데 사용됩니다.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} noValidate>
        {/* 장소 입력 */}
        <div className="form-group">
          <label htmlFor="place">
            현재 장소 *
            <span className="required-indicator">필수</span>
          </label>
          <input
            type="text"
            id="place"
            name="place"
            value={formData.place}
            onChange={handleChange}
            placeholder="예: 집, 학교, 병원, 카페 등"
            required
            disabled={loading}
          />
          <div className="examples-section">
            <span className="examples-label">자주 사용되는 장소:</span>
            <div className="examples-list">
              {PLACE_EXAMPLES.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  className="example-button"
                  onClick={() => handleExampleClick('place', example)}
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 대화 상대 입력 */}
        <div className="form-group">
          <label htmlFor="interactionPartner">
            대화 상대 *
            <span className="required-indicator">필수</span>
          </label>
          <input
            type="text"
            id="interactionPartner"
            name="interactionPartner"
            value={formData.interactionPartner}
            onChange={handleChange}
            placeholder="예: 엄마, 친구, 선생님, 의사 등"
            required
            disabled={loading}
          />
          <div className="examples-section">
            <span className="examples-label">자주 사용되는 대화 상대:</span>
            <div className="examples-list">
              {PARTNER_EXAMPLES.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  className="example-button"
                  onClick={() => handleExampleClick('interactionPartner', example)}
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 현재 활동 입력 (선택사항) */}
        <div className="form-group">
          <label htmlFor="currentActivity">
            현재 활동
            <span className="optional-indicator">선택사항</span>
          </label>
          <input
            type="text"
            id="currentActivity"
            name="currentActivity"
            value={formData.currentActivity}
            onChange={handleChange}
            placeholder="예: 식사 중, 수업 중, 놀이 중 등 (비워두어도 됩니다)"
            disabled={loading}
          />
          <div className="examples-section">
            <span className="examples-label">자주 사용되는 활동:</span>
            <div className="examples-list">
              {ACTIVITY_EXAMPLES.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  className="example-button"
                  onClick={() => handleExampleClick('currentActivity', example)}
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
          <small className="form-hint">
            현재 하고 있는 구체적인 활동이 있다면 입력해주세요. 
            더 정확한 카드 추천에 도움이 됩니다.
          </small>
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}
        
        <div className="form-actions">
          <button 
            type="submit" 
            className="primary-button large"
            disabled={loading}
          >
            {loading ? '컨텍스트 생성 중...' : 'AAC 카드 추천받기'}
          </button>
        </div>

        <div className="context-help">
          <h4>입력 가이드</h4>
          <ul>
            <li><strong>장소:</strong> 구체적인 위치를 입력하면 상황에 맞는 카드를 추천받을 수 있어요</li>
            <li><strong>대화 상대:</strong> 관계에 따라 적절한 표현 방식이 달라져요</li>
            <li><strong>현재 활동:</strong> 하고 있는 일이 명확하면 더 정확한 추천이 가능해요</li>
          </ul>
        </div>
      </form>
    </div>
  );
};

export { ContextForm };