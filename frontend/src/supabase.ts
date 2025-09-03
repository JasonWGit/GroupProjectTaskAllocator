import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY; // Do NOT expose service role key on frontend!

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    autoRefreshToken: true, // Automatically refresh tokens
    persistSession: true, // Keeps user logged in across page reloads
    detectSessionInUrl: true, // Handles OAuth redirects properly
  },
});
