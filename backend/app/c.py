import os
from dotenv import load_dotenv
from google.generativeai import list_models
import google.auth

load_dotenv()  # Loads .env if present

# Explicitly set from env if needed
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '/Users/parthavikurugundla/Downloads/clever-airship-466111-h5-d5b58551d0c2.json')

# Test ADC
try:
    credentials, project_id = google.auth.default()
    print(f"ADC loaded successfully. Project ID: {project_id}")
except Exception as e:
    print(f"ADC failed: {e}")
    exit(1)

# List models
models = list_models()
print("Available models:", [model.name for model in models])
