import CardItem from './CardItem';
import '../../styles/CardGrid.css';

const CardGrid = ({ cards, selectedCards, onCardSelect, maxSelection = 4 }) => {
  return (
    <div className="card-grid">
      {cards.map(card => (
        <CardItem
          key={card.id}
          card={card}
          isSelected={selectedCards.includes(card.id)}
          onSelect={(isSelected) => onCardSelect(card.id, isSelected)}
          disabled={!selectedCards.includes(card.id) && selectedCards.length >= maxSelection}
        />
      ))}
    </div>
  );
};

export default CardGrid;
