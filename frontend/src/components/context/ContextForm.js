// src/components/context/ContextForm.js
import React, { useState } from 'react';
import { contextService } from '../../services/contextService';

// 자주 사용되는 예시들
const PLACE_EXAMPLES = [
  '집', '학교', '병원', '카페', '식당', '공원', '마트', '도서관', '직장', '친구 집'
];

const PARTNER_EXAMPLES = [
  '엄마', '아빠', '형', '누나', '언니', '오빠', '동생', '친구', '선생님', '의사', '간호사', '점원', '동료'
];

const ACTIVITY_EXAMPLES = [
  '식사', '공부', '놀이', '일', '치료', '쇼핑', '산책', '운동', '독서', '영화 시청', '게임'
];

const ContextForm = ({ userId, onContextCreated }) => {
  const [formData, setFormData] = useState({
    place: '',
    interactionPartner: '',
    currentActivity: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  // 예시 클릭으로 자동 입력
  const handleExampleClick = (fieldName, value) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }));
    setError('');
  };

  // 유효성 검증
  const validateForm = () => {
    if (!formData.place.trim()) return '현재 장소를 입력해주세요.';
    if (!formData.interactionPartner.trim()) return '대화 상대를 입력해주세요.';
    return null;
  };

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
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="context-form partner-theme">
      <div className="context-header">
        <div className="role-indicator partner-role">
          <span>도움이 상황 입력</span>
        </div>
        <h2>
          지금 어떤 상황인가요?
        </h2>
        <p style={{ whiteSpace: 'pre-line' }}>
          소통이의 현재 상황을 입력해주시면 소통이에게 딱 맞는 AAC 카드를 추천해드려요.{'\n'}
          상황에 맞는 카드를 통해 더 원활한 소통이 가능해집니다.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* 장소 입력 */}
        <div className="form-group">
          <label htmlFor="place">
            <img src="/images/place.png" alt="로고" width="20" height="20" className="label-icon" />
            현재 장소 *
          </label>
          <input
            type="text"
            id="place"
            name="place"
            value={formData.place}
            onChange={handleChange}
            placeholder="지금 어디에 있나요? (예: 집, 학교, 병원, 카페 등)"
            disabled={loading}
            className="context-input"
          />
          <div className="examples-section">
            <span className="examples-label">자주 입력하는 장소:</span>
            <div className="examples-list">
              {PLACE_EXAMPLES.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  className="example-button partner-example"
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
            <img src="/images/interactionPartner.png" alt="로고" width="20" height="20" className="label-icon" />
            대화 상대 *
          </label>
          <input
            type="text"
            id="interactionPartner"
            name="interactionPartner"
            value={formData.interactionPartner}
            onChange={handleChange}
            placeholder="누구와 대화하나요? (예: 엄마, 친구, 선생님, 의사 등)"
            disabled={loading}
            className="context-input"
          />
          <div className="examples-section">
            <span className="examples-label">자주 입력하는 대화 상대:</span>
            <div className="examples-list">
              {PARTNER_EXAMPLES.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  className="example-button partner-example"
                  onClick={() => handleExampleClick('interactionPartner', example)}
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 현재 활동 입력 */}
        <div className="form-group">
          <label htmlFor="currentActivity">
            <img src="/images/currentActivity.png" alt="로고" width="20" height="20" className="label-icon" />
            현재 활동 (선택사항)
          </label>
          <input
            type="text"
            id="currentActivity"
            name="currentActivity"
            value={formData.currentActivity}
            onChange={handleChange}
            placeholder="지금 무엇을 하고 있나요? (예: 식사 중, 수업 중, 놀이 중 등)"
            disabled={loading}
            className="context-input"
          />
          <div className="examples-section">
            <span className="examples-label">자주 입력하는 활동:</span>
            <div className="examples-list">
              {ACTIVITY_EXAMPLES.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  className="example-button partner-example"
                  onClick={() => handleExampleClick('currentActivity', example)}
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
          <small className="form-hint"
          style={{
            marginTop: '20px',
            display: 'block',
            lineHeight: '2'
       }}>
            현재 하고 있는 구체적인 활동을 입력하시면
            더 정확한 카드 추천을 받을 수 있어요.
          </small>
        </div>

        {error && (
          <div className="error-message partner-error">
            <img src="/images/error.png" alt="로고" width="16" height="16" className="error-icon" />
            {error}
          </div>
        )}

        <div className="form-actions">
          <button type="submit" className="primary-button partner-button large" disabled={loading}>
            {loading ? (
              <>
                <span className="button-spinner"></span>
                카드 추천 준비 중...
              </>
            ) : (
              <>
                맞춤 카드 추천하기
              </>
            )}
          </button>
        </div>

        <div className="context-help">
          <h4>
            <img src="/images/use_info.png" alt="로고" width="24" height="24" className="help-icon" />
            입력 도움말
          </h4>
          <div className="help-grid">
            <div className="help-item">
              <strong>장소</strong>
              <p>구체적인 위치를 입력하면 상황에 딱 맞는 카드를 추천받아요</p>
            </div>
            <div className="help-item">
              <strong>대화 상대</strong>
              <p>관계에 따라 적절한 표현 방식과 카드가 달라져요</p>
            </div>
            <div className="help-item">
              <strong>현재 활동</strong>
              <p>하고 있는 일이 명확하면 더 정확한 카드 추천이 가능해요</p>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ContextForm;
