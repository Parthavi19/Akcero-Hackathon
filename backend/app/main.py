from __future__ import annotations
import os
import uuid
from pathlib import Path
import io
import logging

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from gtts import gTTS
from pydantic import BaseModel

from app.db import engine, Base, get_db
from app import models
from app.schemas import (
    MeetingCreate, MeetingOut,
    ParticipantCreate, ParticipantOut,
    ArtifactTextIn, ArtifactOut,
    SummaryIn, SummaryOut,
    DecisionIn, DecisionOut,
    ActionItemIn, ActionItemOut,
)

# ----------------------------
# App & Logging
# ----------------------------
app = FastAPI(title="Meetings API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload folder
PROJECT_ROOT = Path(os.getcwd())
UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Create tables
Base.metadata.create_all(bind=engine)

# ----------------------------
# Root
# ----------------------------
@app.get("/")
def root():
    return {"message": "API running!"}

# ----------------------------
# Meetings
# ----------------------------
@app.post("/meetings", response_model=MeetingOut, status_code=201)
def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    db_meeting = models.Meeting(**meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@app.get("/meetings", response_model=list[MeetingOut])
def list_meetings(db: Session = Depends(get_db)):
    return db.query(models.Meeting).all()

@app.get("/meetings/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

# ----------------------------
# Participants
# ----------------------------
@app.post("/meetings/{mid}/participants", response_model=list[ParticipantOut], status_code=201)
def add_participants(mid: str, participants: list[ParticipantCreate], db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    rows: list[models.Participant] = []
    for p in participants:
        row = models.Participant(meeting_id=mid, **p.dict())
        db.add(row)
        rows.append(row)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows

@app.get("/meetings/{mid}/participants", response_model=list[ParticipantOut])
def list_participants(mid: str, db: Session = Depends(get_db)):
    return db.query(models.Participant).filter_by(meeting_id=mid).all()

# ----------------------------
# Artifacts
# ----------------------------
@app.post("/meetings/{mid}/artifacts/text", response_model=ArtifactOut, status_code=201)
def add_text_artifact(mid: str, payload: ArtifactTextIn, db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    artifact_url = f"http://localhost:8000/artifacts/{uuid.uuid4()}"
    art = models.Artifact(
        meeting_id=mid,
        kind=models.ArtifactKind.text,
        url=artifact_url,
        transcript_text=payload.text
    )
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

@app.post("/meetings/{mid}/artifacts/audio", response_model=ArtifactOut, status_code=201)
def upload_audio_artifact(mid: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    ext = os.path.splitext(file.filename or "")[1] or ".wav"
    fname = f"{mid}_{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / fname
    with path.open("wb") as f:
        f.write(file.file.read())

    artifact_url = f"http://localhost:8000/uploads/{fname}"
    art = models.Artifact(
        meeting_id=mid,
        kind=models.ArtifactKind.audio,
        url=artifact_url,
        file_path=str(path)
    )
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

@app.post("/meetings/{mid}/artifacts/image", response_model=ArtifactOut, status_code=201)
def upload_image_artifact(mid: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    fname = f"{mid}_{uuid.uuid4().hex}{ext}"
    path = UPLOAD_DIR / fname
    with path.open("wb") as f:
        f.write(file.file.read())

    artifact_url = f"http://localhost:8000/uploads/{fname}"
    art = models.Artifact(
        meeting_id=mid,
        kind=models.ArtifactKind.image,
        url=artifact_url,
        file_path=str(path)
    )
    db.add(art)
    db.commit()
    db.refresh(art)
    return art

@app.get("/meetings/{mid}/artifacts", response_model=list[ArtifactOut])
def list_artifacts(mid: str, db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return db.query(models.Artifact).filter_by(meeting_id=mid).all()

# ----------------------------
# Summaries
# ----------------------------
@app.post("/meetings/{mid}/summary", response_model=SummaryOut, status_code=201)
def create_summary(mid: str, payload: SummaryIn, db: Session = Depends(get_db)):
    if not db.get(models.Meeting, mid):
        raise HTTPException(status_code=404, detail="Meeting not found")
    row = models.Summary(meeting_id=mid, text=payload.text)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@app.get("/meetings/{mid}/summary", response_model=list[SummaryOut])
def get_summaries(mid: str, db: Session = Depends(get_db)):
    return db.query(models.Summary).filter_by(meeting_id=mid).all()

# ----------------------------
# Decisions
# ----------------------------
@app.post("/meetings/{mid}/decisions", response_model=list[DecisionOut], status_code=201)
def create_decisions(mid: str, items: list[DecisionIn], db: Session = Depends(get_db)):
    if not db.get(models.Meeting, mid):
        raise HTTPException(status_code=404, detail="Meeting not found")
    rows = [models.Decision(meeting_id=mid, text=i.text) for i in items]
    db.add_all(rows)
    db.commit()
    for r in rows: db.refresh(r)
    return rows

@app.get("/meetings/{mid}/decisions", response_model=list[DecisionOut])
def list_decisions(mid: str, db: Session = Depends(get_db)):
    return db.query(models.Decision).filter_by(meeting_id=mid).all()

# ----------------------------
# Action Items
# ----------------------------
@app.post("/meetings/{mid}/action-items", response_model=list[ActionItemOut], status_code=201)
def create_action_items(mid: str, items: list[ActionItemIn], db: Session = Depends(get_db)):
    if not db.get(models.Meeting, mid):
        raise HTTPException(status_code=404, detail="Meeting not found")
    rows = [
        models.ActionItem(meeting_id=mid, task=i.task, owner=i.owner, due_date=i.due_date, status=models.ActionStatus.pending)
        for i in items
    ]
    db.add_all(rows)
    db.commit()
    for r in rows: db.refresh(r)
    return rows

@app.get("/meetings/{mid}/action-items", response_model=list[ActionItemOut])
def list_action_items(mid: str, db: Session = Depends(get_db)):
    return db.query(models.ActionItem).filter_by(meeting_id=mid).all()

# ----------------------------
# Processing / Summarization
# ----------------------------
from app.llm import generate_summary, generate_decisions, generate_action_items, answer_question, transcribe_audio, analyze_image

@app.post("/meetings/{mid}/process")
async def process_meeting(mid: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    background_tasks.add_task(real_processing, mid, db)
    
    return {"status": "processing started", "meeting_id": mid}

def real_processing(mid: str, db: Session):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        logger.error(f"Meeting {mid} not found during processing")
        return

    artifacts = db.query(models.Artifact).filter_by(meeting_id=mid).all()

    # Transcribe non-text artifacts
    for a in artifacts:
        if a.transcript_text:
            continue
        if a.kind == models.ArtifactKind.audio and a.file_path:
            a.transcript_text = transcribe_audio(a.file_path)
        elif a.kind == models.ArtifactKind.image and a.file_path:
            a.transcript_text = analyze_image(a.file_path)
    db.commit()

    # Deduplicate and concatenate transcripts
    transcripts = [a.transcript_text for a in artifacts if a.transcript_text]
    unique_transcripts = list(dict.fromkeys(transcripts))  # Remove duplicates
    transcript = "\n".join(unique_transcripts)
    
    if not transcript.strip():
        logger.warning(f"No valid transcript for meeting {mid}")
        transcript = "No valid transcript available."

    logger.info(f"Processing transcript for meeting {mid} (length: {len(transcript)} chars): {transcript[:200]}...")

    # Get participants for assignment
    participants = db.query(models.Participant).filter_by(meeting_id=mid).all()
    participant_names = [p.name for p in participants if p.name]

    # Clear existing summaries, decisions, and action items
    db.query(models.Summary).filter_by(meeting_id=mid).delete()
    db.query(models.Decision).filter_by(meeting_id=mid).delete()
    db.query(models.ActionItem).filter_by(meeting_id=mid).delete()
    db.commit()

    # Summarize
    summary_text = generate_summary(transcript)
    db.add(models.Summary(meeting_id=mid, text=summary_text))

    # Decisions
    decisions_list = generate_decisions(transcript)
    db.add_all([models.Decision(meeting_id=mid, text=d) for d in decisions_list])

    # Action Items
    actions_list = generate_action_items(transcript, participant_names)
    db.add_all([
        models.ActionItem(
            meeting_id=mid,
            task=a['task'],
            owner=a['owner'],
            due_date=a['due_date'],
            status=models.ActionStatus.pending
        )
        for a in actions_list
    ])

    db.commit()
    logger.info(f"Processing completed for meeting {mid}")

# ----------------------------
# Smart Chatbot
# ----------------------------
class ChatRequest(BaseModel):
    question: str

@app.post("/meetings/{mid}/chat")
async def chat_meeting(mid: str, req: ChatRequest, db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        return {"answer": "Meeting not found. Please check the meeting ID."}

    artifacts = db.query(models.Artifact).filter_by(meeting_id=mid).all()
    transcripts = [a.transcript_text for a in artifacts if a.transcript_text]
    unique_transcripts = list(dict.fromkeys(transcripts))  # Remove duplicates
    transcript = "\n".join(unique_transcripts)

    if not transcript.strip():
        logger.warning(f"No transcript available for meeting {mid}")
        return {"answer": "No transcript available yet. Please upload meeting audio, image, or text first."}

    # Use LLM to answer
    answer = answer_question(transcript, req.question)
    return {"answer": answer}

# ----------------------------
# Avatar / TTS
# ----------------------------
@app.get("/meetings/{mid}/avatar")
async def avatar_meeting(mid: str, db: Session = Depends(get_db)):
    meeting = db.get(models.Meeting, mid)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Use the latest summary for TTS
    summaries = db.query(models.Summary).filter_by(meeting_id=mid).order_by(models.Summary.created_at.desc()).all()
    text = summaries[0].text if summaries else "Hello! No summary is available for this meeting yet."

    if len(text) > 1000:
        text = text[:1000] + "... The full details contain more."

    logger.info(f"Generating TTS for meeting {mid}")
    tts = gTTS(text, lang="en", slow=False)
    audio_io = io.BytesIO()
    tts.write_to_fp(audio_io)
    audio_io.seek(0)

    return StreamingResponse(
        audio_io, 
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"inline; filename=meeting_{mid}_avatar.mp3",
            "Cache-Control": "no-cache"
        }
    )
