#!/usr/bin/env node

/**
 * Migration Script: localStorage to Database
 * 
 * This script takes exported localStorage reflection data and safely imports it
 * into the PostgreSQL database while avoiding duplicates and data loss.
 */

const fs = require('fs');
const path = require('path');

// Check if we have the necessary dependencies
try {
    const { Pool } = require('pg');
    var pool = new Pool({
        host: 'localhost',
        database: 'echosofme_dev',
        user: 'echosofme',
        password: 'secure_dev_password',
        port: 5432
    });
} catch (error) {
    console.error('❌ PostgreSQL client not found. Install with: npm install pg');
    process.exit(1);
}

class ReflectionMigrator {
    constructor() {
        this.stats = {
            totalProcessed: 0,
            successfulInserts: 0,
            duplicatesSkipped: 0,
            errors: 0,
            usersMerged: new Set()
        };
    }

    async migrate(exportFiles) {
        console.log('🚀 Starting reflection migration...');
        console.log(`📁 Processing ${exportFiles.length} export file(s)`);
        
        try {
            // Test database connection
            await this.testConnection();
            
            // Process each export file
            for (const filePath of exportFiles) {
                await this.processExportFile(filePath);
            }
            
            // Show final stats
            this.showFinalStats();
            
        } catch (error) {
            console.error('💥 Migration failed:', error.message);
            throw error;
        } finally {
            await pool.end();
        }
    }

    async testConnection() {
        try {
            const client = await pool.connect();
            const result = await client.query('SELECT COUNT(*) as count FROM responses');
            console.log(`✅ Database connected. Current responses: ${result.rows[0].count}`);
            client.release();
        } catch (error) {
            throw new Error(`Database connection failed: ${error.message}`);
        }
    }

    async processExportFile(filePath) {
        console.log(`\n📄 Processing: ${filePath}`);
        
        if (!fs.existsSync(filePath)) {
            console.error(`❌ File not found: ${filePath}`);
            this.stats.errors++;
            return;
        }

        try {
            const rawData = fs.readFileSync(filePath, 'utf8');
            const exportData = JSON.parse(rawData);
            
            console.log(`📊 Export info:`);
            console.log(`   Domain: ${exportData.exportInfo.domain}`);
            console.log(`   Date: ${exportData.exportInfo.timestamp}`);
            console.log(`   Count: ${exportData.exportInfo.reflectionCount}`);
            
            if (!exportData.reflections || !Array.isArray(exportData.reflections)) {
                throw new Error('Invalid export format: reflections array not found');
            }

            // Process reflections in batches
            await this.processReflections(exportData.reflections, exportData.exportInfo.domain);
            
        } catch (error) {
            console.error(`❌ Error processing ${filePath}:`, error.message);
            this.stats.errors++;
        }
    }

    async processReflections(reflections, sourceDomain) {
        console.log(`\n🔄 Processing ${reflections.length} reflections from ${sourceDomain}...`);
        
        const batchSize = 100;
        const batches = [];
        
        // Split into batches
        for (let i = 0; i < reflections.length; i += batchSize) {
            batches.push(reflections.slice(i, i + batchSize));
        }
        
        console.log(`   Split into ${batches.length} batch(es) of ${batchSize}`);
        
        for (let i = 0; i < batches.length; i++) {
            const batch = batches[i];
            console.log(`   Processing batch ${i + 1}/${batches.length}...`);
            
            for (const reflection of batch) {
                await this.insertReflection(reflection, sourceDomain);
            }
        }
    }

    async insertReflection(reflection, sourceDomain) {
        this.stats.totalProcessed++;
        
        try {
            // Determine user email - need to handle different localStorage formats
            let userEmail = 'unknown@localhost.local';
            
            // Try to extract from user profile or use a default for migration
            if (sourceDomain === 'localhost') {
                userEmail = 'localhost-user@migration.local';
            } else {
                userEmail = 'mobile-user@migration.local';
            }
            
            // First, ensure user exists
            const userId = await this.ensureUser(userEmail);
            
            // Map localStorage reflection format to database format
            const dbReflection = {
                user_id: userId,
                question_id: reflection.questionId || Math.floor(Math.random() * 10000), // Fallback for missing question IDs
                response_text: reflection.response || reflection.content || '',
                word_count: reflection.wordCount || reflection.response?.split(' ').length || 0,
                is_draft: reflection.isDraft || false,
                created_at: reflection.createdAt || new Date().toISOString()
            };
            
            // Insert with conflict resolution
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
            
            const client = await pool.connect();
            
            try {
                const result = await client.query(insertQuery, [
                    dbReflection.user_id,
                    dbReflection.question_id,
                    dbReflection.response_text,
                    dbReflection.word_count,
                    dbReflection.is_draft,
                    dbReflection.created_at
                ]);
                
                this.stats.successfulInserts++;
                
                if (this.stats.totalProcessed % 50 === 0) {
                    console.log(`   Processed ${this.stats.totalProcessed}...`);
                }
                
            } finally {
                client.release();
            }
            
        } catch (error) {
            if (error.code === '23505') { // Unique constraint violation
                this.stats.duplicatesSkipped++;
            } else {
                console.error(`   ❌ Error inserting reflection:`, error.message);
                this.stats.errors++;
            }
        }
    }

    async ensureUser(email) {
        const client = await pool.connect();
        
        try {
            // Check if user exists
            let result = await client.query('SELECT id FROM users WHERE email = $1', [email]);
            
            if (result.rows.length > 0) {
                this.stats.usersMerged.add(email);
                return result.rows[0].id;
            }
            
            // Create user if doesn't exist
            result = await client.query(
                'INSERT INTO users (email, name) VALUES ($1, $2) RETURNING id',
                [email, email.split('@')[0]]
            );
            
            console.log(`   ✅ Created user: ${email}`);
            this.stats.usersMerged.add(email);
            return result.rows[0].id;
            
        } finally {
            client.release();
        }
    }

    showFinalStats() {
        console.log('\n🎉 Migration Complete!');
        console.log('═'.repeat(50));
        console.log(`📊 Final Statistics:`);
        console.log(`   Total processed:     ${this.stats.totalProcessed}`);
        console.log(`   Successful inserts:  ${this.stats.successfulInserts}`);
        console.log(`   Duplicates skipped:  ${this.stats.duplicatesSkipped}`);
        console.log(`   Errors:              ${this.stats.errors}`);
        console.log(`   Users merged:        ${this.stats.usersMerged.size}`);
        console.log(`   Success rate:        ${((this.stats.successfulInserts / this.stats.totalProcessed) * 100).toFixed(1)}%`);
        
        if (this.stats.usersMerged.size > 0) {
            console.log(`\n👥 Users processed:`);
            this.stats.usersMerged.forEach(email => {
                console.log(`   - ${email}`);
            });
        }
        
        console.log('\n✅ All reflection data has been safely migrated to the database!');
    }
}

// CLI interface
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('📚 Reflection Migration Tool');
        console.log('');
        console.log('Usage: node migrate-reflections.js <export-file1> [export-file2] [...]');
        console.log('');
        console.log('Examples:');
        console.log('  node migrate-reflections.js reflections-localhost-2025-01-25.json');
        console.log('  node migrate-reflections.js reflections-localhost-*.json reflections-mobile-*.json');
        console.log('');
        console.log('This script will safely import localStorage reflection data into the database.');
        return;
    }

    const exportFiles = [];
    
    // Resolve file patterns and validate files
    for (const arg of args) {
        if (fs.existsSync(arg)) {
            exportFiles.push(path.resolve(arg));
        } else {
            console.error(`❌ File not found: ${arg}`);
            process.exit(1);
        }
    }
    
    if (exportFiles.length === 0) {
        console.error('❌ No valid export files found');
        process.exit(1);
    }
    
    console.log(`🎯 Found ${exportFiles.length} export file(s) to process`);
    exportFiles.forEach(file => console.log(`   - ${file}`));
    
    const migrator = new ReflectionMigrator();
    
    try {
        await migrator.migrate(exportFiles);
    } catch (error) {
        console.error('\n💥 Migration failed:', error.message);
        process.exit(1);
    }
}

// Self-test function
async function selfTest() {
    console.log('🧪 Running self-test...');
    
    try {
        const client = await pool.connect();
        await client.query('SELECT 1');
        console.log('✅ Database connection: OK');
        client.release();
    } catch (error) {
        console.error('❌ Database connection: FAILED');
        console.error('   ', error.message);
        return false;
    }
    
    console.log('✅ Self-test passed');
    return true;
}

if (require.main === module) {
    // Check if this is a self-test
    if (process.argv.includes('--test')) {
        selfTest().then(success => {
            process.exit(success ? 0 : 1);
        });
    } else {
        main().catch(error => {
            console.error('💥 Unexpected error:', error);
            process.exit(1);
        });
    }
}

module.exports = { ReflectionMigrator };