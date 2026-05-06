

function switchTab(tier, btn) {
  // Update buttons
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  // Update panels
  document.querySelectorAll('.room-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('room-' + tier).classList.add('active');
}


function toggle_overlay() {
  const overlay = document.getElementById("login-overlay")
  const overlay_title = document.getElementById("overlay-title")
  const overlay_btns = document.getElementById("overlay-btns") 

  const isLoggedIn = document.body.getAttribute("data-is-logged-in") === "true" 

  overlay_btns.innerHTML = "";

  if (!isLoggedIn) {
    overlay_title.innerHTML = "Sign in to book!";

    overlay_btns.innerHTML = `
      <a href="/login"><button>Login</button></a>
      <a href="/signup"><button>Sign up</button></a>
    `;
  } else {
    overlay_title.innerHTML = "Are you sure you want to logout?"

    overlay_btns.innerHTML = `
      <a href="/logout"><button>Logout</button></a>
    `;
  }


  overlay.style.display = (overlay.style.display === "flex") ? "none" : "flex";

}

function btn_book_overlay(){
  const isLoggedIn = document.body.getAttribute("data-is-logged-in") === "true";
  if (isLoggedIn) {
        window.location.href = "/rooms";
    } else {
        toggle_overlay();
  }
}

  


async function toggle_roomStatus(button) {
  const roomId = button.getAttribute("data-room-id")
  const currentStatus = button.getAttribute('data-status')
  const isCurrentlyActive = currentStatus === "true"


  try {
    const response = await fetch(`/admin/toggle-room/${roomId}`, {
            method: 'POST'
    });
    if (response.ok) {
      const card = button.closest('.admin-room-card');
      const badge = card.querySelector('.status-badge');

      if (isCurrentlyActive) {
        // Ändra till Inactive
        button.setAttribute('data-status', 'false');
        button.textContent = "Activate";
        button.className = "toggle-room-btn btn-activate";
        
        badge.textContent = "Inactive";
        badge.className = "status-badge inactive";
      } else {
        // Ändra till Active
        button.setAttribute('data-status', 'true');
        button.textContent = "Deactivate";
        button.className = "toggle-room-btn btn-deactivate";
        
        badge.textContent = "Active";
        badge.className = "status-badge active";
      }
    } else {
      alert("Något gick fel när statusen skulle ändras i databasen.");
    }
  } catch (error) {
        console.error("Fel vid kommunikation med servern:", error);
    }

}





let currentBookingData = null

function toggle_booking_error(err_msg=""){
    const bookErrorP = document.getElementById("booking-error-msg")
    if (err_msg){
      bookErrorP.innerHTML=err_msg
      bookErrorP.style.display="block"
    } else {
      bookErrorP.style.display="none"
    }
      
}

async function openBookOverlay(roomId, roomNumber, roomClass, pricePerNight){

  const bookingOverlay = document.getElementById("booking-overlay")
  bookingOverlay.style.display = "flex"

  document.body.classList.add("no-scroll");

  const checkin_date = document.getElementById("checkin").value 
  const checkout_date = document.getElementById("checkout").value
  const guests = document.getElementById("guests").value

  const date1 = new Date(checkin_date);
  const date2 = new Date(checkout_date);
  const nights = (date2 - date1) / (1000 * 60 * 60 * 24);

  const totalPrice = nights * pricePerNight

  document.getElementById("modal-room-name").textContent = `${roomClass.toUpperCase()} (Room #${roomNumber})`;
  document.getElementById("modal-checkin").textContent = checkin_date;
  document.getElementById("modal-checkout").textContent = checkout_date;
  document.getElementById("modal-guests").textContent = guests;
  document.getElementById("modal-total-price").textContent = totalPrice;

  
  currentBookingData = {
    room_id: roomId,
    checkin: checkin_date,
    checkout: checkout_date,
    guests: guests,
    booking_price: totalPrice
  };  

  setupConfirmButton()
}

function setupConfirmButton() {
  const btn = document.getElementById("confirm-book-btn");
  if (btn) {
    btn.onclick = function() {
      if (currentBookingData) {
        sendBooking(`/bookings/book/${currentBookingData.room_id}`);
      }
    };
  }
}

async function sendBooking(path){
  try{
    const response = await fetch(path,{
      method:"POST",
      headers: {
        "Content-Type": "application/json" 
      },
      body: JSON.stringify({
        checkin:currentBookingData.checkin,
        checkout:currentBookingData.checkout,
        guests:currentBookingData.guests,
        booking_price:currentBookingData.booking_price
      })
    })

    const data = await response.json();

    if (response.ok) {
      // Om success: True, skicka användaren till bokningssidan
      window.location.href = "/bookings"; 
      closeBookingOverlay()// Eller var du nu vill skicka dem
    } else {
      // Om det var ett fel (t.ex. redan bokat), visa en popup med felet!
      toggle_booking_error(data.error) 
    }

  } catch (error){
    console.log("Fel vid kommunikation med servern:")
  }
}



function closeBookingOverlay(){
  const bookingOverlay = document.getElementById("booking-overlay")
  bookingOverlay.style.display = "none"
  document.body.classList.remove("no-scroll");
  currentBookingData = null
}


async function cancelBooking(button){

  const bookingId = button.getAttribute("data-booking-id");

  try {
      // Skicka anropet till din FastAPI backend
    const response = await fetch(`/bookings/cancel/${bookingId}`, {
        method: 'POST'
    });

    if (response.ok) {
      // -- HÄR SKER MAGIN SOM SLIPPER SIDLADDNING -- //
      
      // 1. Hitta footern där knappen och badgen ligger
      const footer = button.closest('.booking-card__footer');
      
      // 2. Hitta badgen och byt ut text och CSS-klass
      const badge = footer.querySelector('.confirm-status-badge');
      if (badge) {
          badge.textContent = "Canceled";
          badge.className = "canceled-status-badge";
      }

      // 3. Ta bort knappen helt från skärmen
      button.remove(); 
    } else {
      // Om backend kastar en HTTPException
      const errorData = await response.json();
      alert("Could not cancel: " + (errorData.detail || "Something went wrong."));
    }
    } catch (error) {
        console.error("Fetch error:", error);
        alert("A network error occurred.");
  }






}