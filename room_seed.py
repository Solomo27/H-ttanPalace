from app.database import SessionLocal
from app.schema import Room

db = SessionLocal()

rooms = [
    # Standard rooms
    Room(room_number=101, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/room/standard-bed.jpg"),
    Room(room_number=102, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/room/standard-bed.jpg"),
    Room(room_number=103, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/room/standard-bed.jpg"),
    Room(room_number=104, room_class="standard", price_per_night=120, max_guests=3, image_url="/static/img/room/standard-bed.jpg"),

    # Deluxe rooms
    Room(room_number=201, room_class="deluxe", price_per_night=180, max_guests=4, image_url="/static/img/room/deluxe-bed.jpg"),
    Room(room_number=202, room_class="deluxe", price_per_night=180, max_guests=4, image_url="/static/img/room/deluxe-bed.jpg"),
    Room(room_number=203, room_class="deluxe", price_per_night=180, max_guests=4, image_url="/static/img/room/deluxe-bed.jpg"),

    # Executive rooms
    Room(room_number=301, room_class="executive", price_per_night=300, max_guests=5, image_url="/static/img/room/executivee-bed.jpg"),
    Room(room_number=302, room_class="executive", price_per_night=300, max_guests=5, image_url="/static/img/room/executivee-bed.jpg"),
]

for room in rooms:
    db.add(room)

db.commit()
db.close()