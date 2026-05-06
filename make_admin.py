from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schema import User # Se till att stigen stämmer

# ANVÄND DIN "EXTERNAL DATABASE URL" FRÅN RENDER HÄR
EXTERNAL_URL = "postgresql://hatan_palace_db_envb_user:CrInGP3c2bGSvk881a5MChVsuEn87UWs@dpg-d7toedbtqb8s73d5pplg-a.frankfurt-postgres.render.com/hatan_palace_db_envb"

engine = create_engine(EXTERNAL_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Hitta din användare via e-post
email_to_promote = "Even@gmail.com"
user = session.query(User).filter(User.email == email_to_promote).first()

if user:
    user.is_admin = True
    session.commit()
    print(f"Success! {email_to_promote} är nu admin.")
else:
    print("Hittade ingen användare med den e-postadressen.")

session.close()