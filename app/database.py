from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from pathlib import Path
from dotenv import load_dotenv

import os


# DATABASE_URL = "postgresql://hatan_palace_db_envb_user:CrInGP3c2bGSvk881a5MChVsuEn87UWs@dpg-d7toedbtqb8s73d5pplg-a/hatan_palace_db_envb"
DATABASE_URL = os.getenv("DATABASE_URL")

# if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
#     DATABASE_URL = DATABASE_URL.replace(
#         "postgresql://",
#         "postgresql+psycopg2://",
#         1
#     )

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from environment variables.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()