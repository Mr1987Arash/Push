#!/usr/bin/env bash
set -e
# helper script to run a second backend instance (for local redis pubsub testing)
# usage: ./scripts/run_second_backend.sh

docker build -t push-backend-test ./backend

docker run --rm -e DATABASE_URL=${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/pushdb} -e REDIS_URL=${REDIS_URL:-redis://localhost:6379/0} -p 8001:8000 push-backend-test
