from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)

    bookings = relationship("Booking", back_populates="user")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(Integer, unique=True)
    room_class = Column(String)
    price_per_night = Column(Integer)
    max_guests = Column(Integer)
    image_url = Column(String)
    status = Column(Boolean, default=True)

    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    checkin_date = Column(Date)
    checkout_date = Column(Date)
    status = Column(Boolean, default=True)
    total_price = Column(Integer)
    guests = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")