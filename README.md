# Ad Channel Spend Optimizer

A small full-stack app that analyzes ad campaign performance across four
channels (Search, Social, Display, Video) and suggests a data-driven
budget reallocation based on ROAS (Return on Ad Spend).

Built with Python (FastAPI) on the backend, SQLite for storage, and Vue 3
on the frontend.

## What it does

- Shows a table of campaigns with computed **CPA** (cost per acquisition)
  and **ROAS** (revenue / spend) per campaign, color-coded against the
  account-wide average.
- A "Get Optimization Suggestion" button calls a backend algorithm that:
  1. Groups campaigns by channel and computes each channel's overall ROAS.
  2. Finds the weakest-performing channel and the strongest-performing channel.
  3. Suggests shifting 15% of the weak channel's spend to the strong one.
  4. Explains the suggestion in plain language.

## Why ROAS, and not clicks or conversions?

Raw clicks and conversions don't tell you whether a channel is actually
making money — a channel can have plenty of conversions but still lose
money if spend is high relative to the revenue those conversions generate.
ROAS (revenue ÷ spend) is the metric that directly answers the business
question: "is this channel worth the budget it's getting?" That's why it
was chosen as the ranking metric for the reallocation algorithm instead of
volume-based metrics like clicks or conversion count.

## Project structure

```
ad-spend-optimizer/
├── backend/
│   ├── main.py          # FastAPI app and the two API endpoints
│   ├── database.py      # SQLite setup + seed data
│   ├── optimizer.py     # The reallocation algorithm (kept separate on purpose)
│   └── requirements.txt
├── frontend/
│   └── index.html       # Single-file Vue 3 dashboard (no build step needed)
└── README.md
```

## How to run it locally

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python database.py        # creates and seeds campaigns.db
uvicorn main:app --reload # starts the API on http://localhost:8000
```

Leave this running in one terminal.

### 2. Frontend

No build step required — it's a single HTML file that talks to the API
over `fetch`. Just open it in a browser:

```bash
# from the frontend/ folder, either double-click index.html, or serve it:
cd frontend
python -m http.server 5500
```

Then visit `http://localhost:5500` (or just open `index.html` directly
in your browser — either works, since it's a static file).

## API endpoints

- `GET /campaigns` — all campaigns with computed CPA/ROAS, plus the
  account-wide average ROAS.
- `GET /suggest-reallocation` — the reallocation suggestion, as both
  structured JSON (`from_channel`, `to_channel`, `amount`, `reason`) and
  a human-readable sentence.

## Notes on scope

This project is deliberately kept small: one table, two endpoints, one
page. No authentication, multi-tenancy, or deployment pipeline — the goal
was a project that's fully understandable end-to-end, including every
line of the optimization logic in `optimizer.py`.
