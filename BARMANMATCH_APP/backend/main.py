import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes import auth, workers, venues, shifts, matching, ratings, contracts, companies, events, policy, payments

load_dotenv()

app = FastAPI(title="BarmanMatch API", version="0.1.0-mvp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("FRONTEND_ORIGIN", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,     prefix="/api/auth",     tags=["auth"])
app.include_router(workers.router,  prefix="/api/workers",  tags=["workers"])
app.include_router(venues.router,   prefix="/api/venues",   tags=["venues"])
app.include_router(shifts.router,   prefix="/api/shifts",   tags=["shifts"])
app.include_router(matching.router, prefix="/api/matching", tags=["matching"])
app.include_router(ratings.router,  prefix="/api/ratings",  tags=["ratings"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["contracts"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(events.router,    prefix="/api/events",    tags=["events"])
app.include_router(policy.router,    prefix="/api/policy",    tags=["policy"])
app.include_router(payments.router,  prefix="/api/payments",  tags=["payments"])


@app.get("/")
def root():
    return {"status": "ok", "version": "0.1.0-mvp", "service": "BarmanMatch API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
