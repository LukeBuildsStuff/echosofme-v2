import type { VercelRequest, VercelResponse } from '@vercel/node';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  throw new Error('Missing Supabase environment variables');
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

// Admin email check
const ADMIN_EMAIL = 'lukemoeller@yahoo.com';

// Verify admin authorization
async function verifyAdmin(req: VercelRequest): Promise<string | null> {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return 'Missing or invalid authorization header';
  }

  const token = authHeader.substring(7);

  try {
    const { data: { user }, error } = await supabase.auth.getUser(token);

    if (error || !user) {
      return 'Invalid token';
    }

    if (user.email !== ADMIN_EMAIL) {
      return 'Access denied - admin privileges required';
    }

    return null; // Success
  } catch (error) {
    return 'Authentication error';
  }
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Verify admin authorization
  const authError = await verifyAdmin(req);
  if (authError) {
    return res.status(401).json({ error: authError });
  }

  try {
    if (req.method === 'GET') {
      // Get users who have reflections with their reflection counts
      const { data: users, error } = await supabase
        .from('users')
        .select(`
          email,
          reflections!reflections_user_id_fkey(id)
        `)
        .order('email');

      if (error) {
        throw error;
      }

      // Transform data to include reflection counts
      const usersWithCounts = users?.map(user => ({
        email: user.email,
        response_count: user.reflections?.length || 0
      }))
      .filter(user => user.response_count > 0) // Only include users with reflections
      .sort((a, b) => b.response_count - a.response_count); // Sort by reflection count descending

      return res.status(200).json({
        users: usersWithCounts || []
      });

    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }

  } catch (error) {
    console.error('Admin Users API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}