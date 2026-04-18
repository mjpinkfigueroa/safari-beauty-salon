/*
  booking.js — Connects the booking form to the Python backend
  Handles: date selection, time slot loading, form submission
*/

const API_URL = 'https://safari-beauty-salon-api.onrender.com/api';

function showDatePrompt() {
  const container = document.querySelector('.time-slots');
  if (!container) return;
  container.innerHTML = `
    <p style="font-size:0.85rem;color:var(--color-mid);font-style:italic;padding:0.75rem 0;grid-column:1/-1;">
      Please select a date above to see available times.
    </p>
  `;
}

showDatePrompt();

const dateInput = document.getElementById('date');
if (dateInput) {
  const today = new Date().toISOString().split('T')[0];
  dateInput.setAttribute('min', today);

  dateInput.addEventListener('change', async function () {
    if (this.value) {
      await loadAvailability(this.value);
    } else {
      showDatePrompt();
    }
  });
}

async function loadAvailability(date) {
  try {
    const container = document.querySelector('.time-slots');
    if (container) {
      container.innerHTML = `<p style="font-size:0.85rem;color:var(--color-mid);font-style:italic;padding:0.75rem 0;grid-column:1/-1;">Loading available times...</p>`;
    }
    const response = await fetch(`${API_URL}/availability?date=${date}`);
    const data = await response.json();
    if (data.success) { renderTimeSlots(data.slots); } else { renderDefaultSlots(); }
  } catch { renderDefaultSlots(); }
}

function renderTimeSlots(slots) {
  const container = document.querySelector('.time-slots');
  if (!container) return;
  container.innerHTML = slots.map(slot =>
    slot.available
      ? `<div class="time-slot" onclick="selectTime(this,'${slot.time}')">${slot.time}</div>`
      : `<div class="time-slot booked">${slot.time}<br><span class="time-slot__label">Booked</span></div>`
  ).join('');
}

function renderDefaultSlots() {
  const container = document.querySelector('.time-slots');
  if (!container) return;
  const slots = ['9:00 AM','10:00 AM','11:00 AM','12:00 PM','1:00 PM','2:00 PM','3:00 PM','4:00 PM','5:00 PM','6:00 PM'];
  container.innerHTML = slots.map(s => `<div class="time-slot" onclick="selectTime(this,'${s}')">${s}</div>`).join('');
}

function selectTime(el, time) {
  if (el.classList.contains('booked')) return;
  document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
  el.classList.add('selected');
  document.getElementById('selectedTime').value = time;
}

const bookingForm = document.getElementById('bookingForm');

if (bookingForm) {
  bookingForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const checkedServices = Array.from(document.querySelectorAll('input[name="services"]:checked')).map(cb => cb.value);

    if (checkedServices.length === 0) { showMessage('Please select at least one service.', 'error'); return; }

    const bookingData = {
      first_name: document.getElementById('firstName').value.trim(),
      last_name:  document.getElementById('lastName').value.trim(),
      email:      document.getElementById('email').value.trim(),
      phone:      document.getElementById('phone').value.trim(),
      service:    checkedServices.join(', '),
      stylist:    document.getElementById('stylist').value,
      date:       document.getElementById('date').value,
      time:       document.getElementById('selectedTime').value,
      notes:      document.getElementById('notes').value.trim(),
    };

    if (!bookingData.date) { showMessage('Please select a date.', 'error'); return; }
    if (!bookingData.time) { showMessage('Please select a time slot.', 'error'); return; }

    try {
      const submitBtn = bookingForm.querySelector('.booking-submit');
      submitBtn.textContent = 'Booking...';
      submitBtn.disabled = true;

      const response = await fetch(`${API_URL}/bookings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookingData)
      });
      const result = await response.json();

      if (result.success) {
        showMessage(`Your appointment is confirmed for ${bookingData.date} at ${bookingData.time}.`, 'success');
        bookingForm.reset();
        document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
        document.querySelectorAll('.service-check').forEach(s => s.classList.remove('checked'));
        submitBtn.textContent = 'Confirm Appointment';
        submitBtn.disabled = false;
        showDatePrompt();
      } else {
        showMessage(`Error: ${result.error}`, 'error');
        submitBtn.textContent = 'Confirm Appointment';
        submitBtn.disabled = false;
      }
    } catch {
      showMessage('Could not connect to the server. Please try again in a moment.', 'error');
      const submitBtn = bookingForm.querySelector('.booking-submit');
      submitBtn.textContent = 'Confirm Appointment';
      submitBtn.disabled = false;
    }
  });
}

function showMessage(text, type) {
  const existing = document.getElementById('bookingMessage');
  if (existing) existing.remove();
  const msg = document.createElement('div');
  msg.id = 'bookingMessage';
  msg.textContent = text;
  msg.style.cssText = `margin-top:1rem;padding:1rem 1.25rem;border-radius:8px;font-size:0.9rem;line-height:1.5;background:${type==='success'?'#f0fdf4':'#fef2f2'};color:${type==='success'?'#166534':'#991b1b'};border-left:4px solid ${type==='success'?'#16a34a':'#dc2626'};`;
  const submitBtn = bookingForm.querySelector('.booking-submit');
  submitBtn.insertAdjacentElement('afterend', msg);
  if (type === 'success') setTimeout(() => msg.remove(), 8000);
}
