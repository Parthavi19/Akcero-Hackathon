# app/features.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import re
import os
import uuid
import pyttsx3  # offline TTS
from typing import List, Dict

router = APIRouter()

# --- Helper: load transcript from your storage ---
# Adjust this to your actual DB/storage. For now, we expect
# transcripts to be saved as plain text files under ./transcripts/{meeting_id}.txt
TRANSCRIPT_DIR = Path("./transcripts")
TRANSCRIPT_DIR.mkdir(exist_ok=True)

def load_transcript(meeting_id: str) -> str:
    f = TRANSCRIPT_DIR / f"{meeting_id}.txt"
    if not f.exists():
        raise FileNotFoundError("Transcript not found for meeting_id " + meeting_id)
    return f.read_text(encoding="utf-8")

# --- Utility: parse transcript into timeline entries ---
# Expect transcript lines like "Parthavi Kurugundla (Chair): Welcome everyone..."
SPEAKER_LINE_REGEX = re.compile(r"^\s*(?P<speaker>[A-Za-z .'-]+)\s*(?:\([^\)]*\))?\s*:\s*(?P<text>.+)$")

def parse_timeline(transcript: str) -> List[Dict]:
    timeline = []
    for line in transcript.splitlines():
        m = SPEAKER_LINE_REGEX.match(line)
        if m:
            timeline.append({
                "speaker": m.group("speaker").strip(),
                "text": m.group("text").strip()
            })
    return timeline

# --- Simple retrieval QA: pick sentence with highest keyword overlap ---
def retrieve_answer(transcript: str, question: str) -> str:
    if not transcript.strip():
        return "No transcript available to answer the question."
    # split into sentences (naive)
    sentences = re.split(r'(?<=[.?!])\s+', transcript)
    q_tokens = set(re.findall(r"\w+", question.lower()))
    best = ("", 0)
    for s in sentences:
        s_tokens = set(re.findall(r"\w+", s.lower()))
        overlap = len(q_tokens & s_tokens)
        if overlap > best[1]:
            best = (s, overlap)
    if best[1] == 0:
        # fallback: return a short heuristic summary from transcript head
        return sentences[0] if sentences else "Couldn't find a direct answer in the transcript."
    return best[0]

# --- Action Flow endpoint ---
@router.get("/meetings/{meeting_id}/action-flow")
async def get_action_flow(meeting_id: str):
    try:
        transcript = load_transcript(meeting_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript not found")
    timeline = parse_timeline(transcript)
    # Add index and short preview
    for i, t in enumerate(timeline):
        t["id"] = f"{meeting_id}-t-{i}"
    return {"timeline": timeline}

# --- Chat endpoint (Q&A) ---
@router.post("/meetings/{meeting_id}/chat")
async def chat_meeting(meeting_id: str, payload: Dict):
    question = payload.get("question") or ""
    if question.strip() == "":
        raise HTTPException(status_code=400, detail="Question is required")
    try:
        transcript = load_transcript(meeting_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript not found")
    # Naive retrieval
    answer = retrieve_answer(transcript, question)
    return {"question": question, "answer": answer}

# --- Avatar (TTS) endpoint ---
AUDIO_DIR = Path("./static/avatar_audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/meetings/{meeting_id}/avatar")
async def generate_avatar_audio(meeting_id: str):
    """
    Generates a short spoken summary (TTS) from the transcript and returns an audio URL.
    Uses offline pyttsx3. For production replace with an LLM + cloud TTS.
    """
    try:
        transcript = load_transcript(meeting_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transcript not found")

    # Very simple "summary": take the first 2-4 sentences that are not placeholders
    sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+', transcript) if s.strip()]
    # filter out lines like "The team discussed..." placeholders
    sentences = [s for s in sentences if "placeholder" not in s.lower() and "no transcript" not in s.lower()]
    summary_text = " ".join(sentences[:4]) or "No summary available."

    # create unique filename
    fname = f"{meeting_id}_{uuid.uuid4().hex[:8]}.mp3"
    out_path = AUDIO_DIR / fname

    # offline TTS
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        # save to file (pyttsx3 supports save_to_file)
        engine.save_to_file(summary_text, str(out_path))
        engine.runAndWait()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

    # Return path relative to static mount
    return {"audio_path": f"/static/avatar_audio/{fname}", "text": summary_text}

