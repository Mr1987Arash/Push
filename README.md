# README.md
# Push - MVP

This repository contains a small FastAPI backend with WebSocket chat rooms, Redis pub/sub for scaling across instances, JWT auth with HttpOnly cookies, and docker-compose for local dev.

Branches:
- feature/base-secure: initial MVP
- feature/redis-alembic: added Redis pubsub and Alembic migrations
- feature/secure-ws: TLS-ready nginx config and secure cookie flow

Quick start:
  cp .env.example .env
  docker-compose up --build -d
  docker-compose exec backend bash -c "alembic upgrade head"
  docker-compose up --build
  Open http://localhost:8080/login.html
