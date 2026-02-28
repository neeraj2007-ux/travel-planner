// Auth Helpers
function getAuthToken() { return localStorage.getItem('authToken'); }
function setAuthToken(token) { localStorage.setItem('authToken', token); }
function removeAuthToken() { localStorage.removeItem('authToken'); }

document.addEventListener('DOMContentLoaded', () => {
    if(getAuthToken()) updateUIForLoggedIn();

    // Form Submit
    const form = document.getElementById('tripForm');
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if(!getAuthToken()) { openModal(); return; }
            
            const btn = document.querySelector('.generate-btn');
            btn.textContent = 'Planning...';
            btn.disabled = true;
            
            const data = {
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
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getAuthToken()}` },
                    body: JSON.stringify(data)
                });
                const resData = await res.json();
                if(resData.success) displayTripPlan(resData.trip);
                else alert('Error: ' + resData.message);
            } catch(err) { console.error(err); alert('Server Error'); }
            finally { btn.textContent = 'Generate Trip Plan'; btn.disabled = false; }
        });
    }
    
    // OTP Auto-Focus
    document.querySelectorAll('.otp-input').forEach((input, idx, inputs) => {
        input.addEventListener('input', () => {
            if(input.value.length === 1 && idx < inputs.length - 1) inputs[idx+1].focus();
        });
    });
});

// --- Core Functions ---

function displayTripPlan(trip) {
    const div = document.getElementById('results');
    let html = `
        <div class="planner-card" style="margin-top: 20px;">
            <h2 style="color:#06b6d4">Trip to ${trip.destination}</h2>
            <p><strong>Budget:</strong> ₹${trip.budget} | <strong>Days:</strong> ${trip.days}</p>
            <div class="timeline">
    `;
    
    if(trip.itinerary) {
        trip.itinerary.forEach(day => {
            html += `<div style="margin-bottom:15px"><h4>Day ${day.day}: ${day.title || ''}</h4><ul>`;
            if(day.activities) {
                day.activities.forEach(act => {
                    // Logic fix for AI variable names
                    const name = act.activity || act.name;
                    const cost = act.cost ? ` (₹${act.cost})` : '';
                    html += `<li>${act.time ? act.time + ' - ' : ''}<strong>${name}</strong>${cost}</li>`;
                });
            }
            html += `</ul></div>`;
        });
    }
    html += `<button onclick="window.print()" style="margin-top:10px; padding:5px 15px;">Print Plan</button></div>`;
    div.innerHTML = html;
    div.scrollIntoView({behavior: 'smooth'});
}

async function fetchPastTrips() {
    if(!getAuthToken()) { openModal(); return; }
    try {
        const res = await fetch(`${window.API_BASE_URL}/api/my-trips`, {
            headers: { 'Authorization': `Bearer ${getAuthToken()}` }
        });
        const data = await res.json();
        if(data.success && data.trips.length > 0) {
            let html = '<div class="planner-card" style="margin-top:20px"><h3>My Past Trips</h3><ul>';
            data.trips.forEach(t => {
                html += `<li style="margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;">
                    <strong>${t.destination}</strong> (₹${t.budget}) - ${t.days} Days
                    <button onclick='displayTripPlan(${JSON.stringify(t)})' style="float:right; font-size:12px;">View</button>
                </li>`;
            });
            html += '</ul></div>';
            document.getElementById('results').innerHTML = html;
            document.getElementById('results').scrollIntoView({behavior:'smooth'});
        } else {
            alert('No past trips found.');
        }
    } catch(e) { alert('Failed to fetch trips'); }
}

function showPopularTrip(loc) {
    document.getElementById('destination').value = loc.charAt(0).toUpperCase() + loc.slice(1);
    document.getElementById('budget').value = 15000;
    document.getElementById('members').value = 4;
    document.getElementById('days').value = 5;
    document.getElementById('from').value = 'New Delhi'; // Default
    document.getElementById('planner').scrollIntoView({behavior:'smooth'});
}

// --- Auth Functions ---

function openModal() { document.getElementById('authModal').classList.add('active'); }
function closeModal() { document.getElementById('authModal').classList.remove('active'); }

async function sendOTP() {
    const email = document.getElementById('loginEmail').value;
    if(!email) return alert('Enter Email');
    
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
        } else { alert(data.message); }
    } catch(e) { alert('Error sending OTP'); }
    finally { document.getElementById('sendOTPBtn').innerText = 'Send OTP'; }
}

async function verifyOTP() {
    const email = document.getElementById('loginEmail').value;
    const otp = Array.from(document.querySelectorAll('.otp-input')).map(i=>i.value).join('');
    
    try {
        const res = await fetch(`${window.API_BASE_URL}/api/verify-otp`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, otp})
        });
        const data = await res.json();
        if(data.success) {
            setAuthToken(data.token);
            updateUIForLoggedIn();
            closeModal();
        } else { alert(data.message); }
    } catch(e) { alert('Verification Error'); }
}

function updateUIForLoggedIn() {
    const btn = document.querySelector('.login-btn');
    btn.textContent = 'Logout';
    btn.onclick = (e) => { 
        e.preventDefault(); 
        if(confirm('Logout?')) { removeAuthToken(); window.location.reload(); }
    };
}