from app.db import get_db
from app import models
from google.cloud import speech
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def transcribe_audio_artifact(db, artifact_id):
    artifact = db.get(models.Artifact, artifact_id)
    if not artifact or not artifact.url:
        raise ValueError("Artifact not found or no URL")
    
    client = speech.SpeechClient()
    with open(artifact.url, "rb") as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Adjust based on file format
        sample_rate_hertz=16000,  # Adjust based on audio
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    transcript = response.results[0].alternatives[0].transcript if response.results else "No transcript available"

    artifact.transcript_text = transcript
    db.commit()
    return transcript
