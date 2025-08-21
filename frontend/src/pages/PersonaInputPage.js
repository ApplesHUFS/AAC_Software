import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import '../styles/PersonaInputPage.css';

const PersonaInputPage = () => {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    disability_type: '',
    communication_characteristics: '',
    interesting_topics: ''
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

    if (!formData.age || !formData.gender || !formData.disability_type) {
      setError('필수 항목을 모두 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const userId = localStorage.getItem('userId');
      await userAPI.updatePersona(userId, formData);

      navigate('/context/input');
    } catch (err) {
      setError('페르소나 정보 저장 중 오류가 발생했습니다.');
      console.error('Error saving persona:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="persona-input-page">
      <div className="container">
        <h2>페르소나 정보 입력</h2>
        <p className="subtitle">사용자의 특성을 입력하여 더 정확한 카드 추천을 받아보세요.</p>

        <form onSubmit={handleSubmit} className="persona-form">
          <div className="form-group">
            <label htmlFor="age">나이 *</label>
            <input
              type="number"
              id="age"
              name="age"
              value={formData.age}
              onChange={handleInputChange}
              placeholder="나이를 입력하세요"
              min="1"
              max="100"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="gender">성별 *</label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleInputChange}
              disabled={isLoading}
            >
              <option value="">선택하세요</option>
              <option value="male">남성</option>
              <option value="female">여성</option>
              <option value="other">기타</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="disability_type">장애 유형 *</label>
            <select
              id="disability_type"
              name="disability_type"
              value={formData.disability_type}
              onChange={handleInputChange}
              disabled={isLoading}
            >
              <option value="">선택하세요</option>
              <option value="intellectual">지적장애</option>
              <option value="autism">자폐스펙트럼장애</option>
              <option value="communication">의사소통장애</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="communication_characteristics">의사소통 특징</label>
            <textarea
              id="communication_characteristics"
              name="communication_characteristics"
              value={formData.communication_characteristics}
              onChange={handleInputChange}
              placeholder="의사소통할 때의 특징을 자유롭게 작성해주세요 (예: 짧은 문장 선호, 제스처 많이 사용 등)"
              rows="3"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="interesting_topics">관심 주제</label>
            <textarea
              id="interesting_topics"
              name="interesting_topics"
              value={formData.interesting_topics}
              onChange={handleInputChange}
              placeholder="관심 있는 주제를 입력해주세요 (예: 음식, 동물, 스포츠, 음악 등)"
              rows="3"
              disabled={isLoading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="button-group">
            <button
              type="button"
              className="back-button"
              onClick={() => navigate('/user/create')}
              disabled={isLoading}
            >
              이전
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={isLoading}
            >
              {isLoading ? '저장 중...' : '다음 단계'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PersonaInputPage;
