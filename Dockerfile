FROM python:3.10.6 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app


RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt
RUN apt-get update && apt-get install -y curl net-tools procps bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
FROM python:3.10.6-slim
WORKDIR /app
COPY --from=builder /app/.venv .venv/
COPY . .
CMD ["/app/.venv/bin/python", "main.py"]
