import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../services/api';
import '../styles/UserCreatePage.css';

const UserCreatePage = () => {
  const [userName, setUserName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userName.trim()) {
      setError('사용자 이름을 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await userAPI.createUser({ name: userName });
      const userId = response.data.id;

      localStorage.setItem('userId', userId);
      navigate('/persona/input');
    } catch (err) {
      setError('사용자 생성 중 오류가 발생했습니다.');
      console.error('Error creating user:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="user-create-page">
      <div className="container">
        <h2>사용자 생성</h2>
        <p className="subtitle">AAC 해석 시스템을 사용하기 위해 사용자 정보를 입력해주세요.</p>

        <form onSubmit={handleSubmit} className="user-form">
          <div className="form-group">
            <label htmlFor="userName">사용자 이름</label>
            <input
              type="text"
              id="userName"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="이름을 입력하세요"
              disabled={isLoading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            className="submit-button"
            disabled={isLoading || !userName.trim()}
          >
            {isLoading ? '생성 중...' : '다음 단계'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UserCreatePage;
