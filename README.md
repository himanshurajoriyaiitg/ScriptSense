# ScriptSense

A Human-in-the-Loop (HITL) exam grading pipeline. Professors upload bulk handwritten exam scans and JSON rubrics. A vision model transcribes the answers, a LangGraph agentic pipeline grades them with partial credit and justifications, and TAs review/approve/override on a high-speed dashboard.

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| ML Pipeline | LangGraph + LangChain + Groq (OCR + Grading) |
| Storage | Local filesystem |
| Frontend | React + Vite + Redux Toolkit |

## Requirements

- Python 3.11
- Node.js 20+
- PostgreSQL 16+
- Groq API key (free at console.groq.com)

## Local Setup

### Option 1: Docker (Recommended)

1. **Set up environment variables:**
   Copy `.env.example` to `.env` and fill in `GROQ_API_KEY`.
   ```bash
   cp .env.example .env     # (macOS/Linux)
   copy .env.example .env   # (Windows)
   ```

2. **Run the containers:**
   ```bash
   docker compose up -d --build
   ```

3. **Open the app:**
   Go to `http://localhost:5173`.

### Option 2: Manual Setup (If you don't use Docker)

1. **Set up the `.env` file:**
   Copy the `.env.example` file to create a new `.env` file.
   ```bash
   cp .env.example .env     # (macOS/Linux)
   copy .env.example .env   # (Windows)
   ```

2. **Install PostgreSQL:**
   - Download and install PostgreSQL (version 16 or latest) from the [official website](https://www.postgresql.org/download/).
   - **Important:** During installation, it will ask you to set a password for the default `postgres` superuser. Remember this password!
   - Leave the default port as `5432`.

3. **Create the Database (using pgAdmin or psql):**
   - **Via pgAdmin (GUI for Windows/Mac):**
     1. Open **pgAdmin 4** and log in with your master password.
     2. Expand **Servers** -> **PostgreSQL**.
     3. Right-click on **Databases** -> **Create** -> **Database...**
     4. Set the Database name to `scriptsense` and click **Save**.
   - **Via psql (Terminal):**
     ```sql
     CREATE USER scriptsense WITH PASSWORD 'scriptsense';
     CREATE DATABASE scriptsense OWNER scriptsense;
     GRANT ALL ON SCHEMA public TO scriptsense;
     ALTER DATABASE scriptsense OWNER TO scriptsense;
     ```

4. **Update your `.env` file:**
   Open the `.env` file you created and update the `DATABASE_URL` line to match your new database credentials.
   If using the default `postgres` user from your installation, it should look like:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/scriptsense
   ```
   *(Replace `YOUR_PASSWORD_HERE` with the password you set during installation).*
   
   Also, don't forget to add your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

5. **Set up Python venv and install dependencies:**
   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

6. **Start the backend:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

7. **Start the frontend:**
   Open a new terminal:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

8. **Open the app:**
   Go to `http://localhost:5173`.

### Seeding Demo Data (Optional)
To test the app, you can seed demo data by running the following script with your Python environment active:
```bash
# Windows
set PYTHONPATH=backend
python scripts/seed_db.py

# macOS/Linux
PYTHONPATH=backend python scripts/seed_db.py
```
*(If using Docker, run this script inside the backend container or locally if Python is installed).*

**Demo credentials:**
- Instructor: `instructor@scriptsense.com` / `password123`
- TA: `ta@scriptsense.com` / `password123`

## Project Structure
backend/
main.py                   FastAPI app entry point
config.py                 Pydantic settings (reads .env)
database.py               SQLAlchemy engine + session
models/                   SQLAlchemy ORM models
schemas/                  Pydantic request/response schemas
routers/                  API route handlers
auth.py                 Register, login, /me
upload.py               Create exams, upload PDFs
grade.py                Fetch grades & summary
review.py               TA approve/override endpoints
pipeline/
ocr.py                  Groq vision PDF → text extraction
rubric_parser.py        Parse rubric JSON, build grading prompts
grader_agent.py         Groq LLM answer grader
plagiarism.py           TF-IDF cosine similarity detection
langgraph_workflow.py   Orchestration: extract → grade → plagiarism
utils/
jwt.py                  Auth helpers, route guards
cloud_storage.py        Local file storage (replaces GCS)
uploads/                  Locally stored PDFs and cropped images
frontend/
src/
pages/
LoginPage.jsx
DashboardPage.jsx     Exam list with status cards
UploadPage.jsx        Create exam + bulk PDF upload
ReviewPage.jsx        TA review dashboard (keyboard shortcuts)
components/Navbar.jsx
store/index.js          Redux Toolkit slices (auth, exams, grades)
api/index.js            Axios instance with auth interceptor
scripts/
seed_db.py                Insert demo data

## Rubric JSON Format

```json
{
  "questions": [
    {
      "number": 1,
      "text": "Explain the difference between a stack and a queue.",
      "max_score": 10,
      "criteria": [
        { "description": "Correct definition of stack (LIFO)", "points": 3 },
        { "description": "Correct definition of queue (FIFO)", "points": 3 },
        { "description": "Real-world example for stack", "points": 2 },
        { "description": "Real-world example for queue", "points": 2 }
      ]
    }
  ]
}
```

## Review Dashboard Keyboard Shortcuts

| Key | Action |
|---|---|
| `A` | Approve current grade |
| `O` | Open override modal |
| `← / P` | Previous grade |
| `→ / N` | Next grade |
| `Esc` | Close modal |
