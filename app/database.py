from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://hatan_palace_db_envb_user:CrInGP3c2bGSvk881a5MChVsuEn87UWs@dpg-d7toedbtqb8s73d5pplg-a/hatan_palace_db_envb"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()