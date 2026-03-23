import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis

postgres_user = os.getenv("POSTGRES_USER", "radius")
postgres_password = os.getenv("POSTGRES_PASSWORD", "radius123!")
postgres_db = os.getenv("POSTGRES_DB", "radius")
postgres_host = os.getenv("POSTGRES_HOST", "postgres")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

redis_password = os.getenv("REDIS_PASSWORD", "redis123!")
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

# Construct PostgreSQL URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Construct Redis connection
redis_client = redis.Redis(
    host=redis_host, 
    port=int(redis_port), 
    password=redis_password, 
    decode_responses=True
)

app = FastAPI(title="NAC Policy Engine")

@app.get("/health")
def health_check():
    # Check DB
    try:
        with engine.connect() as connection:
            pass
        db_status = "ok"
    except Exception as e:
        db_status = str(e)
        
    # Check Redis
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
