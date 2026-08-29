# Hattan Hotel

Hattan Hotel is a fullstack hotel booking project built with FastAPI, SQLAlchemy, Jinja/HTML, CSS, JavaScript, SMTP email and Stripe test payments.

Users can register, log in, book rooms, pay through Stripe Checkout, receive booking confirmation emails, cancel bookings and reset their password by email. The project also includes an admin page where admins can manage rooms, users and bookings.

## Main Features

* User login and registration
* Room booking system
* Stripe Checkout test payment
* Booking confirmation email
* Booking cancellation email
* Forgot password / reset password by email
* My Bookings page
* Admin page for managing rooms and bookings

## Stripe Test Payment

This project uses Stripe in test mode. No real money is charged.

To test a successful payment, use:

```text
Card number: 4242 4242 4242 4242
Expiry date: Any future date
CVC: Any 3 digits
Postal code: Any value
```

After a successful payment, the booking is confirmed, the user is redirected to My Bookings, and a confirmation email is sent.

To test a cancelled payment, start a booking and go to Stripe Checkout, then press back/cancel instead of paying. The booking will not be confirmed.

## Note

This project was created for educational purposes to demonstrate a complete hotel booking flow with authentication, database handling, email functionality, admin tools and Stripe test payments.



