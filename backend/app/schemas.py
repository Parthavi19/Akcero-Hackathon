from datetime import date
from typing import Optional
from pydantic import BaseModel

# ---- Meetings ----
class MeetingCreate(BaseModel):
    title: str
    date: date
    created_by: str

class MeetingOut(MeetingCreate):
    id: str

    class Config:
        from_attributes = True  # Updated from orm_mode

# ---- Participants ----
class ParticipantCreate(BaseModel):
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None  # default avatar optional

class ParticipantOut(ParticipantCreate):
    id: str

    class Config:
        from_attributes = True  # Updated from orm_mode

# ---- Artifacts ----
class ArtifactTextIn(BaseModel):
    text: str

class ArtifactOut(BaseModel):
    id: str
    meeting_id: str
    kind: str
    url: Optional[str] = None
    transcript_text: Optional[str] = None
    file_path: Optional[str] = None

    class Config:
        from_attributes = True  # Updated from orm_mode

# ---- Summaries ----
class SummaryIn(BaseModel):
    text: str

class SummaryOut(SummaryIn):
    id: str
    meeting_id: str

    class Config:
        from_attributes = True  # Updated from orm_mode

# ---- Decisions ----
class DecisionIn(BaseModel):
    text: str

class DecisionOut(DecisionIn):
    id: str
    meeting_id: str

    class Config:
        from_attributes = True  # Updated from orm_mode

# ---- Action Items ----
class ActionItemIn(BaseModel):
    task: str
    owner: Optional[str] = None
    due_date: Optional[date] = None

class ActionItemOut(ActionItemIn):
    id: str
    meeting_id: str
    status: Optional[str] = None  # Added to match ActionItem model

    class Config:
        from_attributes = True  # Updated from orm_mode
