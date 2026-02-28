// API Base URL - Change this to your deployed backend URL
const API_BASE_URL = 'http://localhost:5000/api';

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('authToken');
}

// Set auth token in localStorage
function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

// Remove auth token
function removeAuthToken() {
    localStorage.removeItem('authToken');
}

// Form submission
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
    
    // Check if user is logged in
    const token = getAuthToken();
    if (!token) {
        alert('Please login to generate your trip plan!');
        openModal();
        return;
    }

    // Show loading
    const submitBtn = document.querySelector('.generate-btn');
    submitBtn.textContent = 'Generating...';
    submitBtn.disabled = true;

    // Call API to generate trip
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

        if (data.success) {
            alert('Trip plan generated successfully!');
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
        alert('An error occurred. Please try again.');
    } finally {
        submitBtn.textContent = 'Generate Trip Plan';
        submitBtn.disabled = false;
    }
});

function displayTripPlan(trip) {
    // Create a simple display of the trip plan
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
            ${trip.itinerary.map(day => `
                <div style="margin: 15px 0; padding: 20px; background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%); border-radius: 10px; border-left: 4px solid #06b6d4;">
                    <h4 style="color: #06b6d4; margin-bottom: 10px;">${day.title}</h4>
                    <ul style="margin-left: 20px; line-height: 1.8;">
                        ${day.activities.map(activity => `<li>${activity}</li>`).join('')}
                    </ul>
                </div>
            `).join('')}

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

    // Remove any existing trip plan
    const existingPlan = document.getElementById('tripPlanResult');
    if (existingPlan) {
        existingPlan.remove();
    }

    // Insert after the form
    const plannerCard = document.querySelector('.planner-card');
    plannerCard.insertAdjacentHTML('afterend', planHTML);

    // Scroll to result
    document.getElementById('tripPlanResult').scrollIntoView({ behavior: 'smooth' });
}

// Modal functions
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
    
    // Validate email
    if (!email) {
        alert('Please enter your email');
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/send-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email })
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
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

// Verify OTP
async function verifyOTP() {
    const email = document.getElementById('loginEmail').value;
    const otp = document.getElementById('otp1').value +
                document.getElementById('otp2').value +
                document.getElementById('otp3').value +
                document.getElementById('otp4').value +
                document.getElementById('otp5').value +
                document.getElementById('otp6').value;
    
    if (otp.length !== 6) {
        alert('Please enter complete OTP');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/verify-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, otp: otp })
        });

        const data = await response.json();

        if (data.success) {
            // Store token
            setAuthToken(data.token);
            
            // Show success message
            document.getElementById('otpStep').style.display = 'none';
            document.getElementById('successMessage').style.display = 'block';
            
            // Update UI
            updateUIForLoggedIn(email);
            
            setTimeout(() => {
                closeModal();
            }, 2000);
        } else {
            alert(data.message || 'Invalid OTP');
            clearOTPInputs();
            document.getElementById('otp1').focus();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

// Update UI for logged in user
function updateUIForLoggedIn(email) {
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.textContent = email.split('@')[0];
    loginBtn.onclick = function() {
        if (confirm('Do you want to logout?')) {
            logout();
        }
    };
}

// Update UI for logged out user
function updateUIForLoggedOut() {
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.textContent = 'Login';
    loginBtn.onclick = openModal;
}

// Logout function
function logout() {
    removeAuthToken();
    updateUIForLoggedOut();
    alert('Logged out successfully');
}

// Auto-focus next OTP input
const otpInputs = document.querySelectorAll('.otp-input');
otpInputs.forEach((input, index) => {
    // Move to next input on digit entry
    input.addEventListener('input', function(e) {
        // Only allow numbers
        this.value = this.value.replace(/[^0-9]/g, '');
        
        if (this.value.length === 1 && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }
    });
    
    // Move to previous input on backspace
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && this.value === '' && index > 0) {
            otpInputs[index - 1].focus();
        }
    });
    
    // Prevent non-numeric input
    input.addEventListener('keypress', function(e) {
        if (!/[0-9]/.test(e.key)) {
            e.preventDefault();
        }
    });
});

// Close modal on outside click
document.getElementById('authModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Check if user is already logged in (on page load)
window.addEventListener('DOMContentLoaded', function() {
    const authToken = getAuthToken();
    if (authToken) {
        // Verify token is still valid
        fetch(`${API_BASE_URL}/health`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        }).then(response => {
            if (response.ok) {
                // Token is valid, update UI
                updateUIForLoggedIn('User');
            } else {
                // Token expired, clear it
                removeAuthToken();
            }
        }).catch(() => {
            // Server error, keep token for now
        });
    }
});
