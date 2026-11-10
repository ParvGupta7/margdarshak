# MargDarshak

A web app that reads a resume and turns it into practical career guidance:
what skills you already have, which roles suit you, what you are missing,
where to learn it, and which openings are live right now. A built-in
assistant answers follow-up questions about your results.

> This repository accompanies a research paper that is currently under
> review. A citation will be added here after publication.

## What you get

- A profile summary (contact details, location, detected skills)
- A ranked list of suitable roles
- Missing skills for each role, plus a readiness indicator
- Free learning links for those skills
- Current job openings for your best-fit role and city
- A chat assistant that answers questions using your own results

## Getting started

You need Python 3.11 or 3.12 and Node.js 18 or newer.

**Backend**

    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    cp .env.example .env
    python main.py

**Frontend**

    cd frontend
    npm install
    npm run dev

Then open http://localhost:5173.

## Configuration

Job listings come from the Adzuna API. Create a free account at
developer.adzuna.com and put your keys in `backend/.env`:

    ADZUNA_APP_ID=your_app_id
    ADZUNA_APP_KEY=your_app_key

Without keys, everything except live job listings still works.

## Project layout

    backend/
      main.py          API entry point
      pipeline/        resume processing modules
      chatbot/         chat assistant
      data/            skill list, role definitions, course links
    frontend/src/      React interface
    evaluation/        datasets and scripts used for the reported results

## Notes

- PDF is the supported resume format. Image upload through OCR is an
  experimental extra and needs the Tesseract engine installed separately.
- Role definitions reference O*NET-SOC occupation codes
  (onetonline.org). The skill lists inside them were compiled by the
  project authors.
- The chat assistant uses a small trained classifier. If the model files
  are missing, it switches to a simpler keyword-based mode.

## Contributing

Issues and pull requests are welcome.
