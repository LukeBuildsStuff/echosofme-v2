import type { VercelRequest, VercelResponse } from '@vercel/node';
import { createClient } from '@supabase/supabase-js';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Initialize Supabase client
    const supabaseUrl = process.env.VITE_SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

    if (!supabaseUrl || !supabaseServiceKey) {
      return res.status(500).json({
        status: 'error',
        message: 'Missing Supabase configuration',
        timestamp: new Date().toISOString()
      });
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Test Supabase connection with a simple query
    const { data, error } = await supabase
      .from('questions')
      .select('id')
      .limit(1);

    if (error) {
      return res.status(500).json({
        status: 'error',
        message: 'Supabase connection failed',
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }

    // Return success response
    return res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      supabase: 'connected',
      environment: process.env.NODE_ENV || 'development'
    });

  } catch (error) {
    console.error('Health check error:', error);
    return res.status(500).json({
      status: 'error',
      message: 'Internal server error',
      timestamp: new Date().toISOString()
    });
  }
}