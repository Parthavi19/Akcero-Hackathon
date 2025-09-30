import "./OptionCard.css";

function OptionCard({ title, desc, icon, color, onSelect }) {
  return (
    <div className={`option-card ${color}`} onClick={onSelect}>
      <div className="icon">{icon}</div>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  );
}

export default OptionCard;
