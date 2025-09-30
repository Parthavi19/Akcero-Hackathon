// src/components/AvatarExplainer.jsx
import React, { useState, useContext } from "react";
import axios from "axios";
import { MeetingContext } from "../context/MeetingContext";

export default function AvatarExplainer({ meetingId: propMeetingId }) {
  const { meetingId: ctxMeetingId } = useContext(MeetingContext);
  const meetingId = propMeetingId || ctxMeetingId;

  const [audioUrl, setAudioUrl] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const generateAvatar = async () => {
    if (!meetingId) return;
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/meetings/${meetingId}/avatar`);
      setAudioUrl(res.data.audio_path);
      setText(res.data.text);
    } catch (err) {
      console.error("Avatar generation failed", err);
      alert("Avatar generation failed: " + (err?.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="avatar-explainer">
      <h2>Avatar Explainer</h2>
      <p>Generates a spoken summary (audio) from the meeting transcript.</p>
      <button onClick={generateAvatar} disabled={!meetingId || loading}>
        {loading ? "Generating..." : "Generate & Play Avatar Explanation"}
      </button>

      {text && (
        <div className="avatar-text">
          <h4>Summary Text</h4>
          <p>{text}</p>
        </div>
      )}

      {audioUrl && (
        <div className="avatar-audio">
          <audio controls src={`http://localhost:8000${audioUrl}`} />
        </div>
      )}
    </div>
  );
}

