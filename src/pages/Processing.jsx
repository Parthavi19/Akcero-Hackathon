import React, { useState, useContext } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { MeetingContext } from "../context/MeetingContext";
import "./Processing.css";

// Icons
const FileTextIcon = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>
    <path d="M14 2v4a2 2 0 0 0 2 2h4"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <line x1="10" y1="9" x2="8" y2="9"/>
  </svg>
);

const CameraIcon = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
    <circle cx="12" cy="13" r="3"/>
  </svg>
);

const MicIcon = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" y1="19" x2="12" y2="22"/>
  </svg>
);

// Type config
const typeConfig = {
  text: { title: "Text Transcript", desc: "Paste your meeting notes", icon: FileTextIcon, color: "#5b21b6", buttonText: "Process Text Notes", endpoint: "text" },
  photo: { title: "Whiteboard Photo", desc: "Upload photos of notes", icon: CameraIcon, color: "#ec4899", buttonText: "Process Photos", endpoint: "image" },
  audio: { title: "Audio Recording", desc: "Upload audio recordings", icon: MicIcon, color: "#8b5cf6", buttonText: "Process Audio", endpoint: "audio" },
};

function Processing() {
  const { type: paramType } = useParams();
  const navigate = useNavigate();
  const { meetingId, createNewMeeting } = useContext(MeetingContext);

  const [type, setType] = useState(paramType || "text");
  const [textInput, setTextInput] = useState("");
  const [fileInput, setFileInput] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const config = typeConfig[type];
  const Icon = config.icon;

  const handleBack = () => navigate("/");
  const handleFileChange = (e) => {
    setFileInput(e.target.files[0]);
    setError("");
  };

  const handleProcess = async () => {
    // Validation
    if (type === "text" && !textInput.trim()) {
      setError("Please paste your meeting notes before processing.");
      return;
    }
    if ((type === "photo" || type === "audio") && !fileInput) {
      setError("Please select a file before processing.");
      return;
    }

    // Ensure we have a meeting ID
    let currentMeetingId = meetingId;
    if (!currentMeetingId) {
      try {
        setLoading(true);
        currentMeetingId = await createNewMeeting();
        if (!currentMeetingId) {
          setError("Failed to create meeting. Please try again.");
          setLoading(false);
          return;
        }
      } catch (err) {
        setError("Failed to create meeting. Please try again.");
        setLoading(false);
        return;
      }
    }

    setLoading(true);
    setError("");

    try {
      if (type === "text") {
        // Save text transcript
        console.log("Saving transcript for meeting:", currentMeetingId);
        const response = await axios.post(
          `http://localhost:8000/meetings/${currentMeetingId}/artifacts/text`,
          { text: textInput }
        );
        console.log("Transcript saved:", response.data);
        
      } else {
        // Upload file (audio or image)
        const formData = new FormData();
        formData.append("file", fileInput);

        console.log(`Uploading ${type} for meeting:`, currentMeetingId);
        const response = await axios.post(
          `http://localhost:8000/meetings/${currentMeetingId}/artifacts/${config.endpoint}`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log(`${type} uploaded:`, response.data);
      }

      // Navigate to outputs page
      navigate("/outputs");
      
    } catch (err) {
      console.error("Error saving artifact:", err);
      setError(
        err.response?.data?.detail || 
        `Failed to save ${type}. Please try again.`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="processing-page">
      <div className="processing-card">
        <button className="back-btn" onClick={handleBack}>← Back</button>

        <div className="type-selector">
          {Object.keys(typeConfig).map((t) => (
            <button 
              key={t} 
              onClick={() => setType(t)} 
              className={`type-btn ${t === type ? "active" : ""}`}
            >
              {typeConfig[t].title}
            </button>
          ))}
        </div>

        <h1 className="processing-title">
          <Icon width={32} height={32} /> Processing {config.title}
        </h1>
        <p className="processing-subtitle">{config.desc}</p>

        {error && (
          <div style={{
            width: "100%",
            padding: "12px",
            background: "#fff3cd",
            border: "1px solid #ffc107",
            borderRadius: "8px",
            color: "#856404",
            fontSize: "14px"
          }}>
            {error}
          </div>
        )}

        {meetingId && (
          <div style={{
            width: "100%",
            padding: "8px",
            background: "#d1ecf1",
            border: "1px solid #17a2b8",
            borderRadius: "8px",
            color: "#0c5460",
            fontSize: "12px"
          }}>
            Meeting ID: {meetingId}
          </div>
        )}

        <div className="processing-box">
          {type === "text" ? (
            <textarea
              className="input-text"
              value={textInput}
              onChange={(e) => {
                setTextInput(e.target.value);
                setError("");
              }}
              placeholder="Paste or type your meeting notes here..."
            />
          ) : (
            <label className="input-file-box">
              <Icon width={50} height={50} className="input-icon"/>
              <p>Click or drag to upload {type}</p>
              <p className="input-note">
                {type === 'photo' ? "PNG, JPG, HEIC up to 10MB" : "MP3, WAV, M4A up to 25MB"}
              </p>
              <input 
                type="file" 
                accept={type === "photo" ? "image/*" : "audio/*"} 
                onChange={handleFileChange} 
              />
            </label>
          )}
        </div>

        <div className="results-box">
          {type === "text" && textInput && <p>{textInput}</p>}
          {fileInput && <p>File selected: {fileInput.name}</p>}
          {!textInput && !fileInput && <p>No content provided yet.</p>}
        </div>

        <button 
          className="process-btn" 
          style={{ backgroundColor: config.color }} 
          onClick={handleProcess}
          disabled={loading}
        >
          {loading ? "⏳ Saving..." : `✨ ${config.buttonText} ✨`}
        </button>
      </div>
    </div>
  );
}

export default Processing;
