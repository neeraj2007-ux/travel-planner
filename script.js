// API Base URL is defined in config.js

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

// -------------------- Trip Form Submission --------------------
document.getElementById('tripForm').addEventListener('submit', async function(e) {
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
        console.log('API Response:', data); // Debug

        if (data.success) {
            console.log('Trip data:', data.trip); // Debug
            displayTripPlan(data.trip);
        } else {
            if (response.status === 401) {
                alert('Session expired. Please login again.');
                removeAuthToken();
                updateUIForLoggedOut();
                openModal();
            } else {
                alert(data.message || 'Failed to generate trip');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Check console for details.');
    } finally {
        submitBtn.textContent = 'Generate Trip Plan';
        submitBtn.disabled = false;
    }
});

// -------------------- Display Trip Plan --------------------
function displayTripPlan(trip) {
    console.log('Displaying trip:', trip); // Debug
    
    // Remove any existing trip plan
    const existingPlan = document.getElementById('tripPlanResult');
    if (existingPlan) existingPlan.remove();

    let planHTML = `
        <div id="tripPlanResult" style="background: white; padding: 30px; border-radius: 15px; margin-top: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #06b6d4; margin-bottom: 20px;">🎉 Your Trip Plan to ${trip.destination}</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px;">
                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px;">
                    <strong style="color: #06b6d4;">Total Budget:</strong><br>
                    ₹${trip.budget.toLocaleString()}
                </div>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px;">
                    <strong style="color: #06b6d4;">Per Person:</strong><br>
                    ₹${trip.per_person_budget.toLocaleString()}
                </div>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px;">
                    <strong style="color: #06b6d4;">Duration:</strong><br>
                    ${trip.days} days
                </div>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 10px;">
                    <strong style="color: #06b6d4;">Travelers:</strong><br>
                    ${trip.members} person(s)
                </div>
            </div>

            <h3 style="color: #333; margin-bottom: 15px;">💰 Budget Breakdown:</h3>
            <div style="display: grid; gap: 10px; margin-bottom: 30px;">
                <div style="background: linear-gradient(90deg, #06b6d4 0%, #06b6d4 ${(trip.budget_breakdown.transportation/trip.budget*100)}%, #f5f5f5 ${(trip.budget_breakdown.transportation/trip.budget*100)}%); padding: 12px; border-radius: 8px;">
                    <strong>🚗 Transportation:</strong> ₹${trip.budget_breakdown.transportation.toLocaleString()}
                </div>
                <div style="background: linear-gradient(90deg, #3b82f6 0%, #3b82f6 ${(trip.budget_breakdown.accommodation/trip.budget*100)}%, #f5f5f5 ${(trip.budget_breakdown.accommodation/trip.budget*100)}%); padding: 12px; border-radius: 8px;">
                    <strong>🏨 Accommodation:</strong> ₹${trip.budget_breakdown.accommodation.toLocaleString()}
                </div>
                <div style="background: linear-gradient(90deg, #06b6d4 0%, #06b6d4 ${(trip.budget_breakdown.food/trip.budget*100)}%, #f5f5f5 ${(trip.budget_breakdown.food/trip.budget*100)}%); padding: 12px; border-radius: 8px;">
                    <strong>🍽️ Food:</strong> ₹${trip.budget_breakdown.food.toLocaleString()}
                </div>
                <div style="background: linear-gradient(90deg, #3b82f6 0%, #3b82f6 ${(trip.budget_breakdown.activities/trip.budget*100)}%, #f5f5f5 ${(trip.budget_breakdown.activities/trip.budget*100)}%); padding: 12px; border-radius: 8px;">
                    <strong>🎭 Activities:</strong> ₹${trip.budget_breakdown.activities.toLocaleString()}
                </div>
                <div style="background: linear-gradient(90deg, #06b6d4 0%, #06b6d4 ${(trip.budget_breakdown.miscellaneous/trip.budget*100)}%, #f5f5f5 ${(trip.budget_breakdown.miscellaneous/trip.budget*100)}%); padding: 12px; border-radius: 8px;">
                    <strong>💼 Miscellaneous:</strong> ₹${trip.budget_breakdown.miscellaneous.toLocaleString()}
                </div>
            </div>

            <h3 style="color: #333; margin-bottom: 15px;">📅 Day-wise Itinerary:</h3>
            ${trip.itinerary.map(day => {
                console.log('Day:', day); // Debug each day
                
                let activitiesHTML = '';
                
                if (day.activities && Array.isArray(day.activities)) {
                    if (typeof day.activities[0] === 'string') {
                        // Old format: array of strings
                        activitiesHTML = `
                            <ul style="margin-left: 20px; line-height: 1.8;">
                                ${day.activities.map(activity => `<li>${activity}</li>`).join('')}
                            </ul>
                        `;
                    } else {
                        // New AI format: array of objects
                        activitiesHTML = day.activities.map(activity => `
                            <div style="margin: 10px 0; padding: 12px; background: white; border-radius: 6px; border-left: 3px solid #06b6d4;">
                                <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 10px;">
                                    <div style="flex: 1; min-width: 200px;">
                                        <strong style="color: #06b6d4;">${activity.time || ''}</strong> ${activity.activity || activity.name || 'Activity'}
                                        ${activity.location ? `<br><small style="color: #666;">📍 ${activity.location}</small>` : ''}
                                    </div>
                                    ${activity.cost ? `<div style="background: #06b6d4; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; white-space: nowrap;">₹${activity.cost}</div>` : ''}
                                </div>
                                ${activity.description ? `<p style="margin: 8px 0 0 0; color: #666; font-size: 14px;">${activity.description}</p>` : ''}
                                ${activity.tips ? `<p style="margin: 6px 0 0 0; color: #0891b2; font-size: 13px;">💡 ${activity.tips}</p>` : ''}
                            </div>
                        `).join('');
                    }
                }
                
                let dayCostHTML = '';
                if (day.total_day_cost) {
                    dayCostHTML = `<div style="margin-top: 15px; padding: 10px; background: #e0f2fe; border-radius: 6px; text-align: right;"><strong>Day Total: ₹${day.total_day_cost.toLocaleString()}</strong></div>`;
                }
                
                return `
                    <div style="margin: 15px 0; padding: 20px; background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); border-radius: 10px; border-left: 4px solid #06b6d4;">
                        <h4 style="color: #06b6d4; margin-bottom: 15px;">${day.title}</h4>
                        ${activitiesHTML}
                        ${dayCostHTML}
                    </div>
                `;
            }).join('')}

            ${trip.recommendations ? `
                <div style="margin-top: 30px; padding: 20px; background: #f0f9ff; border-radius: 10px; border: 2px solid #06b6d4;">
                    <h3 style="color: #06b6d4; margin-bottom: 15px;">💡 Recommendations & Tips</h3>
                    
                    ${trip.recommendations.best_restaurants && trip.recommendations.best_restaurants.length > 0 ? `
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #333;">🍽️ Best Restaurants:</strong>
                            <p style="color: #666; margin: 5px 0;">${trip.recommendations.best_restaurants.join(', ')}</p>
                        </div>
                    ` : ''}
                    
                    ${trip.recommendations.free_attractions && trip.recommendations.free_attractions.length > 0 ? `
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #333;">🎫 Free Attractions:</strong>
                            <p style="color: #666; margin: 5px 0;">${trip.recommendations.free_attractions.join(', ')}</p>
                        </div>
                    ` : ''}
                    
                    ${trip.recommendations.local_transport_tips ? `
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #333;">🚌 Transport Tips:</strong>
                            <p style="color: #666; margin: 5px 0;">${trip.recommendations.local_transport_tips}</p>
                        </div>
                    ` : ''}
                    
                    ${trip.recommendations.must_try_foods && trip.recommendations.must_try_foods.length > 0 ? `
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #333;">🥘 Must Try Foods:</strong>
                            <p style="color: #666; margin: 5px 0;">${trip.recommendations.must_try_foods.join(', ')}</p>
                        </div>
                    ` : ''}
                    
                    ${trip.recommendations.safety_tips && trip.recommendations.safety_tips.length > 0 ? `
                        <div>
                            <strong style="color: #333;">🛡️ Safety Tips:</strong>
                            <ul style="color: #666; margin: 5px 0 0 20px;">
                                ${trip.recommendations.safety_tips.map(tip => `<li>${tip}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            ` : ''}

            <div style="margin-top: 30px; display: flex; gap: 15px; flex-wrap: wrap;">
                <button onclick="window.print()" style="background: #06b6d4; color: white; padding: 12px 30px; border: none; border-radius: 25px; cursor: pointer; font-size: 16px; font-weight: 600;">
                    🖨️ Print Itinerary
                </button>
                <button onclick="document.getElementById('tripPlanResult').remove()" style="background: #999; color: white; padding: 12px 30px; border: none; border-radius: 25px; cursor: pointer; font-size: 16px; font-weight: 600;">
                    ✖️ Close
                </button>
            </div>
        </div>
    `;

    // Insert after the form
    const plannerCard = document.querySelector('.planner-card');
    plannerCard.insertAdjacentHTML('afterend', planHTML);

    // Scroll to result
    document.getElementById('tripPlanResult').scrollIntoView({ behavior: 'smooth' });
}

// -------------------- Modal & OTP --------------------
function openModal() {
    document.getElementById('authModal').classList.add('active');
}

function closeModal() {
    document.getElementById('authModal').classList.remove('active');
    resetModal();
}

function resetModal() {
    document.getElementById('emailStep').style.display = 'block';
    document.getElementById('otpStep').style.display = 'none';
    document.getElementById('successMessage').style.display = 'none';
    document.getElementById('loginEmail').value = '';
    clearOTPInputs();
}

function clearOTPInputs() {
    for (let i = 1; i <= 6; i++) {
        document.getElementById('otp' + i).value = '';
    }
}

// Send OTP
async function sendOTP() {
    const email = document.getElementById('loginEmail').value;
    if (!email) return alert('Please enter your email');

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return alert('Please enter a valid email address');

    try {
        const response = await fetch(`${API_BASE_URL}/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.success) {
            alert('OTP sent to ' + email + '. Please check your email.');
            document.getElementById('emailStep').style.display = 'none';
            document.getElementById('otpStep').style.display = 'block';
            document.getElementById('otp1').focus();
        } else {
            alert(data.message || 'Failed to send OTP');
        }
    } catch (error) {
        console.error('Error sending OTP:', error);
        alert('An error occurred. Please try again.');
    }
}

// Verify OTP
async function verifyOTP() {
    const email = document.getElementById('loginEmail').value;
    const otp = Array.from({length:6}, (_,i) => document.getElementById('otp'+(i+1)).value).join('');

    if (otp.length !== 6) return alert('Please enter complete OTP');

    try {
        const response = await fetch(`${API_BASE_URL}/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp })
        });

        const data = await response.json();

        if (data.success) {
            setAuthToken(data.token);
            document.getElementById('otpStep').style.display = 'none';
            document.getElementById('successMessage').style.display = 'block';
            updateUIForLoggedIn(email);
            setTimeout(closeModal, 2000);
        } else {
            alert(data.message || 'Invalid OTP');
            clearOTPInputs();
            document.getElementById('otp1').focus();
        }
    } catch (error) {
        console.error('Error verifying OTP:', error);
        alert('An error occurred. Please try again.');
    }
}

// -------------------- UI Updates --------------------
function updateUIForLoggedIn(email) {
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.textContent = email.split('@')[0];
    loginBtn.onclick = () => { if (confirm('Do you want to logout?')) logout(); };
}

function updateUIForLoggedOut() {
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.textContent = 'Login';
    loginBtn.onclick = openModal;
}

function logout() {
    removeAuthToken();
    updateUIForLoggedOut();
    alert('Logged out successfully');
}

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

// -------------------- Modal Close on Outside Click --------------------
document.getElementById('authModal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
});

// -------------------- Smooth Scroll --------------------
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
        const href = anchor.getAttribute('href');
        
        // Skip if href is just "#" (for onclick handlers)
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

// -------------------- Check Existing Login --------------------
window.addEventListener('DOMContentLoaded', () => {
    const token = getAuthToken();
    if (!token) return;
    fetch(`${API_BASE_URL}/health`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.ok ? updateUIForLoggedIn('User') : removeAuthToken())
    .catch(() => {});
});
