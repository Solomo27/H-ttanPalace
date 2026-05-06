from datetime import date
from pathlib import Path
from tempfile import template
from fastapi import Body, FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import SessionLocal
from app.schema import User, Room, Booking

from app.schema import Base
from app.database import engine


class_img_holder = {"standard": "/static/img/rooms/standard-bed.jpg", "deluxe": "/static/img/rooms/deluxe-bed.jpg", "executive": "/static/img/rooms/executivee-bed.jpg"}



Base.metadata.create_all(bind=engine)




app = FastAPI()


app.add_middleware(SessionMiddleware, secret_key="supersecretkey")


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=BASE_DIR/"templates")

app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_landing_page(request: Request):

    current_user_id = request.session.get("user_id")
    is_admin = request.session.get("admin")

    return templates.TemplateResponse(
        "landing.html",
        {"request": request, 
         "user_id": current_user_id,
         "is_admin": is_admin}
    )

@app.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.get("/signup")
def get_signup_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@app.get("/rooms")
def get_room_page(request: Request):

    current_user_id = request.session.get("user_id")
    is_admin = request.session.get("admin")

    return templates.TemplateResponse(
        "rooms.html",
        {"request": request, 
         "user_id": current_user_id,
         "is_admin": is_admin
        }
    )

@app.get("/bookings")
def get_room_page(request: Request, db: Session=Depends(get_db)):


    current_user_id = request.session.get("user_id")
    is_current_admin = request.session.get("admin")

    my_bookings = db.query(Booking).filter(
        Booking.user_id == current_user_id 
    ).order_by(
        Booking.created_at.desc()
    ).all()

    
    
    return templates.TemplateResponse(
        "bookings.html",
        {"request": request, 
         "user_id": current_user_id,
         "is_admin": is_current_admin,
         "bookings": my_bookings
        }
    )

# Admin Logic

@app.get("/admin")
def get_admin_page(request: Request, db: Session = Depends(get_db)):

    current_user_id = request.session.get("user_id")
    is_admin = request.session.get("admin")

    rooms = db.query(Room).all()
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()


    return templates.TemplateResponse(
        "admin.html",
        {"request": request, 
         "user_id": current_user_id,
         "is_admin": is_admin,
         "rooms": rooms,
         "bookings": bookings}
    )

@app.post("/admin/add-room")
def add_room(
    request: Request, 
    db: Session = Depends(get_db),
    room_number: int = Form(...),
    room_class: str = Form(...),
    max_guests: int = Form(...),
    price: int = Form(...)
):
    room = Room(room_number=room_number, room_class=room_class, 
        price_per_night=price, max_guests=max_guests, image_url=class_img_holder[room_class]
    )

    db.add(room)
    db.commit()
    db.refresh(room)

    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/toggle-room/{room_id}")
def toggle_room(room_id: int, db: Session = Depends(get_db)):

    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.status = not room.status

    db.commit()
    db.refresh(room)

    return {"active": room.status}


#Login Logic And functions

@app.post("/login")
def post_login_toPage(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db) ):
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user or user.password != password:

        return templates.TemplateResponse(
            "login.html",
            {   
                "request": request,
                "error": "Wrong email or password!"
            }
        ) 
            
        
            
    
    request.session["user_id"] = user.id
    request.session["admin"] = user.is_admin

    return RedirectResponse("/", status_code=302)

@app.post("/signup")
def post_signup_page(request: Request, fullname: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db) ):
    
    user = User(fullname=fullname, email=email, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    

    return RedirectResponse("/login", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear() 
    return RedirectResponse(url="/", status_code=302)



# Search Rooms Logic 

@app.post("/rooms/search")
def get_availabel_rooms(
    request: Request, 
    checkin: date = Form(...),
    checkout: date = Form(...),
    guests: int = Form(...),
    db: Session = Depends(get_db)
):
    current_user_id = request.session.get("user_id")
    is_admin = request.session.get("admin")

    
    booked_rooms = db.query(Booking.room_id).filter(
        and_(
            Booking.checkin_date < checkout,
            Booking.checkout_date > checkin
        )
    )

    available_rooms = db.query(Room).filter(
        Room.status == True,
        Room.max_guests >= guests,
        ~Room.id.in_(booked_rooms)
    ).all()

    if not available_rooms or checkin>=checkout:
        return templates.TemplateResponse(
            "rooms.html",
            {    "request": request,
               "user_id": current_user_id,
                "is_admin": is_admin,
                "error": "There is no room available for this period."
            }
        )

    return templates.TemplateResponse(
        "rooms.html", 
        {
            "request": request,
            "rooms": available_rooms,
            "checkin": checkin,
            "checkout": checkout,
            "guests": guests,
            "user_id": current_user_id,
            "is_admin": is_admin
        }
    )


# Booking logic 

@app.post("/bookings/book/{room_id}")
def book_room(
    request: Request,
    room_id: int,
    checkin: date = Body(...),
    checkout: date = Body(...),
    guests: int = Body(...),
    booking_price: int = Body(...),
    db: Session = Depends(get_db)
):
    excisting_booking = db.query(Booking).filter(
        room_id == Booking.room_id,
        and_(
            Booking.checkin_date < checkout,
            Booking.checkout_date > checkin
        )).first()

    current_user_id = request.session.get("user_id")
    
    if excisting_booking:
        return JSONResponse(status_code=400, content={"error": "There is already a booking for this date."})
         
    

    new_booking = Booking(
        user_id=current_user_id,
        room_id=room_id,
        checkin_date=checkin,
        checkout_date=checkout,
        guests=guests,
        total_price=booking_price
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {"success": True}


@app.post("/bookings/cancel/{booking_id}")
def cancelBooking(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.user_id != request.session.get("user_id") and not request.session.get("admin"):
        raise HTTPException(status_code=403, detail="Not your booking")

    booking.status = False

    db.commit()
    db.refresh(booking)

    return {"success": True, "message": "Booking canceled"}