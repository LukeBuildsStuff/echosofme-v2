#!/usr/bin/env node

/**
 * Direct Database Migration - Simplest Approach
 * 
 * This script directly inserts localStorage data into PostgreSQL,
 * bypassing the Eleanor API to avoid constraints.
 */

const { Pool } = require('pg');
const readline = require('readline');

const pool = new Pool({
    host: 'localhost',
    database: 'echosofme_dev',
    user: 'echosofme',
    password: 'secure_dev_password',
    port: 5432
});

async function directMigration() {
    console.log('🚀 Direct Database Migration Tool');
    console.log('📋 This will help you migrate your localhost reflections directly');
    
    try {
        // Test connection
        const client = await pool.connect();
        const result = await client.query('SELECT COUNT(*) as count FROM responses');
        console.log(`✅ Database connected. Current responses: ${result.rows[0].count}`);
        client.release();
        
        console.log('\n📝 Please copy the reflection data from your browser:');
        console.log('1. Go to http://localhost:5173');
        console.log('2. Open DevTools (F12) → Console');
        console.log('3. Paste this code:');
        console.log('\n' + '='.repeat(60));
        console.log(`
// Extract localStorage reflections
(() => {
    let reflections = [];
    let userEmail = 'localhost-user@migration.local';
    
    // Try to get user profile
    try {
        const profile = JSON.parse(localStorage.getItem('echos_user_profile') || 'null');
        if (profile && profile.email) {
            userEmail = profile.email;
        }
    } catch (e) {}
    
    // Find reflections
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.includes('reflection') || key === 'echos_reflections' || key.startsWith('echos_reflections_'))) {
            try {
                const data = JSON.parse(localStorage.getItem(key));
                if (Array.isArray(data) && data.length > 0) {
                    reflections = data;
                    break;
                }
            } catch (e) {}
        }
    }
    
    console.log('=== COPY THE JSON BELOW ===');
    console.log(JSON.stringify({
        userEmail: userEmail,
        reflections: reflections,
        count: reflections.length
    }, null, 2));
})();
        `);
        console.log('='.repeat(60));
        
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        
        return new Promise((resolve) => {
            rl.question('\n📋 Paste the JSON data here: ', async (jsonData) => {
                rl.close();
                
                try {
                    const data = JSON.parse(jsonData);
                    console.log(`\n✅ Parsed data: ${data.count} reflections for ${data.userEmail}`);
                    
                    await processReflections(data);
                    
                } catch (error) {
                    console.error('❌ Error:', error.message);
                }
                resolve();
            });
        });
        
    } catch (error) {
        console.error('💥 Connection failed:', error.message);
    } finally {
        await pool.end();
    }
}

async function processReflections(data) {
    console.log('\n🔄 Processing reflections...');
    
    const client = await pool.connect();
    
    try {
        // Ensure user exists
        let result = await client.query('SELECT id FROM users WHERE email = $1', [data.userEmail]);
        let userId;
        
        if (result.rows.length > 0) {
            userId = result.rows[0].id;
            console.log(`✅ Found user: ${data.userEmail} (ID: ${userId})`);
        } else {
            result = await client.query(
                'INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id',
                [data.userEmail, data.userEmail.split('@')[0]]
            );
            userId = result.rows[0].id;
            console.log(`✅ Created user: ${data.userEmail} (ID: ${userId})`);
        }
        
        // Insert reflections with VERY high question IDs to avoid conflicts
        let successCount = 0;
        let startingQuestionId = 100000; // Start way above existing questions
        
        for (let i = 0; i < data.reflections.length; i++) {
            const reflection = data.reflections[i];
            const questionId = startingQuestionId + i; // Sequential, guaranteed unique
            
            try {
                await client.query(`
                    INSERT INTO responses (user_id, question_id, response_text, word_count, is_draft, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                `, [
                    userId,
                    questionId,
                    reflection.response || reflection.content || '',
                    reflection.wordCount || (reflection.response || '').split(' ').length,
                    reflection.isDraft || false,
                    reflection.createdAt || new Date().toISOString()
                ]);
                
                successCount++;
                
                if ((i + 1) % 5 === 0) {
                    console.log(`   ✅ Migrated ${i + 1}/${data.reflections.length} reflections...`);
                }
                
            } catch (error) {
                console.error(`   ❌ Failed reflection ${i + 1}: ${error.message}`);
            }
        }
        
        console.log(`\n🎉 Migration complete!`);
        console.log(`   Successfully migrated: ${successCount}/${data.reflections.length}`);
        console.log(`   Question IDs used: ${startingQuestionId} to ${startingQuestionId + data.reflections.length - 1}`);
        
        // Final verification
        result = await client.query('SELECT COUNT(*) as count FROM responses WHERE user_id = $1', [userId]);
        console.log(`   Total reflections for user: ${result.rows[0].count}`);
        
    } finally {
        client.release();
    }
}

if (require.main === module) {
    directMigration().catch(console.error);
}