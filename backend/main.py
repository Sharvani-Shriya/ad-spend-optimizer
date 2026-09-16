"""
main.py

FastAPI app exposing two endpoints:
  GET /campaigns            -> all campaigns with computed CPA and ROAS
  GET /suggest-reallocation -> the budget reallocation suggestion

Run with:
    uvicorn main:app --reload
Then open frontend/index.html in a browser (it calls http://localhost:8000).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from optimizer import suggest_reallocation

app = FastAPI(title="Ad Channel Spend Optimizer")

# Allow the frontend (opened as a local static file, or via a dev server)
# to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    # Ensures the DB exists and is seeded the first time the server starts.
    # reset=False so restarting the server doesn't wipe manual edits.
    init_db(reset=False)


def row_to_campaign_dict(row) -> dict:
    """Converts a DB row into a dict with computed CPA and ROAS fields."""
    spend = row["spend"]
    conversions = row["conversions"]
    revenue = row["revenue"]

    cpa = round(spend / conversions, 2) if conversions > 0 else None
    roas = round(revenue / spend, 2) if spend > 0 else None

    return {
        "id": row["id"],
        "name": row["name"],
        "channel": row["channel"],
        "spend": spend,
        "clicks": row["clicks"],
        "conversions": conversions,
        "revenue": revenue,
        "cpa": cpa,
        "roas": roas,
    }


@app.get("/campaigns")
def get_campaigns():
    """Returns all campaigns with computed CPA and ROAS per campaign."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM campaigns ORDER BY channel, id").fetchall()
    conn.close()

    campaigns = [row_to_campaign_dict(r) for r in rows]

    # also compute the account-wide average ROAS, used by the frontend
    # to decide whether to color a campaign's ROAS green or red
    valid_roas = [c["roas"] for c in campaigns if c["roas"] is not None]
    avg_roas = round(sum(valid_roas) / len(valid_roas), 2) if valid_roas else None

    return {"campaigns": campaigns, "average_roas": avg_roas}


@app.get("/suggest-reallocation")
def get_suggestion():
    """Returns the budget reallocation suggestion computed from current
    campaign data. See optimizer.py for the algorithm itself."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM campaigns").fetchall()
    conn.close()

    campaigns = [dict(r) for r in rows]
    return suggest_reallocation(campaigns)


@app.get("/")
def root():
    return {
        "message": "Ad Channel Spend Optimizer API",
        "endpoints": ["/campaigns", "/suggest-reallocation"],
    }
