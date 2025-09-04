// src/components/auth/RegisterForm.js
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
    password: ''
  });
  const [topicInput, setTopicInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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

  // 클라이언트 사이드 유효성 검증
  const validateForm = () => {
    const required = ['userId', 'name', 'age', 'gender', 'disabilityType', 'communicationCharacteristics', 'password'];
    
    for (const field of required) {
      if (!formData[field]?.toString().trim()) {
        return `${getFieldName(field)}을(를) 입력해주세요.`;
      }
    }

    if (formData.interestingTopics.length === 0) {
      return '관심 주제를 최소 1개 이상 입력해주세요.';
    }

    if (formData.age < 1 || formData.age > 100) {
      return '나이는 1~100세 사이로 입력해주세요.';
    }

    if (formData.password.length < 4) {
      return '비밀번호는 4자 이상 입력해주세요.';
    }

    return null;
  };

  const getFieldName = (field) => {
    const names = {
      userId: '사용자 ID',
      name: '이름',
      age: '나이',
      gender: '성별',
      disabilityType: '장애 유형',
      communicationCharacteristics: '의사소통 특징',
      password: '비밀번호'
    };
    return names[field] || field;
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
        onRegisterSuccess(response.data);
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
    <div className="auth-form partner-form register-form">
      <h2>
        <span className="form-icon">👥</span>
        소통이 계정 만들기
      </h2>
      <p className="form-description">
        소통이의 개인 맞춤 AAC 서비스를 위한 정보를 입력해주세요. 
        <br />이름은 닉네임도 사용할 수 있어요.
      </p>
      
      <form onSubmit={handleSubmit}>
        {/* 기본 정보 */}
        <div className="form-section">
          <h4>
            <span className="section-icon">📋</span>
            기본 정보
          </h4>
          
          <div className="form-group">
            <label htmlFor="userId">사용자 ID *</label>
            <input
              type="text"
              id="userId"
              name="userId"
              value={formData.userId}
              onChange={handleChange}
              placeholder="로그인에 사용할 ID를 입력하세요"
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="name">이름 (닉네임 가능) *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="소통이의 이름이나 원하는 닉네임을 입력해주세요"
              disabled={loading}
              autoComplete="name"
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
          <h4>
            <span className="section-icon">💬</span>
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
              placeholder="AAC 카드 사용이 아닌 평소 의사소통 방식의 특징을 간단히 적어주세요 (예: 짧은 단어로 말함, 제스처 자주 사용 등)"
              rows="3"
              disabled={loading}
            />
          </div>
        </div>

        {/* 관심 주제 */}
        <div className="form-section">
          <h4>
            <span className="section-icon">❤️</span>
            소통이의 관심 주제 *
          </h4>
          
          <div className="form-group">
            <div className="topic-input-section">
              <input
                type="text"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                onKeyPress={handleTopicKeyPress}
                placeholder="소통이가 좋아하는 것들을 입력해주세요 (예: 동물, 음식, 게임 등)"
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
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 비밀번호 */}
        <div className="form-section">
          <div className="form-group">
            <label htmlFor="password">
              <span className="label-icon">🔒</span>
              비밀번호 *
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="4자 이상의 비밀번호를 입력하세요"
              disabled={loading}
              autoComplete="new-password"
            />
          </div>
        </div>

        {error && (
          <div className="error-message partner-error">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
        
        <button type="submit" className="primary-button partner-button large" disabled={loading}>
          {loading ? '계정 만드는 중...' : '소통이 계정 만들기'}
        </button>
      </form>
      
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

export { LoginForm, RegisterForm };