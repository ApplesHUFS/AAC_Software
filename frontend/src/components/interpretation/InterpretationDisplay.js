import React from 'react';

const InterpretationDisplay = ({ interpretations, selectedCards, contextInfo, onSelectInterpretation, selectedIndex }) => {
  return (
    <div className="interpretation-display">
      <div className="interpretation-header">
        <h2>카드 해석 결과</h2>
        <div className="context-summary">
          <p><strong>상황:</strong> {contextInfo.place}에서 {contextInfo.interactionPartner}와</p>
          {contextInfo.currentActivity && (
            <p><strong>활동:</strong> {contextInfo.currentActivity}</p>
          )}
          <p><strong>시간:</strong> {contextInfo.time}</p>
        </div>
      </div>

      <div className="selected-cards-summary">
        <h3>선택된 카드</h3>
        <div className="cards-preview">
          {selectedCards.map((card) => (
            <div key={card.filename} className="card-preview">
              <img src={`http://localhost:8000${card.imagePath}`} alt={card.name} />
              <span>{card.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="interpretations-list">
        <h3>가능한 해석 (3가지)</h3>
        <p>Partner가 가장 적절한 해석을 선택해주세요:</p>
        
        {interpretations.map((interpretation, index) => (
          <div 
            key={index}
            className={`interpretation-item ${selectedIndex === index ? 'selected' : ''}`}
            onClick={() => onSelectInterpretation(index)}
          >
            <div className="interpretation-number">{index + 1}</div>
            <div className="interpretation-text">{interpretation.text}</div>
            {selectedIndex === index && <div className="selection-indicator">선택됨</div>}
          </div>
        ))}
      </div>
    </div>
  );
};
