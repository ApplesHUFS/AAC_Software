import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { contextAPI } from '../services/api';
import '../styles/ContextInputPage.css';

const ContextInputPage = () => {
  const [formData, setFormData] = useState({
    time: new Date().toISOString().slice(0, 16),
    place: '',
    interaction_partner: '',
    current_activity: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (!userId) {
      navigate('/user/create');
    }
  }, [navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.place || !formData.interaction_partner) {
      setError('장소와 상대방 정보를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const userId = localStorage.getItem('userId');
      const contextData = {
        ...formData,
        userId
      };

      const response = await contextAPI.createContext(contextData);
      localStorage.setItem('contextId', response.data.id);

      navigate('/cards/recommendation');
    } catch (err) {
      setError('컨텍스트 정보 저장 중 오류가 발생했습니다.');
      console.error('Error saving context:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="context-input-page">
      <div className="container">
        <h2>대화 상황 정보</h2>
        <p className="subtitle">현재 대화 상황에 대한 정보를 입력해주세요.</p>

        <form onSubmit={handleSubmit} className="context-form">
          <div className="form-group">
            <label htmlFor="time">시간</label>
            <input
              type="datetime-local"
              id="time"
              name="time"
              value={formData.time}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="place">장소 *</label>
            <input
              type="text"
              id="place"
              name="place"
              value={formData.place}
              onChange={handleInputChange}
              placeholder="현재 있는 장소를 입력하세요 (예: 집, 학교, 카페 등)"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="interaction_partner">대화 상대 *</label>
            <input
              type="text"
              id="interaction_partner"
              name="interaction_partner"
              value={formData.interaction_partner}
              onChange={handleInputChange}
              placeholder="대화하는 상대방과의 관계를 입력하세요 (예: 엄마, 친구, 선생님 등)"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="current_activity">현재 활동 (선택사항)</label>
            <textarea
              id="current_activity"
              name="current_activity"
              value={formData.current_activity}
              onChange={handleInputChange}
              placeholder="현재 하고 있는 활동이나 상황을 설명해주세요 (예: 점심 먹기, 숙제하기, 놀이하기 등)"
              rows="3"
              disabled={isLoading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="button-group">
            <button
              type="button"
              className="back-button"
              onClick={() => navigate('/persona/input')}
              disabled={isLoading}
            >
              이전
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={isLoading}
            >
              {isLoading ? '저장 중...' : '카드 추천받기'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContextInputPage;
