# MeetWise: Smart Meeting Management Platform

MeetWise is a web application designed to streamline meeting management by automatically handling meeting scheduling, participant tracking, transcripts, summaries, and action items using AI-assisted capabilities. The platform allows teams to efficiently organize, document, and track meetings, ensuring accountability and easy retrieval of meeting artifacts.

## Features

### Meeting Management
- Create, view, and update meetings.
- Add participants to meetings with roles and avatars.
- Schedule meetings with specific dates.

### Meeting Artifacts
- Upload meeting transcripts.
- Store notes, action items, and decisions.
- Generate summaries (requires LLM integration, e.g., Gemini API).

### Smart Summarization
- Automatically generate meeting summaries, decisions, and action items (if API quota is available).

### Frontend-Backend Integration
- FastAPI backend serves REST endpoints.
- React + Vite frontend communicates with backend APIs.
- WebSocket support for real-time updates (planned).

### Database
- PostgreSQL database stores meetings, participants, and artifacts.

## Tech Stack
- **Frontend**: React.js, Vite
- **Backend**: FastAPI, Python 3.10+
- **Database**: PostgreSQL
- **Real-time**: WebSocket (planned)
- **AI Integration**: Google Gemini API (Generative AI for summarization)
- **Deployment**: AWS EC2 + RDS for backend, Vercel/Netlify for frontend

## Project Structure

meet-wise/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Backend entry point
│   │   ├── models.py        # Database models
│   │   ├── routes/          # API routes for meetings, participants, artifacts
│   │   └── utils/           # Utility functions (e.g., AI integration)
│   └── requirements.txt      # Backend dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── context/         # React context for state management
│   │   ├── pages/           # Page components
│   │   └── App.jsx          # Frontend entry point
│   └── package.json          # Frontend dependencies
├── README.md                  # Project documentation
└── .env                       # Environment variables



# Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<username>/meet-wise.git
cd meet-wise

2. Backend Setup
bashcd backend
python3 -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate       # Windows
pip install -r requirements.txt

Configure environment variables in .env:
textDATABASE_URL=postgresql://<user>:<password>@localhost:5432/meetwise
GEMINI_API_KEY=<your_gemini_api_key>

Run the backend server:
bashuvicorn app.main:app --reload --host 0.0.0.0 --port 8000

3. Frontend Setup
bashcd ../frontend
npm install
npm run dev

Access the frontend at: http://localhost:5173

### API Usage Examples
##Create a Meeting
bashcurl -X POST http://127.0.0.1:8000/meetings \
-H "Content-Type: application/json" \
-d '{"title": "Team Sync", "date": "2025-09-30", "created_by": "Parthavi"}'

##Add Participants
bashcurl -X POST http://127.0.0.1:8000/meetings/<meeting_id>/participants \
-H "Content-Type: application/json" \
-d '[{"name": "Parthavi"}, {"name": "Sneha"}]'

##Add Meeting Transcript
bashcurl -X POST http://127.0.0.1:8000/meetings/<meeting_id>/artifacts/text \
-H "Content-Type: application/json" \
-d '{"text": "Meeting started with agenda discussion and task assignment."}'

##Get Meeting Summary
bashcurl -X GET http://127.0.0.1:8000/meetings/<meeting_id>/summary
