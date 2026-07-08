from typing import Optional
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvoiceRequest(BaseModel):
    text: Optional[str] = ""


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    text = (req.text or "").strip()

    vendor = ""
    amount = 0.0
    currency = "USD"
    date = ""

    if text:

        # -------- Vendor --------
        vendor_patterns = [
            r"Vendor\s*:\s*(.+)",
            r"Supplier\s*:\s*(.+)",
            r"From\s*:\s*(.+)"
        ]

        for p in vendor_patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                vendor = m.group(1).splitlines()[0].strip()
                break

        if not vendor:
            vendor = text.splitlines()[0].strip()

        # -------- Amount --------
        amount_patterns = [
            r"Total\s+Due\s*:\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
            r"Amount\s+Due\s*:\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
            r"Total\s*:\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
            r"Amount\s*:\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
            r"(?:USD|EUR|GBP)\s+([0-9]+(?:\.[0-9]{1,2})?)",
            r"[$€£]\s*([0-9]+(?:\.[0-9]{1,2})?)",
        ]

        for p in amount_patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                try:
                    amount = float(m.group(1))
                    break
                except ValueError:
                    pass

        # -------- Currency --------
        m = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
        if m:
            currency = m.group(1).upper()
        elif "€" in text:
            currency = "EUR"
        elif "£" in text:
            currency = "GBP"
        elif "$" in text:
            currency = "USD"

        # -------- Date --------
        m = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
        if m:
            date = m.group(1)

    return {
        "vendor": vendor,
        "amount": float(amount),
        "currency": currency,
        "date": date,
    }