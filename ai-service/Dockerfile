# syntax=docker/dockerfile:1

FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHON_EXECUTABLE=python \
    APP_SCRIPT_ROOT=/app/scripts

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY ai-service/requirements.txt /app/requirements.txt
COPY requirements-sync.txt /app/scripts/requirements-sync.txt
RUN pip install --no-cache-dir -r /app/requirements.txt -r /app/scripts/requirements-sync.txt

COPY ai-service/app /app/app
COPY scripts/sync/ /app/scripts/sync/

EXPOSE 8082
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082"]
