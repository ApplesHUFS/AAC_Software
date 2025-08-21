import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import '../styles/UserCreatePage.css';

const UserCreatePage = () => {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    disability_type: '',
    communication_characteristics: '',
    interesting_topics: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // 필수 입력 검증
    if (!formData.name.trim()) {
      setError('사용자 이름을 입력해주세요.');
      return;
    }
    if (!formData.age) {
      setError('나이를 입력해주세요.');
      return;
    }
    if (!formData.gender) {
      setError('성별을 선택해주세요.');
      return;
    }
    if (!formData.disability_type) {
      setError('장애 유형을 선택해주세요.');
      return;
    }
    if (!formData.password) {
      setError('비밀번호를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // interesting_topics를 배열로 변환
      const userData = {
        ...formData,
        age: parseInt(formData.age),
        interesting_topics: formData.interesting_topics
          ? formData.interesting_topics.split(',').map(topic => topic.trim()).filter(topic => topic)
          : []
      };

      const response = await userAPI.createUser(userData);
      const userId = response.data.id;

      localStorage.setItem('userId', userId);
      localStorage.setItem('userName', formData.name);

      // 모든 정보를 한 번에 입력했으므로 바로 컨텍스트 입력으로 이동
      navigate('/context/input');
    } catch (err) {
      const errorMessage = err.response?.data?.error || '사용자 생성 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('Error creating user:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="user-create-page">
      <div className="container">
        <h2>사용자 생성 및 페르소나 입력</h2>
        <p className="subtitle">AAC 해석 시스템을 사용하기 위해 사용자 정보를 입력해주세요.</p>

        <form onSubmit={handleSubmit} className="user-form">
          <div className="form-group">
            <label htmlFor="name">사용자 이름 *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="이름을 입력하세요"
              disabled={isLoading}
              required
            />
          </div>

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
              required
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
              required
            >
              <option value="">성별을 선택하세요</option>
              <option value="남성">남성</option>
              <option value="여성">여성</option>
              <option value="기타">기타</option>
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
              required
            >
              <option value="">장애 유형을 선택하세요</option>
              <option value="지적장애">지적장애</option>
              <option value="자폐스펙트럼장애">자폐스펙트럼장애</option>
              <option value="의사소통장애">의사소통장애</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="communication_characteristics">의사소통 특징</label>
            <textarea
              id="communication_characteristics"
              name="communication_characteristics"
              value={formData.communication_characteristics}
              onChange={handleInputChange}
              placeholder="AAC 카드 사용이 아닌 의사소통 할 때의 특징을 입력하세요"
              rows="3"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="interesting_topics">관심 주제</label>
            <input
              type="text"
              id="interesting_topics"
              name="interesting_topics"
              value={formData.interesting_topics}
              onChange={handleInputChange}
              placeholder="관심 있는 주제들을 쉼표(,)로 구분하여 입력하세요 (예: 음식, 스포츠, 음악)"
              disabled={isLoading}
            />
            <small className="input-help">
              입력한 관심 주제를 바탕으로 개인화된 카드를 추천합니다.
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호 *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="비밀번호를 입력하세요"
              disabled={isLoading}
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? '생성 중...' : '사용자 생성 완료'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UserCreatePage;
