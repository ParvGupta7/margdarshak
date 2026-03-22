# MargDarshak — AI Resume Analyzer & Career Guidance Platform

An NLP-powered platform that analyzes resumes through a demonstrable 9-step pipeline,
identifies skills, classifies job roles, finds skill gaps, recommends courses, and
matches live job listings.

---

## Prerequisites

- macOS with Homebrew
- Python 3.11+
- Node.js 18+

Install if not present:

```bash
# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python
brew install python@3.11

# Node
brew install node
```

---

## Step 1 — Get API Keys (Both Free)

### Anthropic (Claude) — for the chatbot
1. Go to https://console.anthropic.com
2. Sign up or log in
3. Click "API Keys" in the left sidebar
4. Click "Create Key" — copy it

### Adzuna — for live job listings
1. Go to https://developer.adzuna.com
2. Click "Register" — fill in the form (free)
3. After login, go to "Dashboard" → "Create Application"
4. You get an App ID and App Key — copy both

---

## Step 2 — Backend Setup

Open a terminal and run these commands one by one:

```bash
# Navigate into the backend folder
cd margdarshak/backend

# Create a Python virtual environment
python3 -m venv venv

# Activate it (you must do this every time you open a new terminal)
source venv/bin/activate

# Install all Python dependencies
pip install -r requirements.txt

# Download the spaCy English language model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

### Create your .env file

```bash
cp .env.example .env
```

Open `.env` in VS Code and fill in your keys:

```
ANTHROPIC_API_KEY=sk-ant-...your key here...
ADZUNA_APP_ID=...your id here...
ADZUNA_APP_KEY=...your key here...
```

### Start the backend

```bash
# Make sure you are in margdarshak/backend with venv activated
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

Leave this terminal running. Open a new terminal for the frontend.

---

## Step 3 — Frontend Setup

Open a new terminal tab (Command + T in Terminal or iTerm):

```bash
# Navigate to the frontend folder
cd margdarshak/frontend

# Install JavaScript dependencies
npm install

# Start the development server
npm run dev
```

You should see:
```
VITE ready in Xms
Local: http://localhost:5173/
```

Open http://localhost:5173 in your browser.

---

## Step 4 — Test It

1. Open http://localhost:5173
2. Upload a PDF resume (drag and drop or click)
3. Click "Analyze Resume"
4. Wait ~15-20 seconds for the full pipeline to run
5. Explore all tabs — Profile, Skills, Job Roles, Skill Gaps, Courses, Live Jobs
6. Click the "NLP Pipeline" tab to see each step's output (good for teacher demo)
7. Use the chatbot (bottom right) to ask questions about the resume

---

## Project Structure

```
margdarshak/
├── backend/
│   ├── main.py                    # FastAPI server — all routes
│   ├── requirements.txt
│   ├── .env.example               # Copy to .env and add your keys
│   ├── pipeline/
│   │   ├── extractor.py           # Step 1: PDF text extraction (pdfminer.six)
│   │   ├── preprocessor.py        # Step 2: NLP preprocessing (NLTK)
│   │   ├── parser.py              # Step 3: Entity extraction (Regex + spaCy)
│   │   ├── skill_extractor.py     # Step 4: Skill mapping (fuzzywuzzy)
│   │   ├── job_classifier.py      # Step 5: Role classification (scikit-learn)
│   │   ├── gap_analyzer.py        # Step 6: Skill gap analysis (set ops)
│   │   ├── course_recommender.py  # Step 7: Course recommendations
│   │   └── job_matcher.py         # Step 8: Live jobs (Adzuna API)
│   ├── chatbot/
│   │   └── bot.py                 # Step 9: Chatbot (Claude API)
│   └── data/
│       ├── skills_db.py           # 500+ skills across 15 categories
│       ├── job_roles.py           # 12 job roles with required/preferred skills
│       └── courses_db.py          # Skill → free course mapping
│
└── frontend/
    └── src/
        ├── App.jsx
        ├── pages/
        │   ├── UploadPage.jsx     # Landing + drag-and-drop upload
        │   └── DashboardPage.jsx  # Results dashboard with tabs
        └── components/
            ├── ProfilePanel.jsx   # Contact info + role summary
            ├── SkillsPanel.jsx    # Categorized skills with match method
            ├── JobRolesPanel.jsx  # Ranked job roles with scores
            ├── GapPanel.jsx       # Missing skills per role
            ├── CoursesPanel.jsx   # Free course links per missing skill
            ├── JobsPanel.jsx      # Live job listings
            ├── PipelinePanel.jsx  # NLP pipeline demo view
            └── Chatbot.jsx        # Floating chatbot panel
```

---

## NLP Pipeline Summary (for your teacher)

| Step | File | Method | Libraries |
|------|------|--------|-----------|
| 1. Text Extraction | extractor.py | LAParams-based PDF parsing | pdfminer.six |
| 2. Preprocessing | preprocessor.py | 7-stage NLP pipeline | NLTK |
| 3. Entity Extraction | parser.py | Regex + Named Entity Recognition | re, spaCy |
| 4. Skill Extraction | skill_extractor.py | Exact + fuzzy string matching | fuzzywuzzy |
| 5. Job Classification | job_classifier.py | Cosine similarity on skill vectors | scikit-learn, numpy |
| 6. Gap Analysis | gap_analyzer.py | Set subtraction | Python sets |
| 7. Course Recommendation | course_recommender.py | Dictionary lookup + partial match | — |
| 8. Job Matching | job_matcher.py | REST API call | requests |
| 9. Chatbot | bot.py | Intent classification + LLM | anthropic |

---

## Common Issues

**"spaCy model not found"**
```bash
python -m spacy download en_core_web_sm
```

**"Module not found" errors**
Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

**"No text found in PDF"**
The PDF may be image-based (scanned). Use a text-based PDF resume.

**Jobs show placeholder instead of real listings**
Your Adzuna keys are not in `.env`. Add them and restart the backend.

**Chatbot says "not configured"**
Your Anthropic key is not in `.env`. Add it and restart the backend.

**Frontend can't reach backend**
Make sure the backend is running on port 8000. Check for error messages in the backend terminal.

---

## Deployment (after local testing works)

### Backend → Render.com (free)
1. Push your code to a GitHub repository
2. Go to render.com → "New Web Service"
3. Connect your GitHub repo, set Root Directory to `backend`
4. Build command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (your keys) in the Render dashboard

### Frontend → Vercel (free)
1. Go to vercel.com → "New Project"
2. Import your GitHub repo, set Root Directory to `frontend`
3. In `frontend/src/utils/api.js`, change `BASE_URL` to your Render backend URL
4. Deploy

---

Built with FastAPI, React, NLTK, spaCy, scikit-learn, pdfminer.six, and the Anthropic Claude API.
