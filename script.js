
// -------------------- Backend & Global Config --------------------
console.log('Backend URL:', window.API_BASE_URL);

// -------------------- Auth Token Helpers --------------------
function getAuthToken() { return localStorage.getItem('authToken'); }
function setAuthToken(token) { localStorage.setItem('authToken', token); }
function removeAuthToken() { localStorage.removeItem('authToken'); }

// -------------------- DOM Loaded --------------------
window.addEventListener('DOMContentLoaded', () => {

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
            if (!token) { alert('Please login!'); openModal(); return; }

            const submitBtn = document.querySelector('.generate-btn');
            submitBtn.textContent = 'Generating...';
            submitBtn.disabled = true;

            try {
                const res = await fetch(`${window.API_BASE_URL}/api/generate-trip`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json', 
                        'Authorization': `Bearer ${token}` 
                    },
                    body: JSON.stringify(formData)
                });

                const text = await res.text();
                let data;
                try { data = JSON.parse(text); } 
                catch(e){ console.error('Invalid JSON:', text); alert(`Server error: ${res.status}`); return; }

                if(res.status === 405){ alert('Method Not Allowed on backend'); return; }
                if(data.success) displayTripPlan(data.trip); 
                else alert(data.message || 'Failed to generate trip');

            } catch(e){ console.error(e); alert('Network or server error'); }
            finally { submitBtn.textContent = 'Generate Trip Plan'; submitBtn.disabled = false; }
        });
    }

    // -------------------- OTP Login --------------------
    const sendOTPBtn = document.getElementById('sendOTPBtn');
    const verifyOTPBtn = document.getElementById('verifyOTPBtn');
    if(sendOTPBtn) sendOTPBtn.onclick = sendOTP;
    if(verifyOTPBtn) verifyOTPBtn.onclick = verifyOTP;

    // -------------------- OTP Auto-focus --------------------
    document.querySelectorAll('.otp-input').forEach((input, index, inputs)=>{
        input.addEventListener('input', ()=>{
            input.value = input.value.replace(/[^0-9]/g,'');
            if(input.value.length===1 && index<inputs.length-1) inputs[index+1].focus();
        });
        input.addEventListener('keydown', e=>{
            if(e.key==='Backspace' && input.value==='' && index>0) inputs[index-1].focus();
        });
    });

    // -------------------- Smooth Scroll --------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor=>{
        anchor.addEventListener('click', e=>{
            const href = anchor.getAttribute('href');
            if(href==='#') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if(target) target.scrollIntoView({behavior:'smooth', block:'start'});
        });
    });

    // -------------------- Modal Close on Outside Click --------------------
    const authModal = document.getElementById('authModal');
    if(authModal) authModal.addEventListener('click', e=>{ if(e.target===e.currentTarget) closeModal(); });

    // -------------------- Check Existing Login --------------------
    const token = getAuthToken();
    if(token){
        fetch(`${window.API_BASE_URL}/api/health`, { headers:{'Authorization':`Bearer ${token}`} })
            .then(res=> res.ok ? updateUIForLoggedIn('User') : removeAuthToken())
            .catch(()=>{});
    }
});

// -------------------- Display Trip Plan --------------------
function displayTripPlan(trip){
    const existing = document.getElementById('tripPlanResult'); if(existing) existing.remove();
    const card = document.querySelector('.planner-card'); if(!card) return;
    let html = `<div id="tripPlanResult" style="background:white;padding:20px;border-radius:15px;margin-top:20px;">`;
    html += `<h2 style="color:#06b6d4;">Your Trip to ${trip.destination}</h2>`;
    html += `<p>Budget: ₹${trip.budget} | Days: ${trip.days} | Travelers: ${trip.members}</p>`;
    if(trip.itinerary) trip.itinerary.forEach(day=>{
        html += `<h4>${day.title}</h4>`;
        if(day.activities){ html+='<ul>'; day.activities.forEach(a=>html+=`<li>${a.name||a}</li>`); html+='</ul>'; }
    });
    html += `<button onclick="window.print()" style="margin-top:10px;">Print</button>`;
    html += `<button onclick="document.getElementById('tripPlanResult').remove()" style="margin-top:10px;">Close</button>`;
    html += `</div>`;
    card.insertAdjacentHTML('afterend', html);
    document.getElementById('tripPlanResult').scrollIntoView({behavior:'smooth'});
}

// -------------------- Modal & OTP --------------------
function openModal(){ document.getElementById('authModal').classList.add('active'); }
function closeModal(){ document.getElementById('authModal').classList.remove('active'); resetModal(); }
function resetModal(){
    document.getElementById('emailStep').style.display='block';
    document.getElementById('otpStep').style.display='none';
    document.getElementById('successMessage').style.display='none';
    document.getElementById('loginEmail').value='';
    clearOTPInputs();
}
function clearOTPInputs(){ for(let i=1;i<=6;i++) document.getElementById('otp'+i).value=''; }

async function sendOTP(){
    const email = document.getElementById('loginEmail').value; if(!email) return alert('Enter email');
    try{
        const res = await fetch(`${window.API_BASE_URL}/api/send-otp`, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({email})
        });
        const text = await res.text();
        let data; try{ data=JSON.parse(text); } catch(e){ console.error('Invalid JSON', text); alert(`Server error: ${res.status}`); return; }
        if(res.status===405){ alert('Method Not Allowed on backend'); return; }
        if(data.success){ document.getElementById('emailStep').style.display='none'; document.getElementById('otpStep').style.display='block'; document.getElementById('otp1').focus(); }
        else alert(data.message||'Failed to send OTP');
    } catch(e){ console.error('Error sending OTP', e); alert('Network/server error'); }
}

async function verifyOTP(){
    const email = document.getElementById('loginEmail').value;
    const otp = Array.from({length:6},(_,i)=>document.getElementById('otp'+(i+1)).value).join('');
    if(otp.length!==6) return alert('Enter complete OTP');
    try{
        const res = await fetch(`${window.API_BASE_URL}/api/verify-otp`, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({email,otp})
        });
        const text = await res.text();
        let data; try{ data=JSON.parse(text); } catch(e){ console.error('Invalid JSON', text); alert(`Server error: ${res.status}`); return; }
        if(res.status===405){ alert('Method Not Allowed on backend'); return; }
        if(data.success){ setAuthToken(data.token); updateUIForLoggedIn(email); setTimeout(closeModal,2000); }
        else { alert(data.message||'Invalid OTP'); clearOTPInputs(); document.getElementById('otp1').focus(); }
    } catch(e){ console.error('Error verifying OTP', e); alert('Network/server error'); }
}

// -------------------- UI Updates --------------------
function updateUIForLoggedIn(email){
    const btn = document.querySelector('.login-btn');
    btn.textContent = email.split('@')[0];
    btn.onclick = ()=>{ if(confirm('Logout?')) logout(); };
}
function updateUIForLoggedOut(){
    const btn = document.querySelector('.login-btn');
    btn.textContent='Login'; btn.onclick=openModal;
}
function logout(){ removeAuthToken(); updateUIForLoggedOut(); alert('Logged out successfully'); }
