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
  res.setHeader('Access-Control-Allow-Methods', 'GET, DELETE, OPTIONS');
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
      // Get responses with pagination and filtering
      const {
        limit = '50',
        offset = '0',
        search,
        user_filter
      } = req.query;

      let query = supabase
        .from('responses')
        .select(`
          *,
          users!responses_user_id_fkey(email)
        `)
        .order('created_at', { ascending: false });

      // Apply search filter
      if (search && typeof search === 'string') {
        query = query.or(`response_text.ilike.%${search}%,id.eq.${search}`);
      }

      // Apply user filter
      if (user_filter && typeof user_filter === 'string' && user_filter !== 'all') {
        // Need to join with users table to filter by email
        query = query.eq('users.email', user_filter);
      }

      // Get total count first
      const { count, error: countError } = await supabase
        .from('responses')
        .select('*', { count: 'exact', head: true });

      if (countError) {
        throw countError;
      }

      // Apply pagination
      const limitNum = parseInt(limit as string, 10);
      const offsetNum = parseInt(offset as string, 10);

      query = query.range(offsetNum, offsetNum + limitNum - 1);

      const { data: responses, error } = await query;

      if (error) {
        throw error;
      }

      // Transform the data to match expected format
      const transformedResponses = responses?.map(response => ({
        id: response.id,
        user_id: response.user_id,
        question_id: response.question_id,
        response_text: response.response_text,
        word_count: response.word_count,
        created_at: response.created_at,
        question_text_snapshot: response.question_text_snapshot,
        category_snapshot: response.category_snapshot,
        user_email: response.users?.email
      })) || [];

      return res.status(200).json({
        responses: transformedResponses,
        total: count || 0,
        limit: limitNum,
        offset: offsetNum
      });

    } else if (req.method === 'DELETE') {
      // Delete response
      const responseId = req.url?.split('/').pop();
      if (!responseId || isNaN(parseInt(responseId, 10))) {
        return res.status(400).json({ error: 'Invalid response ID' });
      }

      const { error } = await supabase
        .from('responses')
        .delete()
        .eq('id', responseId);

      if (error) {
        throw error;
      }

      return res.status(200).json({ message: 'Response deleted successfully' });

    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }

  } catch (error) {
    console.error('Admin Responses API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}