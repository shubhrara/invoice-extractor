from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvoiceRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract_invoice(req: InvoiceRequest):
    text = req.text

    if not text.strip():
        return InvoiceResponse(
            vendor="",
            amount=0.0,
            currency="USD",
            date=""
        )

    # ---------- Vendor ----------
    vendor = ""

    patterns = [
        r"Vendor[:\s]+(.+)",
        r"Supplier[:\s]+(.+)",
        r"From[:\s]+(.+)"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    if vendor == "":
        first = text.strip().split("\n")[0]
        vendor = first.strip()

    # ---------- Amount ----------
    amount = 0.0

    amount_patterns = [
        r"Total(?: Due)?[:\s]*[$€£]?([0-9]+(?:\.[0-9]{1,2})?)",
        r"Amount(?: Due)?[:\s]*[$€£]?([0-9]+(?:\.[0-9]{1,2})?)",
        r"Due[:\s]*[$€£]?([0-9]+(?:\.[0-9]{1,2})?)",
        r"[$€£]\s*([0-9]+(?:\.[0-9]{1,2})?)"
    ]

    for p in amount_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    # ---------- Currency ----------
    currency = "USD"

    m = re.search(r"\b(USD|EUR|GBP)\b", text)
    if m:
        currency = m.group(1).upper()
    else:
        if "$" in text:
            currency = "USD"
        elif "€" in text:
            currency = "EUR"
        elif "£" in text:
            currency = "GBP"

    # ---------- Date ----------
    date = ""

    m = re.search(r"(2026-\d{2}-\d{2})", text)
    if m:
        date = m.group(1)

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )