import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


def _send_email(to_email: str, subject: str, html_content: str):
    """
    Sends email using SendGrid API instead of Gmail SMTP.
    This works better on Render Free because it uses HTTPS/API, not SMTP ports.
    """

    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("EMAIL_FROM_EMAIL", "hattanpalace@gmail.com")
    from_name = os.getenv("EMAIL_FROM_NAME", "Hattan Palace")

    if not sendgrid_api_key:
        raise Exception("SENDGRID_API_KEY is missing from environment variables.")

    message = Mail(
        from_email=Email(from_email, from_name),
        to_emails=To(to_email),
        subject=subject,
        html_content=Content("text/html", html_content)
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)

        print("SendGrid email sent")
        print("Status code:", response.status_code)

        return response

    except Exception as error:
        print("SendGrid email failed:", error)
        raise error


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
    html = f"""
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

            <p>Thank you for booking with us.</p>

            <p>Best regards,<br>Hattan Palace Team</p>
        </body>
    </html>
    """

    return _send_email(
        to_email=to_email,
        subject=f"Hattan Palace booking #{booking_id} confirmed",
        html_content=html
    )


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
    html = f"""
    <html>
        <body>
            <h2>Cancellation Confirmation</h2>

            <p>Hello {guest_name},</p>

            <p>Your booking has been cancelled.</p>

            <ul>
                <li><strong>Booking ID:</strong> {booking_id}</li>
                <li><strong>Room ID:</strong> {room_id}</li>
                <li><strong>Check-in:</strong> {checkin}</li>
                <li><strong>Check-out:</strong> {checkout}</li>
                <li><strong>Guests:</strong> {guests}</li>
                <li><strong>Total price:</strong> {total_price} SEK</li>
            </ul>

            <p>If this was a mistake, you can make a new booking.</p>

            <p>Best regards,<br>Hattan Palace Team</p>
        </body>
    </html>
    """

    return _send_email(
        to_email=to_email,
        subject=f"Hattan Palace booking #{booking_id} cancelled",
        html_content=html
    )


def send_password_reset_email(
    to_email: str,
    guest_name: str,
    reset_link: str,
):
    html = f"""
    <html>
        <body>
            <h2>Password Reset</h2>

            <p>Hello {guest_name},</p>

            <p>We received a request to reset your password.</p>

            <p>
                <a href="{reset_link}">Click here to reset your password</a>
            </p>

            <p>If the link does not work, copy and paste this URL into your browser:</p>

            <p>{reset_link}</p>

            <p>This link expires in 15 minutes.</p>

            <p>If you did not request this, you can ignore this email.</p>

            <p>Best regards,<br>Hattan Palace Team</p>
        </body>
    </html>
    """

    return _send_email(
        to_email=to_email,
        subject="Reset your Hattan Palace password",
        html_content=html
    )