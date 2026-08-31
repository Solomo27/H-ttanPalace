from datetime import date, datetime, timedelta
from pathlib import Path
import secrets
from tempfile import template
from fastapi import Body, FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import os
from dotenv import load_dotenv
from app.email_service import send_booking_confirmation_email
from app.email_service import send_cancellation_confirmation_email
from app.email_service import send_password_reset_email

from app.database import SessionLocal
from app.schema import User, Room, Booking

from app.schema import Base
from app.database import engine

import stripe

env_path = Path(__file__).parent / ".env"

load_dotenv(dotenv_path=env_path)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

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
        request=request,
        name="landing.html",
        context={"request": request, 
         "user_id": current_user_id,
         "is_admin": is_admin}
    )

@app.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )

@app.get("/signup")
def get_signup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request}
    )


@app.get("/rooms")
def get_room_page(request: Request):

    current_user_id = request.session.get("user_id")
    is_admin = request.session.get("admin")

    return templates.TemplateResponse(
        request=request,
        name="rooms.html",
        context={"request": request, 
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
        request=request,
        name="bookings.html",
        context={"request": request, 
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
        request=request,
        name="admin.html",
        context={"request": request, 
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
            request=request,
            name="login.html",
            context={   
                "request": request,
                "error": "Wrong email or password!"
            }
        ) 
            
        
            
    
    request.session["user_id"] = user.id
    request.session["admin"] = user.is_admin

    return RedirectResponse("/", status_code=302)

@app.post("/signup")
def post_signup_page(request: Request, fullname: str = Form(...), email: str = Form(...), password: str = Form(...), conf_password: str = Form(...), db: Session = Depends(get_db) ):
    

    if password != conf_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={   
                "request": request,
                "error": "Wrong email or password!"
            }
        ) 

    used_email = db.query(User).filter(User.email == email).first()

    if used_email:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={   
                "request": request,
                "error": "Email already exist, try to login!"
            }
        ) 

    
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

    today = date.today()
    if not available_rooms or checkin>=checkout or today > checkin:
        return templates.TemplateResponse(
            request=request,
            name="rooms.html",
            context={    "request": request,
               "user_id": current_user_id,
                "is_admin": is_admin,
                "error": "There is no room available for this period."
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="rooms.html", 
        context={
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
       Booking.room_id == room_id,
        and_(
            Booking.checkin_date < checkout,
            Booking.checkout_date > checkin
        )).first()

    current_user_id = request.session.get("user_id")
    current_user = db.query(User).filter(User.id == current_user_id).first()
    
    if excisting_booking:
        return JSONResponse(status_code=400, content={"error": "There is already a booking for this date."})
         
    

    new_booking = Booking(
        user_id=current_user_id,
        room_id=room_id,
        checkin_date=checkin,
        checkout_date=checkout,
        guests=guests,
        total_price=booking_price,
        payment_status="pending_payment"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)


    # try:
    #     send_booking_confirmation_email(
    #         to_email=current_user.email,
    #         guest_name=current_user.fullname,
    #         room_id=room_id,
    #         checkin=checkin,
    #         checkout=checkout,
    #         guests=guests,
    #         total_price=booking_price,
    #         booking_id=new_booking.id
    #     )
    # except Exception as email_error:
    #     print("Email could not be sent:", email_error)

    checkout_session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        customer_email=current_user.email,
        line_items=[
            {
                "price_data": {
                    "currency": "sek",
                    "product_data": {
                        "name": f"Hattan Hotel Room {room_id}",
                        "description": f"Check-in: {checkin}, Check-out: {checkout}, Guests: {guests}",
                    },
                    "unit_amount": booking_price * 100,
                },
                "quantity": 1,
            }
        ],
        metadata={
            "booking_id": str(new_booking.id),
            "user_id": str(current_user.id),
        },
        success_url=f"{FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URL}/payment/cancel?booking_id={new_booking.id}",
    )

    new_booking.stripe_session_id = checkout_session.id
    db.commit()

    return {
        "success": True,
        "checkout_url": checkout_session.url
    }

@app.get("/payment/success")
def get_succesfull_payment(
    request: Request,
    session_id: str, 
    db: Session = Depends(get_db)
):
    
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    session_data = checkout_session._to_dict_recursive()

    if session_data.get("payment_status") != "paid":
        return templates.TemplateResponse(
            request=request,
            name="payment_fail.html",
            context={
                "request": request,
                "error": "Payment was not completed."
            }
        )

    booking_id = session_data.get("metadata", {}).get("booking_id")

    booking = db.query(Booking).filter(Booking.id == int(booking_id)).first()

    if not booking:
        return templates.TemplateResponse(
            request=request,
            name="payment_fail.html",
            context={
                "request": request,
                "error": "Booking not found."
            }
        )

    if booking.payment_status != "confirmed":
        booking.payment_status = "confirmed"
        db.commit()
        db.refresh(booking)

        user = db.query(User).filter(User.id == booking.user_id).first()

        try:
            send_booking_confirmation_email(
                to_email=user.email,
                guest_name=user.fullname,
                room_id=booking.room_id,
                checkin=booking.checkin_date,
                checkout=booking.checkout_date,
                guests=booking.guests,
                total_price=booking.total_price,
                booking_id=booking.id
            )
        except Exception as email_error:
            print("Confirmation email failed:", email_error)

    return RedirectResponse(url="/bookings", status_code=303)

@app.get("/payment/cancel")
def payment_cancel(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if booking and booking.status == "pending_payment":
        db.delete(booking)
        db.commit()

    return RedirectResponse(url="/bookings", status_code=303)



@app.post("/bookings/cancel/{booking_id}")
def cancelBooking(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    user = db.query(User).filter(User.id == booking.user_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    if booking.user_id != request.session.get("user_id") and not request.session.get("admin"):
        raise HTTPException(status_code=403, detail="Not your booking")

    booking.status = False
    booking.payment_status = "Canceled"

    db.commit()
    db.refresh(booking)

    try:
        send_cancellation_confirmation_email(
            to_email=user.email,
            guest_name=user.fullname,
            room_id=booking.room_id,
            checkin=booking.checkin_date,
            checkout=booking.checkout_date,
            guests=booking.guests,
            total_price=booking.total_price,
            booking_id=booking_id       
        )
    except Exception as email_error:
        print("Email could not be sent:", email_error)

    return {"success": True, "message": "Booking canceled"}


@app.get("/login/forgot-password")
def get_reset_email_conf_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="send_reset_email.html",
        context={"request": request}
    )


@app.post("/login/forgot-password")
def send_reset_email_to_user(
    request: Request,
    reset_email: str = Form(...),
    db : Session = Depends(get_db)
):
   
    user = db.query(User).filter(User.email == reset_email).first()

    if not user or (user.reset_token_expires and user.reset_token_expires > datetime.now()):
        return templates.TemplateResponse(
            request=request,
            name="send_reset_email.html",
            context={
                "request": request,
                "message": "If an account with that email exists, a reset link has been sent."
            }
        )


    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=15)

    user.reset_token = reset_token
    user.reset_token_expires = expires_at

    db.commit()
    

    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    try: 
        send_password_reset_email(
            user.email,
            user.fullname,
            reset_link
        )
    except Exception as error:
        print("Password reset email failed:", error)    

    return templates.TemplateResponse(
        request=request,
        name="send_reset_email.html",
        context={
            "request": request,
            "message": "If an account with that email exists, a reset link has been sent."
        }
    )


@app.get("/reset-password")
def get_reset_password_page(
    request: Request,
    token: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.reset_token == token).first()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "error": "Invalid or expired reset link."
            }
        )

    if not user.reset_token_expires or user.reset_token_expires < datetime.now():
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "error": "Invalid or expired reset link."
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={
            "request": request,
            "token": token
        }
    )

@app.post("/reset-password")
def reset_password(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    conf_new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.reset_token == token).first()

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "error": "Invalid or expired reset link."
            }
        )

    if not user.reset_token_expires or user.reset_token_expires < datetime.now():
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "error": "Invalid or expired reset link."
            }
        )

    if len(new_password) < 3:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "token": token,
                "error": "Password must be at least 3 characters."
            }
        )

    if new_password != conf_new_password:
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "token": token,
                    "error": "Password dont match with confirmed password."
                }
            )

    user.password = new_password

    user.reset_token = None
    user.reset_token_expires = None

    db.commit()
   

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "message": "Password reset successfully. You can now log in."
        }
    )