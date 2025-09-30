import { useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import OutputCard from "../components/OutputCard";
import "./Outputs.css";
import { MeetingContext } from "../context/MeetingContext";

function Outputs() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState([]);
  const { meetingId, loading, createNewMeeting } = useContext(MeetingContext);
  const [isProcessing, setIsProcessing] = useState(false);
  const [meetingExists, setMeetingExists] = useState(false);
  const [checkingMeeting, setCheckingMeeting] = useState(true);

  const outputs = [
    { title: "Meeting Summary", desc: "Clean overview of key points and decisions", color: "blue" },
    { title: "Task Division", desc: "Auto-assign action items to team members", color: "green" },
    { title: "Action Flow", desc: "Visual workflow with dependencies & timelines", color: "purple" },
    { title: "Smart Chatbot", desc: "Ask questions about your meeting anytime", color: "pink" },
    { title: "Avatar Explainer", desc: "Friendly AI explains key points in simple terms", color: "orange" },
  ];

  useEffect(() => {
    const verifyMeeting = async () => {
      if (!meetingId) { setCheckingMeeting(false); return; }
      try {
        await axios.get(`http://localhost:8000/meetings/${meetingId}`);
        setMeetingExists(true);
      } catch {
        setMeetingExists(false);
      } finally {
        setCheckingMeeting(false);
      }
    };
    verifyMeeting();
  }, [meetingId]);

  const toggleSelect = (title) => {
    setSelected((prev) =>
      prev.includes(title) ? prev.filter((s) => s !== title) : [...prev, title]
    );
  };

  const handleCreateNewMeeting = async () => {
    try {
      const newId = await createNewMeeting();
      if (newId) setMeetingExists(true);
    } catch (error) {
      alert("Failed to create new meeting.");
    }
  };

  const generateOutputs = async () => {
    if (!meetingId || !meetingExists) {
      alert("No valid meeting. Create one first.");
      return;
    }
    if (selected.length === 0) {
      alert("Select at least one output.");
      return;
    }

    setIsProcessing(true);
    try {
      await axios.get(`http://localhost:8000/meetings/${meetingId}`);
      await axios.post(`http://localhost:8000/meetings/${meetingId}/process`);
      navigate("/results", { state: { selected, meetingId } });
    } catch (error) {
      if (error.response?.status === 404) {
        await handleCreateNewMeeting();
      } else {
        alert(`Error: ${error.message || "Unknown error"}`);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading || checkingMeeting) {
    return (
      <div className="loading-container">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="outputs">
      <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>
      <h1>What do you need from this meeting? ✨</h1>
      <p>Choose one or more outputs</p>

      {(!meetingId || !meetingExists) && (
        <div className="warning-box">
          ⚠️ No valid meeting found. 
          <button onClick={handleCreateNewMeeting}>Create New Meeting</button>
        </div>
      )}

      <div className="outputs-grid">
        {outputs.map((o) => (
          <OutputCard
            key={o.title}
            {...o}
            isSelected={selected.includes(o.title)}
            onSelect={() => toggleSelect(o.title)}
          />
        ))}
      </div>

      {selected.length > 0 && (
        <div className="selection-box">
          <p>Selected: {selected.join(", ")}</p>
        </div>
      )}

      <button
        className="generate-btn"
        onClick={generateOutputs}
        disabled={isProcessing}
      >
        {isProcessing ? "⏳ Processing..." : "✨ Generate Outputs ✨"}
      </button>
    </div>
  );
}

export default Outputs;

