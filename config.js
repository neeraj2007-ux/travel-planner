// config.js - Frontend configuration for Travel Planner
// config.js
export const API_BASE_URL = 'https://travel-planner-aax3.onrender.com'; // or your deployed backend URL
// Supabase project URL
const SUPABASE_URL = 'https://yjjlosnssellukbdvrea.supabase.co'; // Replace with your Supabase URL from .env

// Supabase anon/public key (safe for frontend use)
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlqamxvc25zc2VsbHVrYmR2cmVhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyNDI4MjIsImV4cCI6MjA4NzgxODgyMn0.JMObYNmYgfjyqnmxiGLsOv-gGPuRyhyQPLkzL5CjSps'; // Replace with your SUPABASE_KEY from .env (anon key)

// Initialize Supabase client
const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);