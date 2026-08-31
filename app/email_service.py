import os
import smtplib
from email.message import EmailMessage


def send_booking_confirmation_email(
    to_email: str,
    guest_name: str,
    room_id: int,
    checkin,
    checkout,
    guests: int,
    total_price: int,
    booking_id: int
):
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_username or not email_password:
        raise Exception("Email username or password is missing from environment variables.")

    msg = EmailMessage()
    msg["Subject"] = "Booking Confirmation"
    msg["From"] = email_username
    msg["To"] = to_email

    msg.add_alternative(f"""
        <html>
            <body>
                <h2>Booking Confirmation</h2>
                <p>Hello {guest_name},</p>

                <p>Your booking has been confirmed.</p>

                <ul>
                <li><strong>Booking ID:</strong> {booking_id}</li>
                <li><strong>Room ID:</strong> {room_id}</li>
                <li><strong>Check-in:</strong> {checkin}</li>
                <li><strong>Check-out:</strong> {checkout}</li>
                <li><strong>Guests:</strong> {guests}</li>
                <li><strong>Total price:</strong> {total_price} SEK</li>
                </ul>
                
                <p></p>
                <p>Thank you for booking with us.</p>
                <p>Best regards,<br>Hattan Hotel Team</p>
            </body>
        </html>
    """, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_username, email_password)
        smtp.send_message(msg)



def send_cancellation_confirmation_email(
    to_email: str,
    guest_name: str,
    room_id: int,
    checkin,
    checkout,
    guests: int,
    total_price: int,
    booking_id: int
):
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_username or not email_password:
        raise Exception("Email username or password is missing from environment variables.")

    msg = EmailMessage()
    msg["Subject"] = "Booking Cancellation"
    msg["From"] = email_username
    msg["To"] = to_email

    msg.add_alternative(f"""
        <html>
            <body>
                <h2>Cancellation Confirmation</h2>
                <p>Hello {guest_name},</p>

                <p>Your booking has been cancled.</p>

                <ul>
                <li><strong>Booking ID:</strong> {booking_id}</li>
                <li><strong>Room ID:</strong> {room_id}</li>
                <li><strong>Check-in:</strong> {checkin}</li>
                <li><strong>Check-out:</strong> {checkout}</li>
                <li><strong>Guests:</strong> {guests}</li>
                <li><strong>Total price:</strong> {total_price} SEK</li>
                </ul>
                
                <p></p>
                <p>Thank you for booking with us.</p>
                <p>Best regards,<br>Hattan Hotel Team</p>
            </body>
        </html>
    """, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_username, email_password)
        smtp.send_message(msg)



def send_password_reset_email(
    to_email: str,
    guest_name: str,
    reset_link: str,
):
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_username or not email_password:
        raise Exception("Email username or password is missing from environment variables.")

    msg = EmailMessage()
    msg["Subject"] = "Password Reset"
    msg["From"] = email_username
    msg["To"] = to_email

    msg.add_alternative(f"""
        <html>
            <body>
                <h2>Passowrd Reset</h2>
                <p>Hello {guest_name},</p>

                <p>Your email has been confirmed.</p>
                <p>Follow this link to reset your password:</p>

                <p>Reset link: {reset_link}</p>
                <p>Expires in 15 minutes.</p>
                
                <p>Best regards,<br>Hattan Hotel Team</p>
            </body>
        </html>
    """, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email_username, email_password)
            smtp.send_message(msg)