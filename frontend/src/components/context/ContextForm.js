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

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const contextData = {
        userId,
        place: formData.place,
        interactionPartner: formData.interactionPartner,
        currentActivity: formData.currentActivity
      };

      const response = await contextService.createContext(contextData);
      if (response.success) {
        onContextCreated(response.data);
      }
    } catch (error) {
      setError(error.message || '컨텍스트 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="context-form">
      <h2>대화 상황 입력</h2>
      <p>현재 상황을 입력해주세요. 이 정보는 카드 추천과 해석에 사용됩니다.</p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="place">장소 *</label>
          <input
            type="text"
            id="place"
            name="place"
            value={formData.place}
            onChange={handleChange}
            placeholder="예: 집, 학교, 병원, 카페 등"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="interactionPartner">대화 상대 *</label>
          <input
            type="text"
            id="interactionPartner"
            name="interactionPartner"
            value={formData.interactionPartner}
            onChange={handleChange}
            placeholder="예: 엄마, 친구, 선생님, 의사 등"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="currentActivity">현재 활동 (선택사항)</label>
          <input
            type="text"
            id="currentActivity"
            name="currentActivity"
            value={formData.currentActivity}
            onChange={handleChange}
            placeholder="예: 식사 중, 수업 중, 놀이 중 등"
          />
        </div>

        {error && <div className="error-message">{error}</div>}
        
        <button type="submit" disabled={loading}>
          {loading ? '생성 중...' : '컨텍스트 생성'}
        </button>
      </form>
    </div>
  );
};

export { ContextForm };
