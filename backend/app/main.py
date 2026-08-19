# backend/app/main.py
import os
import time
from typing import Optional, Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sqlalchemy as sa
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))

# --- Database (simple SQLAlchemy sync) ---
engine = sa.create_engine(DATABASE_URL, future=True)
metadata = sa.MetaData()
users_table = sa.Table(
    'users', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(128), unique=True, nullable=False),
    sa.Column('hashed_password', sa.String(256), nullable=False),
    sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
)
metadata.create_all(engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Push - secure MVP")

# In-memory room manager (for MVP). For scale, replace with Redis pub/sub.
rooms: Dict[str, Set[WebSocket]] = {}

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post('/api/register', response_model=dict)
def register(user: UserCreate):
    with engine.begin() as conn:
        sel = sa.select(users_table).where(users_table.c.username == user.username)
        r = conn.execute(sel).first()
        if r:
            raise HTTPException(status_code=400, detail='username already exists')
        hashed = get_password_hash(user.password)
        ins = users_table.insert().values(username=user.username, hashed_password=hashed)
        conn.execute(ins)
    return {"ok": True}

@app.post('/api/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with engine.connect() as conn:
        sel = sa.select(users_table).where(users_table.c.username == form_data.username)
        r = conn.execute(sel).first()
        if not r:
            raise HTTPException(status_code=400, detail='Incorrect username or password')
        user = r
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail='Incorrect username or password')
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get current user from token
from fastapi import Header

def get_current_username(token: str = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token header")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get('/api/me')
def me(username: str = Depends(get_current_username)):
    return {"username": username}

@app.websocket('/ws/room/{room_id}')
async def websocket_room(websocket: WebSocket, room_id: str):
    # token passed as query param ?token=...
    token = websocket.query_params.get('token')
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if not username:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    # add to room
    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # broadcast to all in room
            dead = []
            for ws in rooms.get(room_id, set()):
                try:
                    await ws.send_text(f"{username}: {data}")
                except Exception:
                    dead.append(ws)
            for d in dead:
                rooms[room_id].discard(d)
    except WebSocketDisconnect:
        rooms[room_id].discard(websocket)

@app.get('/')
def index():
    return {"ok": True, "ts": int(time.time())}

