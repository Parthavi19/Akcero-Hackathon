// src/components/Chatbot.jsx
import React, { useState, useContext } from "react";
import axios from "axios";
import { MeetingContext } from "../context/MeetingContext";

export default function Chatbot({ meetingId: propMeetingId }) {
  const { meetingId: ctxMeetingId } = useContext(MeetingContext);
  const meetingId = propMeetingId || ctxMeetingId;

  const [history, setHistory] = useState([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!q.trim() || !meetingId) return;
    setLoading(true);
    try {
      const res = await axios.post(`http://localhost:8000/meetings/${meetingId}/chat`, { question: q });
      setHistory(prev => [...prev, { question: res.data.question, answer: res.data.answer }]);
      setQ("");
    } catch (err) {
      console.error("Chat error", err);
      setHistory(prev => [...prev, { question: q, answer: "Error answering question." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot">
      <h2>Smart Chatbot (Q&A)</h2>
      {!meetingId && <p>No meeting selected.</p>}
      <div className="chat-window">
        {history.map((h, idx) => (
          <div key={idx} className="chat-entry">
            <div className="q"><strong>You:</strong> {h.question}</div>
            <div className="a"><strong>Bot:</strong> {h.answer}</div>
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask something about the meeting..." />
        <button onClick={askQuestion} disabled={!q.trim() || loading}>Ask</button>
      </div>
    </div>
  );
}

