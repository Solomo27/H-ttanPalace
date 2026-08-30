from app.database import SessionLocal, engine
from app.schema import Room, User, Base

Base.metadata.create_all(bind=engine)

db = SessionLocal()

#Check if rooms already exist before adding
existing_room = db.query(Room).filter_by(room_number=101).first()

if not existing_room:
    rooms = [
        # Standard rooms
        Room(room_number=101, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/rooms/standard-bed.jpg"),
        Room(room_number=102, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/rooms/standard-bed.jpg"),
        Room(room_number=103, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/rooms/standard-bed.jpg"),
        Room(room_number=104, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/rooms/standard-bed.jpg"),

        # Deluxe rooms
        Room(room_number=201, room_class="deluxe", price_per_night=180, max_guests=4, image_url="/static/img/rooms/deluxe-bed.jpg"),
        Room(room_number=202, room_class="deluxe", price_per_night=180, max_guests=4, image_url="/static/img/rooms/deluxe-bed.jpg"),
        Room(room_number=203, room_class="deluxe", price_per_night=180, max_guests=4, image_url="/static/img/rooms/deluxe-bed.jpg"),

        # Executive rooms
        Room(room_number=301, room_class="executive", price_per_night=300, max_guests=5, image_url="/static/img/rooms/executivee-bed.jpg"),
        Room(room_number=302, room_class="executive", price_per_night=300, max_guests=5, image_url="/static/img/rooms/executivee-bed.jpg"),
    ]
    for room in rooms:
        db.add(room)
    
    db.commit() 
    print("Rooms added to database.")

#Check if admin exists before adding
existing_admin = db.query(User).filter_by(email="Evensenay04@gmail.com").first()

if not existing_admin:
    admin = User(fullname="Even Solomon", email="Evensenay04@gmail.com", password="1234", is_admin=True, reset_token=None, reset_token_expires=None)
    db.add(admin)
    
    db.commit() # Notice: No arguments here!
    print("Admin user added to database.")

db.close()