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

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    -o /usr/local/bin/cloudflared \
    && chmod +x /usr/local/bin/cloudflared

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/*

EXPOSE 7417
COPY config.py .
COPY main.py .
COPY best.pt .
COPY core/ ./core/
COPY detection/ ./detection/
COPY services/ ./services/
COPY utils/ ./utils/

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]