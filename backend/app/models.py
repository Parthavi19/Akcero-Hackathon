from app.db import Base
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import relationship
import enum, uuid

# ---- ENUMS ----
class ArtifactKind(str, enum.Enum):
    audio = "audio"
    image = "image"
    text  = "text"

class ActionStatus(str, enum.Enum):
    pending = "pending"
    open    = "open"
    done    = "done"

# ---- TABLES ----
class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    date = Column(Date)
    created_by = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    participants = relationship("Participant", back_populates="meeting", cascade="all,delete")
    artifacts    = relationship("Artifact", back_populates="meeting", cascade="all,delete")
    summaries    = relationship("Summary", back_populates="meeting", cascade="all,delete")
    decisions    = relationship("Decision", back_populates="meeting", cascade="all,delete")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all,delete")

class Participant(Base):
    __tablename__ = "participants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(ForeignKey("meetings.id"), index=True)
    name = Column(String, nullable=False)
    role = Column(String)
    email = Column(String)
    avatar = Column(String, default="https://www.gravatar.com/avatar/?d=mp&s=200")

    meeting = relationship("Meeting", back_populates="participants")

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(ForeignKey("meetings.id"), index=True)
    kind = Column(Enum(ArtifactKind), nullable=False)
    url  = Column(String, nullable=True)
    transcript_text = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    meeting = relationship("Meeting", back_populates="artifacts")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(ForeignKey("meetings.id"), index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    meeting = relationship("Meeting", back_populates="summaries")

class Decision(Base):
    __tablename__ = "decisions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(ForeignKey("meetings.id"), index=True)
    text = Column(Text, nullable=False)

    meeting = relationship("Meeting", back_populates="decisions")

class ActionItem(Base):
    __tablename__ = "action_items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(ForeignKey("meetings.id"), index=True)
    owner = Column(String, nullable=True)
    task = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(ActionStatus), default=ActionStatus.pending)

    meeting = relationship("Meeting", back_populates="action_items")
