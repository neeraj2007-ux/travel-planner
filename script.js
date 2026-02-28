// API Base URL is defined in config.js


// -------------------- Backend & Supabase --------------------
console.log('Backend URL:', API_BASE_URL);
// -------------------- Auth Token Helpers --------------------
function getAuthToken() {
    return localStorage.getItem('authToken');
}

function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

function removeAuthToken() {
    localStorage.removeItem('authToken');
}

// -------------------- DOM Loaded --------------------
window.addEventListener('DOMContentLoaded', () => {

    console.log('Backend URL:', API_BASE_URL);

    // -------------------- Trip Form Submission --------------------
    const tripForm = document.getElementById('tripForm');
    if (tripForm) {
        tripForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = {
                destination: document.getElementById('destination').value,
                budget: document.getElementById('budget').value,
                members: document.getElementById('members').value,
                days: document.getElementById('days').value,
                from: document.getElementById('from').value,
                accommodation: document.getElementById('accommodation').value,
                interests: document.getElementById('interests').value
            };

            const token = getAuthToken();
            if (!token) {
                alert('Please login to generate your trip plan!');
                openModal();
                return;
            }

            const submitBtn = document.querySelector('.generate-btn');
            submitBtn.textContent = 'Generating...';
            submitBtn.disabled = true;

            try {
                const response = await fetch(`${API_BASE_URL}/generate-trip`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                console.log('API Response:', data);

                if (data.success) displayTripPlan(data.trip);
                else alert(data.message || 'Failed to generate trip');

            } catch (error) {
                console.error(error);
                alert('An error occurred. Check console for details.');
            } finally {
                submitBtn.textContent = 'Generate Trip Plan';
                submitBtn.disabled = false;
            }
        });
    }

    // -------------------- OTP Login --------------------
    const sendOTPBtn = document.getElementById('sendOTPBtn');
    const verifyOTPBtn = document.getElementById('verifyOTPBtn');

    if (sendOTPBtn) sendOTPBtn.onclick = sendOTP;
    if (verifyOTPBtn) verifyOTPBtn.onclick = verifyOTP;

    // -------------------- OTP Auto-focus --------------------
    document.querySelectorAll('.otp-input').forEach((input, index, inputs) => {
        input.addEventListener('input', () => {
            input.value = input.value.replace(/[^0-9]/g,'');
            if (input.value.length === 1 && index < inputs.length - 1) inputs[index+1].focus();
        });
        input.addEventListener('keydown', e => {
            if (e.key === 'Backspace' && input.value === '' && index > 0) inputs[index-1].focus();
        });
    });

    // -------------------- Smooth Scroll --------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            const href = anchor.getAttribute('href');
            if (href === '#') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    // -------------------- Modal Close on Outside Click --------------------
    const authModal = document.getElementById('authModal');
    if (authModal) {
        authModal.addEventListener('click', e => {
            if (e.target === e.currentTarget) closeModal();
        });
    }

    // -------------------- Check Existing Login --------------------
    const token = getAuthToken();
    if (token) {
        fetch(`${API_BASE_URL}/health`, { headers: { 'Authorization': `Bearer ${token}` } })
            .then(res => res.ok ? updateUIForLoggedIn('User') : removeAuthToken())
            .catch(() => {});
    }
});

// -------------------- Display Trip Plan --------------------
function displayTripPlan(trip) {
    const existingPlan = document.getElementById('tripPlanResult');
    if (existingPlan) existingPlan.remove();

    const plannerCard = document.querySelector('.planner-card');
    if (!plannerCard) return;

    let planHTML = `<div id="tripPlanResult" style="background:white;padding:20px;border-radius:15px;margin-top:20px;">`;
    planHTML += `<h2 style="color:#06b6d4;">Your Trip to ${trip.destination}</h2>`;
    planHTML += `<p>Budget: ₹${trip.budget} | Days: ${trip.days} | Travelers: ${trip.members}</p>`;

    if (trip.itinerary) {
        trip.itinerary.forEach(day => {
            planHTML += `<h4>${day.title}</h4>`;
            if (day.activities) {
                planHTML += '<ul>';
                day.activities.forEach(act => planHTML += `<li>${act.name || act}</li>`);
                planHTML += '</ul>';
            }
        });
    }

    planHTML += `<button onclick="window.print()" style="margin-top:10px;">Print</button>`;
    planHTML += `<button onclick="document.getElementById('tripPlanResult').remove()" style="margin-top:10px;">Close</button>`;
    planHTML += '</div>';

    plannerCard.insertAdjacentHTML('afterend', planHTML);
    document.getElementById('tripPlanResult').scrollIntoView({ behavior: 'smooth' });
}

// -------------------- Modal & OTP Functions --------------------
function openModal() { document.getElementById('authModal').classList.add('active'); }
function closeModal() { document.getElementById('authModal').classList.remove('active'); resetModal(); }
function resetModal() {
    document.getElementById('emailStep').style.display = 'block';
    document.getElementById('otpStep').style.display = 'none';
    document.getElementById('successMessage').style.display = 'none';
    document.getElementById('loginEmail').value = '';
    clearOTPInputs();
}
function clearOTPInputs() { for(let i=1;i<=6;i++){document.getElementById('otp'+i).value='';} }

async function sendOTP() {
    const email = document.getElementById('loginEmail').value;
    if (!email) return alert('Enter email');
    try {
        const res = await fetch(`${API_BASE_URL}/send-otp`, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({email})
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById('emailStep').style.display='none';
            document.getElementById('otpStep').style.display='block';
            document.getElementById('otp1').focus();
        } else alert(data.message || 'Failed to send OTP');
    } catch(e) { console.error(e); alert('Error sending OTP'); }
}

async function verifyOTP() {
    const email = document.getElementById('loginEmail').value;
    const otp = Array.from({length:6},(_,i)=>document.getElementById('otp'+(i+1)).value).join('');
    if (otp.length!==6) return alert('Enter complete OTP');
    try {
        const res = await fetch(`${API_BASE_URL}/verify-otp`, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({email,otp})
        });
        const data = await res.json();
        if (data.success) { setAuthToken(data.token); updateUIForLoggedIn(email); setTimeout(closeModal,2000); }
        else { alert(data.message || 'Invalid OTP'); clearOTPInputs(); document.getElementById('otp1').focus(); }
    } catch(e) { console.error(e); alert('Error verifying OTP'); }
}

// -------------------- UI Updates --------------------
function updateUIForLoggedIn(email){
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.textContent = email.split('@')[0];
    loginBtn.onclick = ()=>{if(confirm('Logout?')) logout();};
}
function updateUIForLoggedOut(){
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.textContent='Login';
    loginBtn.onclick = openModal;
}
function logout(){
    removeAuthToken();
    updateUIForLoggedOut();
    alert('Logged out successfully');
}
