import json
import logging
import os
from html import escape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)
BREVO_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"
EMAIL_TIMEOUT_SECONDS = 15


class EmailDeliveryError(RuntimeError):
    """An email request failed or its acceptance could not be confirmed."""


def _send_email(to_email: str, subject: str, html_content: str) -> dict:
    """Submit one transactional email to Brevo over HTTPS.

    Returns Brevo's message ID after acceptance. Actual delivery is tracked in
    Brevo's transactional logs. Calls are not retried automatically because an
    interrupted response can leave delivery uncertain.
    """
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    from_email = os.getenv("EMAIL_FROM_EMAIL", "").strip()
    from_name = os.getenv("EMAIL_FROM_NAME", "Hattan Palace").strip() or "Hattan Palace"
    recipient = to_email.strip()

    if not api_key:
        raise EmailDeliveryError("BREVO_API_KEY is missing from environment variables.")
    if not api_key.isascii() or any(character.isspace() for character in api_key):
        raise EmailDeliveryError("BREVO_API_KEY must be a single line without whitespace.")
    if not from_email:
        raise EmailDeliveryError("EMAIL_FROM_EMAIL must match a verified sender in Brevo.")
    if not recipient:
        raise EmailDeliveryError("A recipient email address is required.")

    payload = {
        "sender": {"email": from_email, "name": from_name},
        "to": [{"email": recipient}],
        "subject": subject,
        "htmlContent": html_content,
    }
    request = Request(
        BREVO_EMAIL_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=EMAIL_TIMEOUT_SECONDS) as response:
            status = response.status
            body = response.read()
    except HTTPError as error:
        status = error.code
        error.close()
        # Do not log the API key, request payload, recipient, or reset links.
        logger.error("Brevo email request rejected: status=%s", status)
        reason = {
            400: "Check the email fields and verified sender in Brevo.",
            401: "Brevo rejected BREVO_API_KEY. Check that the key is active.",
            402: "Check the Brevo account's sending allowance and status.",
            403: "Check Brevo's Transactional email permission, sender, and sending activation.",
            429: "Brevo's sending rate limit was reached. Try again later.",
        }.get(status, "Brevo could not accept the email request.")
        raise EmailDeliveryError(f"{reason} (HTTP {status}).") from None
    except (URLError, TimeoutError) as error:
        logger.error("Brevo email request interrupted: type=%s", type(error).__name__)
        raise EmailDeliveryError(
            "Could not confirm Brevo accepted the email. Check its transactional logs before retrying."
        ) from None

    if status != 201:
        logger.error("Brevo email request returned an unexpected status: status=%s", status)
        raise EmailDeliveryError(f"Brevo returned an unexpected response (HTTP {status}).")
    try:
        result = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.error("Brevo email response could not be read.")
        raise EmailDeliveryError("Brevo's email acceptance could not be verified.") from None
    if not isinstance(result, dict) or not isinstance(result.get("messageId"), str) or not result["messageId"]:
        logger.error("Brevo email response did not include a message ID.")
        raise EmailDeliveryError("Brevo's email response did not include a message ID.")

    logger.info("Brevo accepted email: message_id=%s", result["messageId"])
    return result


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
    guest_name = escape(guest_name)
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
    guest_name = escape(guest_name)
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
    guest_name = escape(guest_name)
    reset_link = escape(reset_link, quote=True)
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
