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
def extract(req: InvoiceRequest):

    text = req.text

    vendor = ""

    for pat in [
        r"Vendor:\s*(.+)",
        r"Supplier:\s*(.+)",
        r"From:\s*(.+)"
    ]:
        m = re.search(pat, text, re.I)
        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    if vendor == "":
        vendor = text.split("\n")[0].strip()

    amount = 0.0

    for pat in [
        r"Total\s+Due[:\s]*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"Amount\s+Due[:\s]*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"Total[:\s]*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"Amount[:\s]*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
    ]:
        m = re.search(pat, text, re.I)
        if m:
            amount = float(m.group(1))
            break

    currency = "USD"

    m = re.search(r"\b(USD|EUR|GBP)\b", text)
    if m:
        currency = m.group(1)

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