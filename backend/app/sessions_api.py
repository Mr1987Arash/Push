from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# mount static files to serve the admin page
import os
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

@app.get('/admin/sessions', response_class=HTMLResponse)
def admin_sessions():
    # simple page
    fn = os.path.join(static_dir, 'admin_sessions.html')
    with open(fn, 'r', encoding='utf-8') as f:
        return HTMLResponse(f.read())

# Sessions management endpoints
@app.get('/api/sessions')
def list_sessions(username: str = Depends(get_current_username)):
    # return list of refresh tokens for current user
    with engine.connect() as conn:
        sel_user = sa.select(users_table.c.id).where(users_table.c.username == username)
        u = conn.execute(sel_user).first()
        if not u:
            raise HTTPException(status_code=404, detail='user not found')
        sel = sa.select(refresh_tokens_table.c.id, refresh_tokens_table.c.created_at, refresh_tokens_table.c.expires_at, refresh_tokens_table.c.revoked, refresh_tokens_table.c.ip_address, refresh_tokens_table.c.user_agent).where(refresh_tokens_table.c.user_id == u.id)
        rows = conn.execute(sel).all()
        out = []
        for r in rows:
            out.append({
                'id': r.id,
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'expires_at': r.expires_at.isoformat() if r.expires_at else None,
                'revoked': bool(r.revoked),
                'ip_address': r.ip_address,
                'user_agent': r.user_agent
            })
        return out

@app.delete('/api/sessions/{session_id}')
def revoke_session(session_id: int, username: str = Depends(get_current_username)):
    with engine.begin() as conn:
        # ensure session belongs to user
        sel = sa.select(refresh_tokens_table.c.user_id).where(refresh_tokens_table.c.id == session_id)
        row = conn.execute(sel).first()
        if not row:
            raise HTTPException(status_code=404, detail='session not found')
        if row.user_id is None:
            raise HTTPException(status_code=404, detail='session not found')
        # get user id
        sel_user = sa.select(users_table.c.id).where(users_table.c.username == username)
        u = conn.execute(sel_user).first()
        if not u or u.id != row.user_id:
            raise HTTPException(status_code=403, detail='not authorized')
        conn.execute(refresh_tokens_table.update().where(refresh_tokens_table.c.id == session_id).values(revoked=True))
        return {'ok': True}
