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
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
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
      // Get questions with pagination and filtering
      const {
        limit = '50',
        offset = '0',
        search,
        category
      } = req.query;

      let query = supabase
        .from('questions')
        .select('*')
        .order('id', { ascending: false });

      // Apply search filter
      if (search && typeof search === 'string') {
        query = query.or(`question_text.ilike.%${search}%,id.eq.${search}`);
      }

      // Apply category filter
      if (category && typeof category === 'string' && category !== 'all') {
        query = query.eq('category', category);
      }

      // Get total count first
      const { count, error: countError } = await supabase
        .from('questions')
        .select('*', { count: 'exact', head: true });

      if (countError) {
        throw countError;
      }

      // Apply pagination
      const limitNum = parseInt(limit as string, 10);
      const offsetNum = parseInt(offset as string, 10);

      query = query.range(offsetNum, offsetNum + limitNum - 1);

      const { data: questions, error } = await query;

      if (error) {
        throw error;
      }

      return res.status(200).json({
        questions: questions || [],
        total: count || 0,
        limit: limitNum,
        offset: offsetNum
      });

    } else if (req.method === 'PUT') {
      // Update question
      const questionId = req.url?.split('/').pop();
      if (!questionId || isNaN(parseInt(questionId, 10))) {
        return res.status(400).json({ error: 'Invalid question ID' });
      }

      const { question_text, category } = req.body;

      if (!question_text && !category) {
        return res.status(400).json({ error: 'No updates provided' });
      }

      const updates: any = {};
      if (question_text) updates.question_text = question_text;
      if (category) updates.category = category;

      const { data, error } = await supabase
        .from('questions')
        .update(updates)
        .eq('id', questionId)
        .select()
        .single();

      if (error) {
        throw error;
      }

      return res.status(200).json({ question: data });

    } else if (req.method === 'DELETE') {
      // Delete question
      const questionId = req.url?.split('/').pop();
      if (!questionId || isNaN(parseInt(questionId, 10))) {
        return res.status(400).json({ error: 'Invalid question ID' });
      }

      const { error } = await supabase
        .from('questions')
        .delete()
        .eq('id', questionId);

      if (error) {
        throw error;
      }

      return res.status(200).json({ message: 'Question deleted successfully' });

    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }

  } catch (error) {
    console.error('Admin Questions API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}