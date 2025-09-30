import { useEffect, useState } from "react";
import axios from "axios";

export default function MeetingDetails({ meetingId }) {
  const [data, setData] = useState({
    summary: [],
    decisions: [],
    actionItems: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let interval;

    const fetchData = async () => {
      try {
        setLoading(true);

        const summaryRes = await axios.get(
          `http://localhost:8000/meetings/${meetingId}/summary`
        );
        const decisionsRes = await axios.get(
          `http://localhost:8000/meetings/${meetingId}/decisions`
        );
        const actionItemsRes = await axios.get(
          `http://localhost:8000/meetings/${meetingId}/action-items`
        );

        setData({
          summary: Array.isArray(summaryRes.data) ? summaryRes.data : [],
          decisions: Array.isArray(decisionsRes.data) ? decisionsRes.data : [],
          actionItems: Array.isArray(actionItemsRes.data)
            ? actionItemsRes.data
            : []
        });
      } catch (error) {
        console.error("Error fetching meeting details:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    interval = setInterval(async () => {
      const summaryRes = await axios.get(
        `http://localhost:8000/meetings/${meetingId}/summary`
      );
      if (Array.isArray(summaryRes.data) && summaryRes.data.length > 0) {
        setData((prev) => ({ ...prev, summary: summaryRes.data }));
        clearInterval(interval);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [meetingId]);

  if (loading) return <p>Loading meeting data...</p>;

  return (
    <div>
      <h2>Meeting Summary</h2>
      {data.summary.length ? (
        data.summary.map((s, i) => <p key={s.id || i}>{s.text}</p>)
      ) : (
        <p>No summary yet.</p>
      )}

      <h2>Decisions</h2>
      {data.decisions.length ? (
        data.decisions.map((d, i) => <p key={d.id || i}>{d.text}</p>)
      ) : (
        <p>No decisions yet.</p>
      )}

      <h2>Action Items</h2>
      {data.actionItems.length ? (
        data.actionItems.map((a, i) => (
          <p key={a.id || i}>
            {a.task} (Owner: {a.owner || "Unassigned"})
          </p>
        ))
      ) : (
        <p>No action items yet.</p>
      )}
    </div>
  );
}

