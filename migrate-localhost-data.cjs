#!/usr/bin/env node

/**
 * Direct localStorage Migration Script
 * 
 * This script connects to the browser's localStorage and migrates reflection data
 * while preserving user profile associations.
 */

const { Pool } = require('pg');
const fs = require('fs');

const pool = new Pool({
    host: 'localhost',
    database: 'echosofme_dev',
    user: 'echosofme',
    password: 'secure_dev_password',
    port: 5432
});

class DirectMigrator {
    constructor() {
        this.stats = {
            reflections: 0,
            users: 0,
            errors: 0
        };
    }

    async migrate() {
        console.log('🔄 Starting direct localhost localStorage migration...');
        
        try {
            await this.testConnection();
            await this.migrateLocalhostData();
            this.showResults();
            
        } catch (error) {
            console.error('💥 Migration failed:', error.message);
            throw error;
        } finally {
            await pool.end();
        }
    }

    async testConnection() {
        const client = await pool.connect();
        const result = await client.query('SELECT COUNT(*) as count FROM responses');
        console.log(`✅ Database connected. Current responses: ${result.rows[0].count}`);
        client.release();
    }

    async migrateLocalhostData() {
        console.log('\n📊 Analyzing localhost localStorage patterns...');
        
        // We need to create a browser automation script since we can't directly access localStorage from Node.js
        const puppeteerScript = this.generatePuppeteerScript();
        
        // Write the script to a temporary file
        fs.writeFileSync('/tmp/extract-localhost-data.js', puppeteerScript);
        
        console.log('📝 Created browser extraction script');
        console.log('🚀 You have two options:');
        console.log('\n   Option 1 (Automated): Install puppeteer and run automated extraction');
        console.log('   Option 2 (Manual): Run the extraction script in browser console');
        
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        return new Promise((resolve, reject) => {
            rl.question('\\nChoose option (1 for automated, 2 for manual, or press Enter for manual): ', async (answer) => {
                rl.close();
                
                if (answer === '1') {
                    await this.runAutomatedExtraction();
                } else {
                    await this.runManualExtraction();
                }
                resolve();
            });
        });
    }

    async runAutomatedExtraction() {
        console.log('\\n🤖 Attempting automated extraction...');
        
        try {
            // Try to use puppeteer if available
            const puppeteer = require('puppeteer');
            
            const browser = await puppeteer.launch({ headless: false });
            const page = await browser.newPage();
            
            // Navigate to localhost
            await page.goto('http://localhost:5173');
            await page.waitForTimeout(2000);
            
            // Extract localStorage data
            const localStorageData = await page.evaluate(() => {
                const data = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    const value = localStorage.getItem(key);
                    data[key] = value;
                }
                return data;
            });
            
            await browser.close();
            
            // Process the extracted data
            await this.processExtractedData(localStorageData);
            
        } catch (error) {
            if (error.code === 'MODULE_NOT_FOUND') {
                console.log('📦 Puppeteer not installed. Install with: npm install puppeteer');
                console.log('🔄 Falling back to manual extraction...');
                await this.runManualExtraction();
            } else {
                throw error;
            }
        }
    }

    async runManualExtraction() {
        console.log('\\n🖥️  Manual extraction steps:');
        console.log('1. Open http://localhost:5173 in your browser');
        console.log('2. Press F12 to open DevTools');
        console.log('3. Go to Console tab');
        console.log('4. Copy and paste this code:');
        console.log('\\n' + '='.repeat(60));
        console.log(this.getBrowserConsoleCode());
        console.log('='.repeat(60));
        console.log('\\n5. Copy the JSON output and paste it when prompted');
        
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        return new Promise((resolve) => {
            rl.question('\\nPaste the JSON output from browser console: ', async (jsonData) => {
                rl.close();
                
                try {
                    const data = JSON.parse(jsonData);
                    await this.processExtractedData(data);
                } catch (error) {
                    console.error('❌ Error parsing JSON:', error.message);
                    console.log('💡 Make sure you copied the complete JSON output');
                }
                resolve();
            });
        });
    }

    getBrowserConsoleCode() {
        return `
// Extract localStorage data with user profile context
(() => {
    const extractionData = {
        timestamp: new Date().toISOString(),
        domain: window.location.hostname,
        url: window.location.href,
        localStorage: {},
        userProfile: null,
        reflections: null
    };

    // Get all localStorage data
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const value = localStorage.getItem(key);
        extractionData.localStorage[key] = value;
    }

    // Try to get user profile
    try {
        extractionData.userProfile = JSON.parse(localStorage.getItem('echos_user_profile') || 'null');
    } catch (e) {
        console.log('No user profile found');
    }

    // Find and parse reflections
    const reflectionKeys = Object.keys(extractionData.localStorage).filter(k => 
        k.includes('reflection') || k === 'echos_reflections'
    );
    
    console.log('Found reflection keys:', reflectionKeys);
    
    for (const key of reflectionKeys) {
        try {
            const parsed = JSON.parse(extractionData.localStorage[key]);
            if (Array.isArray(parsed)) {
                extractionData.reflections = {
                    key: key,
                    count: parsed.length,
                    data: parsed
                };
                break;
            }
        } catch (e) {
            console.log('Could not parse:', key);
        }
    }

    console.log('=== EXTRACTION COMPLETE ===');
    console.log('Copy the JSON below:');
    console.log(JSON.stringify(extractionData, null, 2));
    
    return extractionData;
})();`;
    }

    async processExtractedData(data) {
        console.log('\\n🔍 Processing extracted data...');
        
        if (!data.reflections || !data.reflections.data) {
            console.log('❌ No reflections found in localStorage data');
            return;
        }

        const reflections = data.reflections.data;
        const userProfile = data.userProfile;
        
        console.log(`📊 Found ${reflections.length} reflections`);
        console.log(`👤 User profile:`, userProfile ? userProfile.email || 'Unknown' : 'None');
        
        // Determine user email
        let userEmail = 'localhost-migration@local.dev';
        if (userProfile && userProfile.email) {
            userEmail = userProfile.email;
        } else if (userProfile && userProfile.displayName) {
            userEmail = `${userProfile.displayName.toLowerCase().replace(/\\s+/g, '.')}@localhost.local`;
        }

        console.log(`🎯 Migrating reflections for user: ${userEmail}`);
        
        // Ensure user exists
        const userId = await this.ensureUser(userEmail, userProfile);
        
        // Migrate reflections
        for (const reflection of reflections) {
            await this.migrateReflection(reflection, userId, userEmail);
        }
    }

    async ensureUser(email, profile) {
        const client = await pool.connect();
        
        try {
            let result = await client.query('SELECT id FROM users WHERE email = $1', [email]);
            
            if (result.rows.length > 0) {
                console.log(`✅ Found existing user: ${email}`);
                this.stats.users++;
                return result.rows[0].id;
            }
            
            const name = profile && profile.displayName ? profile.displayName : email.split('@')[0];
            result = await client.query(
                'INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id',
                [email, name]
            );
            
            console.log(`✅ Created new user: ${email} (${name})`);
            this.stats.users++;
            return result.rows[0].id;
            
        } finally {
            client.release();
        }
    }

    async migrateReflection(reflection, userId, userEmail) {
        const client = await pool.connect();
        
        try {
            const dbReflection = {
                user_id: userId,
                question_id: reflection.questionId || Math.floor(Math.random() * 90000) + 10000,
                response_text: reflection.response || reflection.content || '',
                word_count: reflection.wordCount || (reflection.response || '').split(' ').length,
                is_draft: reflection.isDraft || false,
                created_at: reflection.createdAt || new Date().toISOString()
            };
            
            const insertQuery = `
                INSERT INTO responses (user_id, question_id, response_text, word_count, is_draft, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (user_id, question_id) 
                DO UPDATE SET 
                    response_text = EXCLUDED.response_text,
                    word_count = EXCLUDED.word_count,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            `;
            
            await client.query(insertQuery, [
                dbReflection.user_id,
                dbReflection.question_id,
                dbReflection.response_text,
                dbReflection.word_count,
                dbReflection.is_draft,
                dbReflection.created_at
            ]);
            
            this.stats.reflections++;
            
            if (this.stats.reflections % 5 === 0) {
                console.log(`   Migrated ${this.stats.reflections} reflections...`);
            }
            
        } catch (error) {
            console.error(`❌ Error migrating reflection:`, error.message);
            this.stats.errors++;
        } finally {
            client.release();
        }
    }

    showResults() {
        console.log('\\n🎉 Migration Complete!');
        console.log('═'.repeat(50));
        console.log(`📊 Results:`);
        console.log(`   Reflections migrated: ${this.stats.reflections}`);
        console.log(`   Users processed:      ${this.stats.users}`);
        console.log(`   Errors:               ${this.stats.errors}`);
        
        if (this.stats.reflections > 0) {
            console.log('\\n✅ All localhost reflections have been migrated to the database!');
            console.log('🔄 Next: Update frontend to use database as primary source');
        }
    }

    generatePuppeteerScript() {
        return `
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(2000);
    
    const data = await page.evaluate(() => {
        ${this.getBrowserConsoleCode()}
    });
    
    console.log(JSON.stringify(data, null, 2));
    await browser.close();
})();
`;
    }
}

async function main() {
    console.log('🚀 Direct localStorage Migration Tool');
    console.log('📋 This will migrate your 24 localhost reflections to the database');
    
    const migrator = new DirectMigrator();
    
    try {
        await migrator.migrate();
    } catch (error) {
        console.error('\\n💥 Migration failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { DirectMigrator };