// Point to your local backend for development
// Ensure this matches the port in app.py
window.API_BASE_URL = "https://travel-planner-aax3.onrender.com"; 

// If you need direct Supabase access from frontend (optional based on your backend logic)
window.SUPABASE_URL = 'https://yjjlosnssellukbdvrea.supabase.co';
window.SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlqamxvc25zc2VsbHVrYmR2cmVhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyNDI4MjIsImV4cCI6MjA4NzgxODgyMn0.JMObYNmYgfjyqnmxiGLsOv-gGPuRyhyQPLkzL5CjSps'; // Replace with your SUPABASE_KEY from .env (anon key)
window.supabase = supabase.createClient(window.SUPABASE_URL, window.SUPABASE_KEY);