import os
import bcrypt
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import redis

from .models import Base, RadCheck, RadReply, RadUserGroup, RadGroupReply, RadAcct
from .schemas import AuthRequest, AuthResponse, AcctRequest, GenericResponse

postgres_user = os.getenv("POSTGRES_USER", "radius")
postgres_password = os.getenv("POSTGRES_PASSWORD", "radius123!")
postgres_db = os.getenv("POSTGRES_DB", "radius")
postgres_host = os.getenv("POSTGRES_HOST", "postgres")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

redis_password = os.getenv("REDIS_PASSWORD", "redis123!")
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = redis.Redis(
    host=redis_host,
    port=int(redis_port),
    password=redis_password,
    decode_responses=True
)

app = FastAPI(title="NAC Policy Engine")

# Jinja2 Templates Setup
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_rate_limited(username: str) -> bool:
    key = f"rate_limit:{username}"
    attempts = redis_client.get(key)
    if attempts and int(attempts) >= 5:
        return True
    return False

def record_failed_attempt(username: str):
    key = f"rate_limit:{username}"
    redis_client.incr(key)
    redis_client.expire(key, 300) # 5 minutes block

def clear_failed_attempts(username: str):
    key = f"rate_limit:{username}"
    redis_client.delete(key)

@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            pass
        db_status = "ok"
    except Exception as e:
        db_status = str(e)
        
    try:
        redis_client.ping()
        redis_status = "ok"
    except Exception as e:
        redis_status = str(e)
        
    return {
        "status": "ok" if db_status == "ok" and redis_status == "ok" else "error",
        "database": db_status,
        "redis": redis_status
    }

@app.post("/auth")
def authenticate(req: AuthRequest, db: Session = Depends(get_db)):
    if is_rate_limited(req.username):
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")

    # MAB (MAC Authentication Bypass)
    if req.mac_address and req.username == req.mac_address:
        user = db.query(RadCheck).filter(RadCheck.username == req.mac_address).first()
        if user:
            return {"status": "ok", "message": "MAB successful"}
        else:
            record_failed_attempt(req.username)
            raise HTTPException(status_code=401, detail="Unauthorized MAC")

    # Standard Auth
    user = db.query(RadCheck).filter(RadCheck.username == req.username, RadCheck.attribute == 'Bcrypt-Password').first()
    if not user:
        # Fallback to plain text check for simplicity
        user = db.query(RadCheck).filter(RadCheck.username == req.username, RadCheck.attribute == 'Cleartext-Password').first()
        if user and req.password and user.value == req.password:
             clear_failed_attempts(req.username)
             return {"status": "ok", "message": "Auth successful"}

        record_failed_attempt(req.username)
        raise HTTPException(status_code=401, detail="User not found or invalid password")
    
    # Check bcrypt password
    try:
        if req.password and bcrypt.checkpw(req.password.encode('utf-8'), user.value.encode('utf-8')):
            clear_failed_attempts(req.username)
            return {"status": "ok", "message": "Auth successful"}
    except Exception:
        pass
        
    record_failed_attempt(req.username)
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/authorize")
def authorize(req: AuthRequest, db: Session = Depends(get_db)):
    control_dict = {"Auth-Type": "rest"}
    
    # MAB Bypass Logic during authorization phase
    if not req.password and req.mac_address and req.username == req.mac_address:
        user = db.query(RadCheck).filter(RadCheck.username == req.mac_address).first()
        if user:
            control_dict["Auth-Type"] = "Accept"
        else:
            control_dict["Auth-Type"] = "Reject"
            return AuthResponse(reply={}, control=control_dict)

    user_group = db.query(RadUserGroup).filter(RadUserGroup.username == req.username).order_by(RadUserGroup.priority).first()
    
    reply_dict = {}
    if user_group:
        group_replies = db.query(RadGroupReply).filter(RadGroupReply.groupname == user_group.groupname).all()
        for grp in group_replies:
            reply_dict[grp.attribute] = grp.value
            
    user_replies = db.query(RadReply).filter(RadReply.username == req.username).all()
    for ur in user_replies:
        reply_dict[ur.attribute] = ur.value

    return AuthResponse(reply=reply_dict, control={})

@app.post("/accounting")
def accounting(req: AcctRequest, db: Session = Depends(get_db)):
    session_key = f"session:{req.session_id}"
    
    if req.status_type.lower() == "start":
        redis_client.set(session_key, req.username)
        acct = RadAcct(
            acctsessionid=req.session_id,
            username=req.username,
            nasipaddress=req.nas_ip,
            callingstationid=req.mac_address,
            acctstarttime=datetime.utcnow()
        )
        db.add(acct)
        db.commit()
    elif req.status_type.lower() in ["interim-update", "alive"]:
         redis_client.expire(session_key, 3600)
         acct = db.query(RadAcct).filter(RadAcct.acctsessionid == req.session_id).order_by(RadAcct.radacctid.desc()).first()
         if acct:
             acct.acctupdatetime = datetime.utcnow()
             acct.acctinputoctets = req.input_octets
             acct.acctoutputoctets = req.output_octets
             acct.acctsessiontime = req.session_time
             db.commit()
    elif req.status_type.lower() == "stop":
         redis_client.delete(session_key)
         acct = db.query(RadAcct).filter(RadAcct.acctsessionid == req.session_id).order_by(RadAcct.radacctid.desc()).first()
         if acct:
             acct.acctstoptime = datetime.utcnow()
             acct.acctinputoctets = req.input_octets
             acct.acctoutputoctets = req.output_octets
             acct.acctsessiontime = req.session_time
             db.commit()
             
    return GenericResponse(status="ok", message="Accounting recorded")

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(RadCheck).all()
    return [{"username": u.username, "attribute": u.attribute} for u in users]

@app.get("/sessions/active")
def get_active_sessions():
    keys = redis_client.keys("session:*")
    sessions = []
    for k in keys:
        uname = redis_client.get(k)
        sessions.append({"session_id": k.replace("session:", ""), "username": uname})
    return sessions

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    users = db.query(RadCheck).all()
    
    # Get active sessions
    keys = redis_client.keys("session:*")
    sessions = []
    for k in keys:
        uname = redis_client.get(k)
        sessions.append({"session_id": k.replace("session:", ""), "username": uname})
        
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "users": users, "sessions": sessions}
    )
