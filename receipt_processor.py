from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
import math

app = FastAPI()
receipt_data = {}

class Item(BaseModel):
    shortDescription: str
    price: str

class Receipt(BaseModel):
    retailer: str
    purchaseDate: str
    purchaseTime: str
    items: list[Item]
    total: str

def calculate_points(receipt: Receipt):
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name
    points += sum([1 for c in receipt.retailer if c.isalnum()])

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total_amount = float(receipt.total)
    if int(total_amount) == total_amount:
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if total_amount % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    points += (len(receipt.items) // 2) * 5

    # Rule 5: Points for item description length being multiple of 3
    for item in receipt.items:
        trimmed_description = item.shortDescription.strip()
        if len(trimmed_description) % 3 == 0:
            price_points = math.ceil(float(item.price) * 0.2)
            points += price_points

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00 pm and before 4:00 pm
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M")
    if 14 <= purchase_time.hour < 16:  
        points += 10

    return points

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "The receipt is invalid", "errors": exc.errors()},
    )

@app.post("/receipts/process")
async def process_receipt(receipt: Receipt):
    receipt_id = str(uuid4())
    points = calculate_points(receipt)
    receipt_data[receipt_id] = points
    return {"id": receipt_id}

@app.get("/receipts/{id}/points")
async def get_points(id: str):
    if id not in receipt_data:
        raise HTTPException(status_code=404, detail="No receipt found for that id")
    return {"points": receipt_data[id]}

