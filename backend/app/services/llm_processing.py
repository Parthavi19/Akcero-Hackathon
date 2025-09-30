from google.generativeai import GenerativeModel
import os
from dotenv import load_dotenv
from app import models
import json
import time
from google.api_core import exceptions
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Initialize the GenerativeModel
model = GenerativeModel('gemini-2.5-pro',
                        generation_config={
                            "response_mime_type": "application/json"
                        })

def process_transcript_with_google_nlp(transcript: str):
    """
    Process a meeting transcript using Google NLP and return structured output.
    """
    max_retries = 3
    retry_delay = 8  # Start with 8 seconds, per error suggestion

    logger.info(f"Processing transcript of length {len(transcript)}")
    for attempt in range(max_retries):
        try:
            prompt = f"""
            From this meeting transcript, extract the following in JSON format:
            {{
                "summary": "A clean overview of the meeting.",
                "decisions": ["List of decisions made as strings"],
                "action_items": [
                    {{"task": "Task description", "owner": "Owner name", "due_date": "YYYY-MM-DD"}}
                ]
            }}

            Transcript: {transcript}
            """
            response = model.generate_content(prompt)
            output_text = response.text.strip()
            llm_output = json.loads(output_text)
            logger.info("Successfully processed transcript into JSON")
            return llm_output
        except exceptions.ResourceExhausted as e:
            if attempt < max_retries - 1:  # Don't wait on last attempt
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Quota exceeded. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries reached for quota exceeded: {str(e)}")
                raise  # Re-raise on final failure
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM output as JSON: {str(e)}")
            raise ValueError("Failed to parse LLM output as JSON")
        except Exception as e:
            logger.error(f"Unexpected error during NLP processing: {str(e)}")
            raise

def persist_nlp_outputs(meeting_id: str, llm_output: dict, db):
    """
    Persist the NLP output into the database.
    """
    logger.info(f"Persisting NLP outputs for meeting ID: {meeting_id}")
    try:
        summary = models.Summary(meeting_id=meeting_id, text=llm_output.get("summary", ""))
        db.add(summary)
        
        for dec in llm_output.get("decisions", []):
            decision = models.Decision(meeting_id=meeting_id, text=dec)
            db.add(decision)
        
        for item in llm_output.get("action_items", []):
            action = models.ActionItem(
                meeting_id=meeting_id,
                task=item.get("task", ""),
                owner=item.get("owner", ""),
                due_date=datetime.strptime(item.get("due_date", ""), "%Y-%m-%d").date() if item.get("due_date") else None,
                status=item.get("status", "pending")
            )
            db.add(action)
        
        db.commit()
        logger.info("NLP outputs persisted successfully")
    except Exception as e:
        logger.error(f"Error persisting NLP outputs: {str(e)}")
        db.rollback()
        raise

