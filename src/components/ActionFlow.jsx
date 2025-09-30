// src/components/ActionFlow.jsx
import React, { useEffect, useState, useContext } from "react";
import axios from "axios";
import { MeetingContext } from "../context/MeetingContext";

export default function ActionFlow({ meetingId: propMeetingId }) {
  const { meetingId: ctxMeetingId } = useContext(MeetingContext);
  const meetingId = propMeetingId || ctxMeetingId;

  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!meetingId) return;
    const fetchTimeline = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`http://localhost:8000/meetings/${meetingId}/action-flow`);
        setTimeline(res.data.timeline || []);
      } catch (err) {
        console.error("Failed to fetch timeline", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, [meetingId]);

  if (!meetingId) return <p>No meeting selected.</p>;
  if (loading) return <p>Loading action flow...</p>;

  return (
    <div className="action-flow">
      <h2>Action Flow / Timeline</h2>
      {timeline.length === 0 && <p>No timeline found in transcript.</p>}
      <div className="timeline-list">
        {timeline.map((t, i) => (
          <div key={t.id} className="timeline-item">
            <div className="timeline-meta">
              <strong>{t.speaker}</strong>
              <span className="index">#{i + 1}</span>
            </div>
            <div className="timeline-text">{t.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

