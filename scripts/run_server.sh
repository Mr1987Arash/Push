#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
# Run uvicorn for backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
