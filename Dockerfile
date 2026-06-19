FROM python:3.12-slim

# Don't buffer stdout, so logs show up immediately in `kubectl logs`
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lease_worker.py .

# Run as a non-root user (good practice)
RUN useradd -u 10001 -m worker
USER 10001

CMD ["python", "lease_worker.py"]
