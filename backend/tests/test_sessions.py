# backend/tests/test_sessions.py
import os
import tempfile
import time
import json
from fastapi.testclient import TestClient

# ensure test DB
os.environ['DATABASE_URL'] = 'sqlite:///./test_db.sqlite'
from app.main import app

client = TestClient(app)

USERNAME = 'testuser'
PASSWORD = 'pass123'

def test_register_login_refresh_logout():
    # register
    r = client.post('/api/register', json={'username': USERNAME, 'password': PASSWORD})
    assert r.status_code == 200
    # login
    r = client.post('/api/login', data={'username': USERNAME, 'password': PASSWORD})
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data
    # cookies are set in client
    # list sessions
    r = client.get('/api/sessions')
    assert r.status_code == 200
    sessions = r.json()
    assert isinstance(sessions, list)
    assert len(sessions) >= 1
    sid = sessions[0]['id']
    # revoke session
    r = client.delete(f'/api/sessions/{sid}')
    assert r.status_code == 200
    # refresh should fail because we revoked
    r = client.post('/api/token/refresh')
    assert r.status_code in (401,)
    # logout ok
    r = client.post('/api/logout')
    assert r.status_code == 200
