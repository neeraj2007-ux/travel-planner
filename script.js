// -------------------- Helpers --------------------
function getAuthToken() { return localStorage.getItem('authToken'); }
function setAuthToken(token) { localStorage.setItem('authToken', token); }
function removeAuthToken() { localStorage.removeItem('authToken'); }

// -------------------- Event Listeners --------------------
window.addEventListener('DOMContentLoaded', () => {
    
    // Check Login Status
    const token = getAuthToken();
    if(token) updateUIForLoggedIn('User');

    // Handle Form Submit
    const tripForm = document.getElementById('tripForm');
    if (tripForm) {
        tripForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!getAuthToken()) { alert('Please login first!'); openModal(); return; }

            const submitBtn = document.querySelector('.generate-btn');
            submitBtn.textContent = 'Generating Plan... (Takes ~10s)';
            submitBtn.disabled = true;

            const formData = {
                destination: document.getElementById('destination').value,
                budget: document.getElementById('budget').value,
                members: document.getElementById('members').value,
                days: document.getElementById('days').value,
                from: document.getElementById('from').value,
                accommodation: document.getElementById('accommodation').value,
                interests: document.getElementById('interests').value
            };

            try {
                const res = await fetch(`${window.API_BASE_URL}/api/generate-trip`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json', 
                        'Authorization': `Bearer ${getAuthToken()}` 
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await res.json();
                if(data.success) {
                    displayTripPlan(data.trip);
                } else {
                    alert(data.message || 'Error generating trip');
                }
            } catch(e) {
                console.error(e);
                alert('Connection error. Is backend running?');
            } finally {
                submitBtn.textContent = 'Generate Trip Plan';
                submitBtn.disabled = false;
            }
        });
    }

    // OTP Inputs
    document.querySelectorAll('.otp-input').forEach((input, idx, inputs) => {
        input.addEventListener('input', () => {
            if(input.value.length === 1 && idx < inputs.length - 1) inputs[idx+1].focus();
        });
    });
});

// -------------------- Core Functions --------------------

function displayTripPlan(trip) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = ''; // Clear previous

    let html = `
        <div class="trip-result-card" style="background:white; padding:2rem; border-radius:15px; margin-top:2rem; box-shadow:0 5px 20px rgba(0,0,0,0.1);">
            <h2 style="color:#06b6d4;">Trip to ${trip.destination}</h2>
            <div style="margin-bottom:1rem; padding:1rem; background:#f0f9ff; border-radius:10px;">
                <strong>Budget:</strong> ₹${trip.budget} | <strong>Travelers:</strong> ${trip.members} | <strong>Days:</strong> ${trip.days}
            </div>
            <h3>Itinerary</h3>
            <div class="timeline">
    `;

    if(trip.itinerary && Array.isArray(trip.itinerary)) {
        trip.itinerary.forEach(day => {
            html += `
                <div class="day-plan" style="margin-bottom:1.5rem;">
                    <h4 style="color:#333; border-bottom:2px solid #06b6d4; display:inline-block;">Day ${day.day}: ${day.title || ''}</h4>
                    <ul style="list-style:none; padding-left:0; margin-top:10px;">
            `;
            
            if(day.activities) {
                day.activities.forEach(act => {
                    // FIXED: Handle various JSON keys the AI might return
                    const name = act.activity || act.name || act.description;
                    const time = act.time ? `<span style="color:#666; font-size:0.9em;">${act.time}</span> - ` : '';
                    const cost = act.cost ? ` <span style="color:#059669; font-weight:bold;">(₹${act.cost})</span>` : '';
                    
                    html += `<li style="margin-bottom:8px; padding-left:15px; border-left:3px solid #e0e0e0;">
                        ${time}<strong>${name}</strong>${cost}
                        <div style="font-size:0.9em; color:#666;">${act.tips || act.description || ''}</div>
                    </li>`;
                });
            }
            html += `</ul></div>`;
        });
    } else {
        html += `<p>No itinerary details available.</p>`;
    }

    html += `
        <button onclick="window.print()" class="generate-btn" style="width:auto; margin-top:1rem;">Print / Save PDF</button>
        </div>
    `;

    resultsDiv.innerHTML = html;
    resultsDiv.scrollIntoView({behavior: 'smooth'});
}

// FIXED: Missing function implemented
async function fetchPastTrips() {
    if (!getAuthToken()) { alert('Login required'); openModal(); return; }
    
    try {
        const res = await fetch(`${window.API_BASE_URL}/api/my-trips`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        const data = await res.json();
        
        if(data.success) {
            const resultsDiv = document.getElementById('results');
            if(data.trips.length === 0) {
                alert('No past trips found.');
                return;
            }
            
            let html = `<h2 style="margin-top:2rem;">My Past Trips</h2><div style="display:grid; gap:1rem; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr));">`;
            data.trips.forEach(t => {
                html += `
                    <div style="background:white; padding:1.5rem; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
                        <h3 style="color:#06b6d4;">${t.destination}</h3>
                        <p>₹${t.budget} for ${t.days} days</p>
                        <button onclick='displayTripPlan(${JSON.stringify(t)})' style="background:#06b6d4; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer; margin-top:10px;">View Plan</button>
                    </div>
                `;
            });
            html += `</div>`;
            resultsDiv.innerHTML = html;
            resultsDiv.scrollIntoView({behavior:'smooth'});
        }
    } catch(e) {
        console.error(e);
        alert('Failed to fetch history');
    }
}

// FIXED: Missing function implemented
function showPopularTrip(location) {
    document.getElementById('destination').value = location.charAt(0).toUpperCase() + location.slice(1);
    document.getElementById('budget').value = 15000;
    document.getElementById('members').value = 4;
    document.getElementById('days').value = 5;
    document.getElementById('from').value = 'Delhi'; // Default
    document.getElementById('planner').scrollIntoView({behavior:'smooth'});
}

// -------------------- Auth Logic --------------------

function openModal() { document.getElementById('authModal').classList.add('active'); }
function closeModal() { document.getElementById('authModal').classList.remove('active'); }

async function sendOTP() {
    const email = document.getElementById('loginEmail').value;
    if(!email) return alert('Email required');
    
    document.getElementById('sendOTPBtn').innerText = 'Sending...';
    
    try {
        const res = await fetch(`${window.API_BASE_URL}/api/send-otp`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email})
        });
        const data = await res.json();
        if(data.success) {
            document.getElementById('emailStep').style.display = 'none';
            document.getElementById('otpStep').style.display = 'block';
        } else {
            alert(data.message);
        }
    } catch(e) { alert('Error sending OTP'); }
    finally { document.getElementById('sendOTPBtn').innerText = 'Send OTP'; }
}

async function verifyOTP() {
    const email = document.getElementById('loginEmail').value;
    const otp = Array.from(document.querySelectorAll('.otp-input')).map(i => i.value).join('');
    
    try {
        const res = await fetch(`${window.API_BASE_URL}/api/verify-otp`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, otp})
        });
        const data = await res.json();
        if(data.success) {
            setAuthToken(data.token);
            updateUIForLoggedIn(email);
            closeModal();
            alert('Login Successful!');
        } else {
            alert('Invalid OTP');
        }
    } catch(e) { alert('Verify failed'); }
}

function updateUIForLoggedIn(email) {
    const btn = document.querySelector('.login-btn');
    btn.textContent = 'Logout (' + email.split('@')[0] + ')';
    btn.onclick = (e) => {
        e.preventDefault();
        if(confirm('Logout?')) {
            removeAuthToken();
            window.location.reload();
        }
    };
}