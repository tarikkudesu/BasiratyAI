#!/bin/sh

set -e
cloudflared tunnel --url http://localhost:7417 &
exec python -m uvicorn main:app --host 0.0.0.0 --port 7417 --reload
