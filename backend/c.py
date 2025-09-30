import os
from dotenv import load_dotenv
from google.generativeai import list_models

load_dotenv()  # Load .env for other settings, but don't override ADC

# Remove or comment out the explicit credentials path
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/parthavikurugundla/Downloads/clever-airship-466111-h5-d5b58551d0c2.json'

models = list_models()
print("Available models:", [model.name for model in models])
