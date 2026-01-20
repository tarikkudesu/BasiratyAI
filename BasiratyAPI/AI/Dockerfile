# Stage 1: Build stage to install dependencies

FROM python:3.11-slim-bullseye AS builder
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt


# Stage 2: Final production stage
FROM python:3.11-slim-bullseye
ENV APP_HOME=/home/app/web
WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends --fix-missing \
    libgl1-mesa-glx \
    libglib2.0-0 \
    || (apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0) \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/*

EXPOSE 7417
COPY config.py .
COPY main.py .
COPY core/ ./core/
COPY detection/ ./detection/
COPY services/ ./services/
COPY utils/ ./utils/

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7417", "--reload"]
