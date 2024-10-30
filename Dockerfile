FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY receipt_processor.py .

EXPOSE 8000

CMD ["uvicorn", "receipt_processor:app", "--host", "0.0.0.0", "--port", "8000"]
