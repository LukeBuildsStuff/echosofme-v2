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

// Simple similarity function (Levenshtein distance)
function getLevenshteinDistance(str1: string, str2: string): number {
  const matrix = Array(str2.length + 1).fill(null).map(() => Array(str1.length + 1).fill(null));

  for (let i = 0; i <= str1.length; i += 1) {
    matrix[0][i] = i;
  }

  for (let j = 0; j <= str2.length; j += 1) {
    matrix[j][0] = j;
  }

  for (let j = 1; j <= str2.length; j += 1) {
    for (let i = 1; i <= str1.length; i += 1) {
      const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1, // deletion
        matrix[j - 1][i] + 1, // insertion
        matrix[j - 1][i - 1] + indicator, // substitution
      );
    }
  }

  return matrix[str2.length][str1.length];
}

function areSimilar(str1: string, str2: string, threshold: number = 0.8): boolean {
  const maxLength = Math.max(str1.length, str2.length);
  const distance = getLevenshteinDistance(str1.toLowerCase(), str2.toLowerCase());
  const similarity = 1 - (distance / maxLength);
  return similarity >= threshold;
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
      // Get all questions
      const { data: questions, error } = await supabase
        .from('questions')
        .select('id, question_text, category')
        .order('id');

      if (error) {
        throw error;
      }

      if (!questions || questions.length === 0) {
        return res.status(200).json({ duplicate_groups: [] });
      }

      // Find duplicate groups
      const duplicateGroups: Array<Array<any>> = [];
      const processedIds = new Set<number>();

      for (let i = 0; i < questions.length; i++) {
        const currentQuestion = questions[i];

        if (processedIds.has(currentQuestion.id)) {
          continue;
        }

        const similarQuestions = [currentQuestion];
        processedIds.add(currentQuestion.id);

        // Check against remaining questions
        for (let j = i + 1; j < questions.length; j++) {
          const otherQuestion = questions[j];

          if (processedIds.has(otherQuestion.id)) {
            continue;
          }

          // Check if questions are similar
          if (areSimilar(currentQuestion.question_text, otherQuestion.question_text)) {
            similarQuestions.push(otherQuestion);
            processedIds.add(otherQuestion.id);
          }
        }

        // If we found similar questions, add to duplicate groups
        if (similarQuestions.length > 1) {
          duplicateGroups.push(similarQuestions);
        }
      }

      return res.status(200).json({
        duplicate_groups: duplicateGroups
      });

    } else {
      return res.status(405).json({ error: 'Method not allowed' });
    }

  } catch (error) {
    console.error('Admin Duplicates API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}