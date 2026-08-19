feature(refresh-tokens): add refresh token rotation, logout, sessions management

This PR adds refresh token support with rotation and session management.

Changes include:
- Alembic migration to add refresh_tokens table
- /api/login: issues access token and refresh token, stores hashed refresh token and sets HttpOnly cookie
- /api/token/refresh: validates refresh cookie or body-sent token, rotates token, issues new access token
- /api/logout: revokes current refresh token and clears cookie
- /api/sessions: list user's refresh token sessions
- DELETE /api/sessions/{id}: revoke specific session
- Admin UI page at /admin/sessions to view and revoke sessions
- Unit tests using pytest and FastAPI TestClient for basic flow

Notes:
- Refresh tokens are hashed with SHA-256 before storing in DB.
- Rotation is enabled: refresh tokens are invalidated when used.
- Cookie security flags depend on COOKIE_SECURE env var.
