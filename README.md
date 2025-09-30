# MeetWise: Smart Meeting Management Platform

**MeetWise** is a web application that streamlines meeting management by automatically handling scheduling, participant tracking, transcripts, summaries, and action items using AI. It helps teams organize, document, and track meetings efficiently, ensuring accountability and easy retrieval of meeting artifacts.

---

## Features

### Meeting Management
- Create, view, and update meetings
- Add participants with roles and avatars
- Schedule meetings with specific dates

### Meeting Artifacts
- Upload meeting transcripts
- Store notes, decisions, and action items
- Generate summaries using AI (requires LLM integration, e.g., Gemini API)

### Smart Summarization
- Automatically generate meeting summaries, decisions, and action items (if API quota is available)

### Frontend-Backend Integration
- FastAPI backend with REST endpoints
- React + Vite frontend communicates with backend APIs
- WebSocket support for real-time updates (planned)

### Database
- PostgreSQL database stores meetings, participants, and artifacts

---

## Tech Stack
- **Frontend:** React.js, Vite  
- **Backend:** FastAPI, Python 3.10+  
- **Database:** PostgreSQL  
- **Real-time:** WebSocket (planned)  
- **AI Integration:** Google Gemini API  
- **Deployment:** AWS EC2 + RDS (backend), Vercel/Netlify (frontend)  

---

## Project Structure

```text
meet-wise/
├── backend/
│   ├── app/
│   │   ├── main.py          # Backend entry point
│   │   ├── models.py        # Database models
│   │   ├── routes/          # API routes for meetings, participants, artifacts
│   │   └── utils/           # Utility functions (e.g., AI integration)
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── context/         # React context for state management
│   │   ├── pages/           # Page components
│   │   └── App.jsx          # Frontend entry point
│   └── package.json         # Frontend dependencies
├── README.md
└── .env
````

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<username>/meet-wise.git
cd meet-wise
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
# venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the backend folder:

```text
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/meetwise
GEMINI_API_KEY=<your_gemini_api_key>
```

Run the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

Access the frontend at: [http://localhost:5173](http://localhost:5173)

---

## API Usage Examples

### Create a Meeting

```bash
curl -X POST http://127.0.0.1:8000/meetings \
-H "Content-Type: application/json" \
-d '{"title": "Team Sync", "date": "2025-09-30", "created_by": "Parthavi"}'
```

### Add Participants

```bash
curl -X POST http://127.0.0.1:8000/meetings/<meeting_id>/participants \
-H "Content-Type: application/json" \
-d '[{"name": "Parthavi"}, {"name": "Sneha"}]'
```

### Add Meeting Transcript

```bash
curl -X POST http://127.0.0.1:8000/meetings/<meeting_id>/artifacts/text \
-H "Content-Type: application/json" \
-d '{"text": "Meeting started with agenda discussion and task assignment."}'
```

### Get Meeting Summary

```bash
curl -X GET http://127.0.0.1:8000/meetings/<meeting_id>/summary
```






