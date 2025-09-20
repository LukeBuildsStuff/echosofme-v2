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

      // First, get user mapping if we need to filter by email
      let userIdFilter: string | null = null;
      if (user_filter && typeof user_filter === 'string' && user_filter !== 'all') {
        const { data: userData, error: userError } = await supabase
          .from('users')
          .select('id')
          .eq('email', user_filter)
          .single();

        if (userError) {
          console.warn('User filter email not found:', user_filter);
          // Return empty results if user email doesn't exist
          return res.status(200).json({
            responses: [],
            total: 0,
            limit: parseInt(limit as string, 10),
            offset: parseInt(offset as string, 10)
          });
        }
        userIdFilter = userData.id;
      }

      // Build the base query conditions
      let countQuery = supabase.from('responses').select('*', { count: 'exact', head: true });
      let mainQuery = supabase
        .from('responses')
        .select(`
          *,
          users(email)
        `)
        .order('created_at', { ascending: false });

      // Apply search filter to both queries
      if (search && typeof search === 'string') {
        const searchCondition = `response_text.ilike.%${search}%,id.eq.${search}`;
        countQuery = countQuery.or(searchCondition);
        mainQuery = mainQuery.or(searchCondition);
      }

      // Apply user filter to both queries
      if (userIdFilter) {
        countQuery = countQuery.eq('user_id', userIdFilter);
        mainQuery = mainQuery.eq('user_id', userIdFilter);
      }

      // Get total count with filters applied
      const { count, error: countError } = await countQuery;

      if (countError) {
        throw countError;
      }

      // Apply pagination to main query
      const limitNum = parseInt(limit as string, 10);
      const offsetNum = parseInt(offset as string, 10);

      mainQuery = mainQuery.range(offsetNum, offsetNum + limitNum - 1);

      const { data: responses, error } = await mainQuery;

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
      // Delete response - get ID from query parameters
      const { id } = req.query;

      if (!id || Array.isArray(id) || isNaN(parseInt(id, 10))) {
        return res.status(400).json({ error: 'Invalid response ID' });
      }

      const responseId = parseInt(id, 10);

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