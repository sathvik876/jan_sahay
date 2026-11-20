# JanSahay AI – Intelligent Multilingual Citizen Assistance Platform

## Project Overview
A full‑stack AI‑powered web application that helps Indian citizens discover government schemes, check eligibility, analyse official documents and get personalized application guidance.

- **Frontend** – React + Vite + Tailwind CSS (language selector, voice input, chat UI, scheme cards).
- **Backend** – FastAPI (Python) exposing the REST API endpoints listed in the documentation.
- **AI** – Gemini API (text, embeddings, vision) used for conversational understanding and RAG.
- **Vector Store** – ChromaDB (local) for semantic search over scheme documents.
- **Database** – PostgreSQL (or SQLite for quick local testing) storing scheme metadata and eligibility rules.

The project can be started locally with two `npm`/`pip` commands and runs on `http://localhost:3000` (frontend) communicating with the backend at `http://localhost:8000`.

---
## Folder Structure
```
jan_sahay_ai/
├─ frontend/               # React app
│   ├─ public/
│   │   └─ index.html
│   ├─ src/
│   │   ├─ components/
│   │   │   ├─ ChatBox.jsx
│   │   │   ├─ LanguageSelector.jsx
│   │   │   └─ SchemeCard.jsx
│   │   ├─ App.jsx
│   │   └─ main.jsx
│   ├─ tailwind.config.js
│   ├─ vite.config.js
│   └─ package.json
├─ backend/                # FastAPI server
│   ├─ app/
│   │   ├─ __init__.py
│   │   ├─ api.py          # endpoint definitions
│   │   ├─ models.py       # Pydantic models
│   │   ├─ db.py           # DB connection + SQLAlchemy models
│   │   ├─ rag.py          # simple RAG helper (ChromaDB)
│   │   └─ eligibility.py # rule‑engine stub
│   ├─ requirements.txt
│   ├─ main.py
│   └─ .env.example
├─ .gitignore
└─ docs/ (optional docs)
```
---
## Setup Instructions
### Prerequisites
- **Node.js** (>=18) and **npm**
- **Python** (>=3.10) with `pip`
- **PostgreSQL** (or use SQLite – the DB URL can be changed in `.env`)
- **Git** (optional, for cloning)

### 1. Clone / create the project folder
```bash
# In your workspace directory
mkdir jan_sahay_ai && cd jan_sahay_ai
```
*(The folder hierarchy above has already been created for you – see the file list below.)*

### 2. Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
# Copy the example env and insert your Gemini API key
copy .env.example .env
```
Edit `.env` and set `GEMINI_API_KEY=your_key_here`.
```bash
# Run the FastAPI server
uvicorn main:app --reload --port 8000
```
The API docs are available at `http://localhost:8000/docs`.

### 3. Frontend setup
```bash
cd ..\frontend
npm install
npm run dev   # Vite starts on http://localhost:3000
```
The React app proxies API calls to `http://localhost:8000` (see `vite.config.js`).
---
## Important Files (generated for you)
- **frontend/package.json** – defines React, Vite, Tailwind and a proxy.
- **frontend/src/components/** – UI components (`ChatBox`, `LanguageSelector`, `SchemeCard`).
- **backend/app/api.py** – implements the endpoints described in your spec.
- **backend/app/rag.py** – minimal RAG wrapper that loads documents into ChromaDB and returns relevant passages.
- **backend/app/eligibility.py** – rule‑engine placeholder that matches user data against stored eligibility rules.
- **backend/.env.example** – skeleton for environment variables.
---
## Running the Full Stack
1. Start the backend (`uvicorn`).
2. In another terminal, start the frontend (`npm run dev`).
3. Open the browser at `http://localhost:3000`.
4. Choose a language, type or press the microphone (voice integration is a stub – you can hook BHASHINI later), ask a question such as:
   ```
   I am a college student in Telangana with family income 1.5 lakh per year. Which scholarships can I apply for?
   ```
5. The chat UI shows the Gemini‑generated answer with citations and a list of **SchemeCard** components.
---
## Extending the Project
- **Voice integration** – replace the `recordAudio` stub in `ChatBox.jsx` with BHASHINI or another speech‑to‑text service.
- **Document analyzer** – implement `/api/documents/analyze` using `pymupdf` + Gemini Vision as shown in `backend/app/rag.py`.
- **Authentication** – add `fastapi-users` or JWT for optional user accounts.
- **Deploy** – the frontend can be deployed on Vercel, the backend on Render, Railway, or any container platform.
---
## License & Disclaimer
This code is provided **for educational / hack‑athon purposes only**. The platform does **not** issue official government approvals. All data must be verified manually before production use.

---
## Next Steps for the Hackathon
- Populate the `schemes` table with 10‑15 verified schemes (see the `docs/initial_data.sql` file you can add).
- Write unit tests for the eligibility engine (`backend/tests/test_eligibility.py`).
- Record a short demo video showing the Telugu voice flow and the generated checklist.

Happy hacking!
