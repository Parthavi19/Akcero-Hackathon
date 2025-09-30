import React from "react";
import "./MeetingParticipants.css";

const DEFAULT_AVATAR = "https://www.gravatar.com/avatar/?d=mp&s=200";

function MeetingParticipants({ participants = [] }) {
  const handleImageError = (e) => {
    e.target.src = DEFAULT_AVATAR;
  };

  if (participants.length === 0) {
    return (
      <div className="participants-empty">
        <p>No participants added yet</p>
      </div>
    );
  }

  return (
    <div className="participants-container">
      <h3 className="participants-title">Meeting Participants</h3>
      <div className="participants-grid">
        {participants.map((participant, index) => (
          <div key={participant.id || index} className="participant-card">
            <div className="participant-avatar-wrapper">
              <img
                src={participant.avatar || DEFAULT_AVATAR}
                alt={participant.name}
                className="participant-avatar"
                onError={handleImageError}
              />
              <div className="participant-status"></div>
            </div>
            <div className="participant-info">
              <h4 className="participant-name">{participant.name}</h4>
              {participant.email && (
                <p className="participant-email">{participant.email}</p>
              )}
              {participant.role && (
                <span className="participant-role">{participant.role}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MeetingParticipants;
