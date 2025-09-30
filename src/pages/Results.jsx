import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import "./Results.css";

function Results() {
  const navigate = useNavigate();
  const location = useLocation();
  const { selected, meetingId } = location.state || {};

  const [summary, setSummary] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [actionItems, setActionItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingComplete, setProcessingComplete] = useState(false);
  const [error, setError] = useState(null);

  // Chatbot states
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  // Avatar audio
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioError, setAudioError] = useState(null);

  useEffect(() => {
    if (!meetingId) {
      setError("No meeting ID provided.");
      setLoading(false);
      return;
    }

    let pollInterval;
    let pollCount = 0;
    const MAX_POLLS = 60; // Poll for up to 5 minutes (60 * 5 seconds)

    const fetchData = async () => {
      try {
        const [s, d, a] = await Promise.all([
          axios.get(`http://localhost:8000/meetings/${meetingId}/summary`),
          axios.get(`http://localhost:8000/meetings/${meetingId}/decisions`),
          axios.get(`http://localhost:8000/meetings/${meetingId}/action-items`),
        ]);
        
        setSummary(s.data);
        setDecisions(d.data);
        setActionItems(a.data);

        // Check if processing is complete
        if (s.data.length > 0 || d.data.length > 0 || a.data.length > 0) {
          setProcessingComplete(true);
          setLoading(false);
          if (pollInterval) clearInterval(pollInterval);
          return true;
        }
        return false;
      } catch (error) {
        console.error("Error fetching results:", error);
        setError("Failed to fetch results. Please try again.");
        return false;
      }
    };

    // Initial fetch
    fetchData().then((hasData) => {
      if (hasData) return;

      // Start polling if no data yet
      pollInterval = setInterval(async () => {
        pollCount++;
        console.log(`Polling attempt ${pollCount}...`);

        const hasData = await fetchData();
        
        if (hasData || pollCount >= MAX_POLLS) {
          clearInterval(pollInterval);
          setLoading(false);
          if (!hasData) {
            setError("Processing timed out. No data generated.");
          }
        }
      }, 5000); // Poll every 5 seconds
    });

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [meetingId]);

  const sendChat = async () => {
    if (!question.trim()) return;
    setChatLoading(true);

    const newUserMessage = { sender: "user", text: question };
    setMessages((prev) => [...prev, newUserMessage]);

    try {
      const res = await axios.post(
        `http://localhost:8000/meetings/${meetingId}/chat`,
        { question }
      );
      const newBotMessage = { sender: "bot", text: res.data.answer };
      setMessages((prev) => [...prev, newBotMessage]);
    } catch (error) {
      console.error("Chatbot error:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "⚠️ Error fetching chatbot response." },
      ]);
    } finally {
      setQuestion("");
      setChatLoading(false);
    }
  };

  const fetchAvatarAudio = async () => {
    try {
      setAudioError(null);
      setAudioUrl(`http://localhost:8000/meetings/${meetingId}/avatar?ts=${Date.now()}`);
    } catch (error) {
      console.error("Error fetching avatar audio:", error);
      setAudioError("Failed to generate audio. Try again later.");
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Processing your meeting... This may take a moment.</p>
        <p style={{ fontSize: "0.9em", marginTop: "10px", opacity: 0.7 }}>
          We're generating summaries, extracting decisions, and creating action items.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>{error}</p>
        <button onClick={() => navigate(-1)}>Go Back</button>
      </div>
    );
  }

  return (
    <div className="results">
      <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>
      <h1>Results ✨</h1>

      {!processingComplete && (
        <div className="warning-box" style={{ 
          background: "#fff3cd", 
          padding: "15px", 
          borderRadius: "8px", 
          marginBottom: "20px",
          border: "1px solid #ffc107" 
        }}>
          ⚠️ Processing is still in progress or no data was generated. Please wait or refresh.
        </div>
      )}

      {selected?.includes("Meeting Summary") && (
        <div className="card">
          <h2>📝 Meeting Summary</h2>
          {summary.length ? (
            summary.map((s) => (
              <p key={s.id} className="summary-text">{s.text}</p>
            ))
          ) : (
            <p className="empty-message">No summary yet.</p>
          )}
        </div>
      )}

      {selected?.includes("Task Division") && (
        <div className="card">
          <h2>📋 Task Division</h2>
          {actionItems.length ? (
            <ul className="action-items-list">
              {actionItems.map((a) => (
                <li key={a.id} className="action-item">
                  <div className="action-task">{a.task}</div>
                  <div className="action-meta">
                    <span className="action-owner">👤 {a.owner || "Unassigned"}</span>
                    <span className="action-due">📅 {a.due_date || "Not set"}</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No action items yet.</p>
          )}
        </div>
      )}

      {selected?.includes("Action Flow") && (
        <div className="card">
          <h2>🔄 Action Flow</h2>
          {actionItems.length ? (
            <div className="timeline">
              {actionItems.map((a, index) => (
                <div key={a.id} className="timeline-item">
                  <div className="timeline-dot"></div>
                  <div className="timeline-content">
                    <div className="timeline-task">{a.task} (Task #{index + 1})</div>
                    <div className="timeline-details">
                      <span>👤 {a.owner || "Unassigned"}</span>
                      <span>📅 {a.due_date || "Not set"}</span>
                      <span>🔗 Dependencies: {a.dependencies?.join(", ") || "None"}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-message">No action flow data.</p>
          )}
        </div>
      )}

      {selected?.includes("Smart Chatbot") && (
        <div className="card chatbot-card">
          <h2>💬 Smart Chatbot</h2>
          <div className="chat-interface">
            <div className="chat-messages">
              {messages.length === 0 && (
                <p style={{ opacity: 0.6, textAlign: "center", padding: "20px" }}>
                  Ask me anything about this meeting!
                </p>
              )}
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`chat-message ${msg.sender}`}
                >
                  <strong>{msg.sender === "user" ? "You:" : "Bot:"}</strong>
                  <p>{msg.text}</p>
                </div>
              ))}
            </div>
            <div className="chat-input-container">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask me about this meeting..."
                className="chat-input"
                onKeyDown={(e) => e.key === "Enter" && sendChat()}
              />
              <button
                className="chat-send-btn"
                onClick={sendChat}
                disabled={chatLoading}
              >
                {chatLoading ? "..." : "Send"}
              </button>
            </div>
          </div>
        </div>
      )}

      {selected?.includes("Avatar Explainer") && (
        <div className="card avatar-card">
          <h2>🎤 Avatar Explainer</h2>
          <div className="avatar-container">
            <div className="avatar-image-wrapper">
              <img
                src="https://www.gravatar.com/avatar/?d=mp&s=200"
                alt="Avatar"
                className="avatar-img"
              />
            </div>
            <div className="audio-player-wrapper">
              {audioUrl ? (
                <audio controls autoPlay className="audio-player">
                  <source src={audioUrl} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              ) : audioError ? (
                <div className="audio-error">
                  <p>{audioError}</p>
                </div>
              ) : (
                <button onClick={fetchAvatarAudio} className="chat-send-btn">
                  ▶ Generate Explanation
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Results;
