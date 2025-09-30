# app/llm.py
import google.generativeai as genai
import os
import json
import logging
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPIError
from datetime import datetime

# Load .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY is not set in .env file")
    raise ValueError("GEMINI_API_KEY environment variable is required")
genai.configure(api_key=api_key)

# List available models and select one that supports generateContent
try:
    available_models = genai.list_models()
    model_name = None
    for model in available_models:
        if "generateContent" in model.supported_generation_methods:
            model_name = model.name
            break
    if not model_name:
        logger.error("No models supporting generateContent found")
        raise ValueError("No suitable Gemini model found")
    logger.info(f"Using model: {model_name}")
    model = genai.GenerativeModel(model_name)
except GoogleAPIError as e:
    logger.error(f"Error listing models: {str(e)}")
    raise

def deduplicate_transcript(transcript: str) -> str:
    """Deduplicate lines in the transcript to avoid redundant content."""
    lines = transcript.split("\n")
    seen = set()
    unique_lines = [line for line in lines if line.strip() and line not in seen and not seen.add(line)]
    return "\n".join(unique_lines)

def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Gemini"""
    try:
        logger.info(f"Transcribing audio: {file_path}")
        uploaded_file = genai.upload_file(file_path)
        response = model.generate_content(["Transcribe this audio meeting accurately:", uploaded_file])
        text = response.text.strip()
        if not text:
            logger.warning(f"No text transcribed from audio: {file_path}")
            return "No transcription available from audio."
        logger.info(f"Transcription successful: {text[:100]}...")
        return text
    except GoogleAPIError as e:
        logger.error(f"Transcription error for {file_path}: {str(e)}")
        return f"Audio transcription failed: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected transcription error for {file_path}: {str(e)}")
        return f"Audio transcription failed: {str(e)}"

def analyze_image(file_path: str) -> str:
    """Analyze/OCR image (e.g., whiteboard) using Gemini"""
    try:
        logger.info(f"Analyzing image: {file_path}")
        uploaded_file = genai.upload_file(file_path)
        response = model.generate_content(["Transcribe and summarize the text from this whiteboard or notes image:", uploaded_file])
        text = response.text.strip()
        if not text:
            logger.warning(f"No text extracted from image: {file_path}")
            return "No text extracted from image."
        logger.info(f"Image analysis successful: {text[:100]}...")
        return text
    except GoogleAPIError as e:
        logger.error(f"Image analysis error for {file_path}: {str(e)}")
        return f"Image analysis failed: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected image analysis error for {file_path}: {str(e)}")
        return f"Image analysis failed: {str(e)}"

def generate_summary(transcript: str) -> str:
    """Generate a summary using Gemini"""
    if not transcript.strip() or transcript.startswith("No "):
        logger.warning("Empty or invalid transcript for summary")
        return "No valid transcript provided for summary."
    try:
        logger.info(f"Generating summary for transcript (length: {len(transcript)} chars)")
        transcript = deduplicate_transcript(transcript)
        max_length = 10000
        if len(transcript) > max_length:
            transcript = transcript[:max_length] + "... [truncated]"
            logger.warning(f"Transcript truncated to {max_length} characters")
        response = model.generate_content(
            f"Summarize this meeting transcript in 4-5 concise sentences:\n\n{transcript}"
        )
        text = response.text.strip()
        if not text:
            logger.warning("Empty summary generated")
            return "Unable to generate summary."
        logger.info(f"Summary generated: {text[:100]}...")
        return text
    except GoogleAPIError as e:
        logger.error(f"Summary generation error: {str(e)}")
        # Fallback: simple truncation-based summary
        sentences = [s.strip() for s in transcript.split(".") if s.strip()]
        return " ".join(sentences[:4]) + "." if sentences else "Summary generation failed."
    except Exception as e:
        logger.error(f"Unexpected summary generation error: {str(e)}")
        return "Summary generation failed."

def generate_decisions(transcript: str) -> list[str]:
    """Extract key decisions using Gemini with structured output"""
    if not transcript.strip() or transcript.startswith("No "):
        logger.warning("Empty or invalid transcript for decisions")
        return []
    try:
        logger.info(f"Generating decisions for transcript (length: {len(transcript)} chars)")
        transcript = deduplicate_transcript(transcript)
        max_length = 10000
        if len(transcript) > max_length:
            transcript = transcript[:max_length] + "... [truncated]"
            logger.warning(f"Transcript truncated to {max_length} characters")
        prompt = f"Extract all key decisions from this meeting transcript as a JSON list of strings:\n\n{transcript}\nOutput only JSON: [\"decision1\", \"decision2\"]"
        response = model.generate_content(prompt)
        text = response.text.strip()
        try:
            decisions = json.loads(text) if text else []
            logger.info(f"Decisions generated: {decisions}")
            return decisions if isinstance(decisions, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in decisions response: {text}, error: {str(e)}")
            return []
    except GoogleAPIError as e:
        logger.error(f"Decisions generation error: {str(e)}")
        # Fallback: extract lines containing "decision"
        return [line.strip() for line in transcript.split("\n") if "decision" in line.lower() and line.strip()]
    except Exception as e:
        logger.error(f"Unexpected decisions generation error: {str(e)}")
        return []

def generate_action_items(transcript: str, participant_names: list[str]) -> list[dict]:
    """Extract action items using Gemini with structure: task, owner, due_date, dependencies"""
    if not transcript.strip() or transcript.startswith("No "):
        logger.warning("Empty or invalid transcript for action items")
        return []
    try:
        names_str = ", ".join(participant_names) or "Unassigned"
        logger.info(f"Generating action items with participants: {names_str}")
        transcript = deduplicate_transcript(transcript)
        max_length = 10000
        if len(transcript) > max_length:
            transcript = transcript[:max_length] + "... [truncated]"
            logger.warning(f"Transcript truncated to {max_length} characters")
        prompt = f"""
        Extract action items from this meeting transcript. For each, auto-assign an owner from: {names_str}.
        If no clear owner, use 'Unassigned'. Infer due dates as YYYY-MM-DD if mentioned, else use null.
        Include dependencies as a list of task IDs (number them starting from 1).
        Output as JSON array of objects: [{{"task": "str", "owner": "str", "due_date": "str or null", "dependencies": [int]}}]
        
        Transcript:\n{transcript}
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        try:
            actions = json.loads(text) if text else []
            # Convert due_date strings to Python date objects or None
            for action in actions:
                if action.get("due_date") and action["due_date"] != "Not set":
                    try:
                        action["due_date"] = datetime.strptime(action["due_date"], "%Y-%m-%d").date()
                    except ValueError:
                        logger.warning(f"Invalid due_date format: {action['due_date']}")
                        action["due_date"] = None
                else:
                    action["due_date"] = None
            logger.info(f"Action items generated: {actions}")
            return actions if isinstance(actions, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in action items response: {text}, error: {str(e)}")
            return []
    except GoogleAPIError as e:
        logger.error(f"Action items generation error: {str(e)}")
        # Fallback: extract tasks based on keywords
        tasks = []
        lines = transcript.split("\n")
        for i, line in enumerate(lines, 1):
            if any(word in line.lower() for word in ["task", "action", "do", "assigned"]):
                tasks.append({
                    "task": line.strip(),
                    "owner": "Unassigned",
                    "due_date": None,
                    "dependencies": []
                })
        return tasks
    except Exception as e:
        logger.error(f"Unexpected action items generation error: {str(e)}")
        return []

def answer_question(transcript: str, question: str) -> str:
    """Answer arbitrary questions using Gemini"""
    if not transcript.strip() or transcript.startswith("No "):
        logger.warning("Empty or invalid transcript for chatbot")
        return "No valid transcript available to answer the question."
    try:
        logger.info(f"Answering question: {question}")
        transcript = deduplicate_transcript(transcript)
        max_length = 10000
        if len(transcript) > max_length:
            transcript = transcript[:max_length] + "... [truncated]"
            logger.warning(f"Transcript truncated to {max_length} characters")
        prompt = f"""
        You are a helpful assistant. 
        Use the meeting transcript below to answer the user's question concisely.

        Transcript:
        {transcript}

        Question: {question}
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        logger.info(f"Chatbot answer: {text[:100]}...")
        return text
    except GoogleAPIError as e:
        logger.error(f"Chatbot answer error: {str(e)}")
        return "Answer not available."
    except Exception as e:
        logger.error(f"Unexpected chatbot answer error: {str(e)}")
        return "Answer not available."
