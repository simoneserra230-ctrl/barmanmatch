from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time


# ── AUTH ──────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # 'worker' | 'venue'


# ── WORKER ────────────────────────────────────────────────────────
class WorkerProfileCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    city: str
    roles: list[str]
    skills: list[str] = []
    certifications: list[str] = []
    years_experience: int = 0
    bio: Optional[str] = None
    hourly_rate_min: Optional[float] = None


class WorkerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    roles: Optional[list[str]] = None
    skills: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    years_experience: Optional[int] = None
    bio: Optional[str] = None
    hourly_rate_min: Optional[float] = None


# ── VENUE ─────────────────────────────────────────────────────────
class VenueProfileCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    city: str
    venue_type: str
    address: Optional[str] = None
    description: Optional[str] = None
    vat_number: Optional[str] = None      # P.IVA (KYC light)


class VenueProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    venue_type: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    vat_number: Optional[str] = None


# ── SHIFTS ────────────────────────────────────────────────────────
class ShiftCreate(BaseModel):
    role: str
    date: date
    start_time: time
    end_time: time
    hourly_rate: float
    city: str
    requirements: list[str] = []
    description: Optional[str] = None
    dress_code: Optional[str] = None
    spots: int = 1
    is_urgent: bool = False


class ShiftUpdate(BaseModel):
    description: Optional[str] = None
    dress_code: Optional[str] = None
    hourly_rate: Optional[float] = None
    is_urgent: Optional[bool] = None
    status: Optional[str] = None


# ── APPLICATIONS ─────────────────────────────────────────────────
class ApplyRequest(BaseModel):
    contract_accepted: bool = True


class ConfirmApplicationRequest(BaseModel):
    application_id: str


# ── RATINGS ──────────────────────────────────────────────────────
class RatingCreate(BaseModel):
    application_id: str
    score: int
    comment: Optional[str] = None
    # Per venue→worker
    punctuality: Optional[int] = None
    professionalism: Optional[int] = None
    skill_level: Optional[int] = None
    # Per worker→venue
    work_environment: Optional[int] = None
    payment_punctuality: Optional[int] = None


# ── CONTRACTS (tipo Deliveroo) ───────────────────────────────────
class ContractCreate(BaseModel):
    """Opzioni alla generazione del contratto da una candidatura confermata."""
    fee_pct: Optional[float] = None              # override commissione piattaforma
    cancellation_policy: Optional[str] = None
    payment_terms: Optional[str] = None


class ContractComplete(BaseModel):
    actual_hours: Optional[float] = None         # ore effettive (ricalcola i totali)


class ContractCancel(BaseModel):
    reason: Optional[str] = None


# ── COMPANIES (aziende che staffano gli eventi) ──────────────────
class CompanyCreate(BaseModel):
    name: str
    city: Optional[str] = None


# ── EVENTS (Booking.com degli eventi) ────────────────────────────
class EventCreate(BaseModel):
    title: str
    event_type: str = "privato"          # matrimonio|aziendale|privato|catering|altro
    date: date
    start_time: time
    end_time: time
    city: str
    guests: Optional[int] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    priority_hours: Optional[int] = None  # durata finestra prelazione (default env)


class EventCancel(BaseModel):
    reason: Optional[str] = None
