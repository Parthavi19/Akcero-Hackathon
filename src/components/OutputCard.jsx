import React from "react";
import PropTypes from "prop-types";
import "./OutputCard.css";

function OutputCard({ title, desc, color, isSelected, onSelect }) {
  return (
    <div 
      className={`output-card ${color} ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
    >
      <div className="card-header">
        <h3>{title}</h3>
        {isSelected && <div className="checkmark">✓</div>}
      </div>
      <p className="card-desc">{desc}</p>
      <div className="card-action">
        {isSelected ? 'Selected' : 'Click to add'}
      </div>
    </div>
  );
}

OutputCard.propTypes = {
  title: PropTypes.string.isRequired,
  desc: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  isSelected: PropTypes.bool.isRequired,
  onSelect: PropTypes.func.isRequired,
};

export default OutputCard;
