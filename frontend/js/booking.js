/*
  booking.js — Connects the booking form to the Python backend
  Safari Beauty Salon

  HOW fetch() WORKS:
  fetch() is a built-in browser function that sends HTTP requests
  to a server and waits for a response — without refreshing the page.

  Think of it like a waiter:
    1. You (the browser) place an order (send a request)
    2. The waiter (fetch) takes it to the kitchen (Flask server)
    3. The kitchen prepares it (Python processes the data)
    4. The waiter brings it back (response arrives)
    5. You eat (browser shows confirmation)

  This is called AJAX — Asynchronous JavaScript And XML.
  "Asynchronous" means the page doesn't freeze while waiting.
  We use async/await to write async code that reads like normal code.
*/

// The base URL of our Python backend server
const API_URL = 'https://safari-beauty-salon-api.onrender.com/api';


// ── INITIAL STATE — hide time slots until date is selected ─────────
// When the page first loads, show a friendly prompt instead of slots.
// Slots only appear after the user picks a date.
function showDatePrompt() {
  const container = document.querySelector('.time-slots');
  if (!container) return;

  container.innerHTML = `
    <p style="
      font-size: 0.85rem;
      color: var(--color-muted);
      font-style: italic;
      padding: 0.75rem 0;
      grid-column: 1 / -1;
    ">
      Please select a date above to see available times.
    </p>
  `;
}

// Run on page load — shows the prompt instead of slots
showDatePrompt();


// ── LOAD AVAILABILITY WHEN DATE CHANGES ───────────────────────────
// When the user picks a date, we fetch which slots are already booked.
const dateInput = document.getElementById('date');

if (dateInput) {
  // Set minimum date to today so users can't book in the past
  const today = new Date().toISOString().split('T')[0];
  dateInput.setAttribute('min', today);

  // Listen for date changes — only then show time slots
  dateInput.addEventListener('change', async function () {
    const selectedDate = this.value;
    if (selectedDate) {
      await loadAvailability(selectedDate);
    } else {
      // If they clear the date, go back to the prompt
      showDatePrompt();
    }
  });
}


// ── FETCH AVAILABLE SLOTS FROM BACKEND ────────────────────────────
async function loadAvailability(date) {
  try {
    // Show a loading state while waiting for the server
    const slotsContainer = document.querySelector('.time-slots');
    if (slotsContainer) {
      slotsContainer.innerHTML = `
        <p style="
          font-size: 0.85rem;
          color: var(--color-muted);
          font-style: italic;
          padding: 0.75rem 0;
          grid-column: 1 / -1;
        ">
          Loading available times...
        </p>
      `;
    }

    // fetch() sends a GET request to our availability endpoint
    // The ?date= part is a query parameter (like a search filter)
    const response = await fetch(`${API_URL}/availability?date=${date}`);

    // response.json() reads the response body and parses it from JSON
    // into a regular JavaScript object
    const data = await response.json();

    if (data.success) {
      renderTimeSlots(data.slots);
    } else {
      console.error('Failed to load availability:', data.error);
      renderDefaultSlots();
    }

  } catch (error) {
    // This catches network errors (e.g., server is sleeping on free tier)
    console.error('Network error loading availability:', error);
    renderDefaultSlots(); // Fall back to static slots
  }
}


// ── RENDER TIME SLOTS DYNAMICALLY ─────────────────────────────────
// Builds the time slot buttons based on what the server returns
function renderTimeSlots(slots) {
  const container = document.querySelector('.time-slots');
  if (!container) return;

  // Build HTML for each slot
  container.innerHTML = slots.map(slot => {
    if (slot.available) {
      return `
        <div class="time-slot" onclick="selectTime(this, '${slot.time}')">
          ${slot.time}
        </div>
      `;
    } else {
      return `
        <div class="time-slot booked">
          ${slot.time}<br>
          <span class="time-slot__label">Booked</span>
        </div>
      `;
    }
  }).join('');
}


// ── FALLBACK: STATIC SLOTS (if server isn't running) ──────────────
// Shows all slots as available if we can't reach the backend.
// This way the form still works even if the server is waking up.
function renderDefaultSlots() {
  const container = document.querySelector('.time-slots');
  if (!container) return;

  const allSlots = [
    '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
    '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM'
  ];

  container.innerHTML = allSlots.map(slot => `
    <div class="time-slot" onclick="selectTime(this, '${slot}')">
      ${slot}
    </div>
  `).join('');
}


// ── SELECT A TIME SLOT ─────────────────────────────────────────────
// Highlights the chosen slot and stores the value in the hidden input
function selectTime(el, time) {
  if (el.classList.contains('booked')) return;
  document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('selectedTime').value = time;
}


// ── FORM SUBMISSION ────────────────────────────────────────────────
// Intercepts the form submit, collects the data,
// and sends it to our Python backend as JSON.
const bookingForm = document.getElementById('bookingForm');

if (bookingForm) {
  bookingForm.addEventListener('submit', async function (e) {
    // Prevent the default browser behavior (page reload)
    e.preventDefault();

    // ── COLLECT FORM DATA ──────────────────────────────────────
    // Build a plain JavaScript object with all the form values
    const bookingData = {
      first_name: document.getElementById('firstName').value.trim(),
      last_name:  document.getElementById('lastName').value.trim(),
      email:      document.getElementById('email').value.trim(),
      phone:      document.getElementById('phone').value.trim(),
      service:    document.getElementById('service').value,
      stylist:    document.getElementById('stylist').value,
      date:       document.getElementById('date').value,
      time:       document.getElementById('selectedTime').value,
      notes:      document.getElementById('notes').value.trim(),
    };

    // ── CLIENT-SIDE VALIDATION ─────────────────────────────────
    // Check required fields before even sending to the server
    if (!bookingData.date) {
      showMessage('Please select a date.', 'error');
      return;
    }

    if (!bookingData.time) {
      showMessage('Please select a time slot.', 'error');
      return;
    }

    // ── SEND TO BACKEND ────────────────────────────────────────
    try {
      // Disable the button to prevent double-submission
      const submitBtn = bookingForm.querySelector('.booking-submit');
      submitBtn.textContent = 'Booking...';
      submitBtn.disabled = true;

      // fetch() with method: 'POST' sends data TO the server
      // headers tell the server we're sending JSON
      // body is the actual data, converted to a JSON string
      const response = await fetch(`${API_URL}/bookings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
      });

      // Read the server's response
      const result = await response.json();

      if (result.success) {
        // Success! Show confirmation and reset the form
        showMessage(
          `✅ You're booked! Appointment confirmed for ${bookingData.date} at ${bookingData.time}.`,
          'success'
        );
        bookingForm.reset();
        document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
        // Reset button back to normal
        submitBtn.textContent = 'Confirm Appointment';
        submitBtn.disabled = false;
        // Reset time slots back to prompt after successful booking
        showDatePrompt();
      } else {
        showMessage(`❌ Error: ${result.error}`, 'error');
        submitBtn.textContent = 'Confirm Appointment';
        submitBtn.disabled = false;
      }

    } catch (error) {
      // Network error — server probably sleeping on free tier
      showMessage('❌ Could not connect to the server. Please try again in a moment.', 'error');
      const submitBtn = bookingForm.querySelector('.booking-submit');
      submitBtn.textContent = 'Confirm Appointment';
      submitBtn.disabled = false;
    }
  });
}


// ── SHOW FEEDBACK MESSAGE ──────────────────────────────────────────
// Displays a success or error message below the submit button
function showMessage(text, type) {
  // Remove any existing message first
  const existing = document.getElementById('bookingMessage');
  if (existing) existing.remove();

  const msg = document.createElement('div');
  msg.id = 'bookingMessage';
  msg.textContent = text;
  msg.style.cssText = `
    margin-top: 1rem;
    padding: 1rem 1.25rem;
    border-radius: 8px;
    font-size: 0.9rem;
    line-height: 1.5;
    background: ${type === 'success' ? '#e8f5e9' : '#fdecea'};
    color: ${type === 'success' ? '#2e7d32' : '#c62828'};
    border-left: 4px solid ${type === 'success' ? '#43a047' : '#e53935'};
  `;

  // Insert message after the submit button
  const submitBtn = bookingForm.querySelector('.booking-submit');
  submitBtn.insertAdjacentElement('afterend', msg);

  // Auto-remove success messages after 8 seconds
  if (type === 'success') {
    setTimeout(() => msg.remove(), 8000);
  }
}
