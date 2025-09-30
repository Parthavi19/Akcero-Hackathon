const BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const DEFAULT_AVATAR = "https://www.gravatar.com/avatar/?d=mp";

export async function fetchMeetings() {
  const res = await fetch(`${BASE}/meetings`);
  return res.json();
}

export async function createMeeting(meeting) {
  const res = await fetch(`${BASE}/meetings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(meeting),
  });
  return res.json();
}

export async function fetchParticipants(meetingId) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/participants`);
  let participants = await res.json();
  return participants.map(p => ({ ...p, avatar: p.avatar || DEFAULT_AVATAR }));
}

export async function addParticipants(meetingId, participants) {
  participants = participants.map(p => ({ ...p, avatar: p.avatar || DEFAULT_AVATAR }));
  const res = await fetch(`${BASE}/meetings/${meetingId}/participants`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(participants),
  });
  return res.json();
}

export async function fetchSummaries(meetingId) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/summary`);
  return res.json();
}

export async function addSummary(meetingId, text) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

export async function fetchDecisions(meetingId) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/decisions`);
  return res.json();
}

export async function addDecisions(meetingId, decisions) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/decisions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(decisions.map(d => ({ text: d }))),
  });
  return res.json();
}

export async function fetchActionItems(meetingId) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/action-items`);
  return res.json();
}

export async function addActionItems(meetingId, items) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/action-items`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(items),
  });
  return res.json();
}

export async function chatMeeting(meetingId, question) {
  const res = await fetch(`${BASE}/meetings/${meetingId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return res.json();
}

// Removed unused fetchArtifacts
