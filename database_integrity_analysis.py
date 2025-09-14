#!/usr/bin/env python3
"""
Comprehensive Database Integrity Analysis for Echoes of Me
Analyzes data integrity, sync issues, and LLM export readiness
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from collections import defaultdict, Counter
import sys

# Database configuration
DATABASE_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

class DatabaseIntegrityAnalyzer:
    def __init__(self):
        self.conn = None
        self.issues = []
        self.stats = {}
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def add_issue(self, category, severity, message, count=None, details=None):
        """Add an issue to the issues list"""
        issue = {
            'category': category,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if count is not None:
            issue['affected_records'] = count
        if details:
            issue['details'] = details
        self.issues.append(issue)
    
    def analyze_schema_structure(self):
        """Analyze database schema structure"""
        print("\n🔍 ANALYZING DATABASE SCHEMA...")
        
        with self.conn.cursor() as cur:
            # Get table structure
            cur.execute("""
                SELECT table_name, column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            
            schema = defaultdict(list)
            for row in cur.fetchall():
                schema[row['table_name']].append({
                    'column': row['column_name'],
                    'type': row['data_type'],
                    'nullable': row['is_nullable'],
                    'default': row['column_default']
                })
            
            # Check for foreign key constraints
            cur.execute("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
            """)
            
            foreign_keys = cur.fetchall()
            
            # Check for indexes
            cur.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)
            
            indexes = defaultdict(list)
            for row in cur.fetchall():
                indexes[row['tablename']].append({
                    'name': row['indexname'],
                    'definition': row['indexdef']
                })
        
        self.stats['schema'] = {
            'tables': dict(schema),
            'foreign_keys': [dict(fk) for fk in foreign_keys],
            'indexes': dict(indexes)
        }
        
        # Analyze missing constraints
        expected_fks = [
            ('responses', 'user_id', 'users', 'id'),
            ('responses', 'question_id', 'questions', 'id'),
        ]
        
        actual_fks = [(fk['table_name'], fk['column_name'], fk['foreign_table_name'], fk['foreign_column_name']) 
                     for fk in foreign_keys]
        
        missing_fks = [fk for fk in expected_fks if fk not in actual_fks]
        if missing_fks:
            self.add_issue(
                'schema', 
                'HIGH', 
                f"Missing foreign key constraints: {missing_fks}",
                details={'missing_constraints': missing_fks}
            )
        
        print(f"📊 Found {len(schema)} tables, {len(foreign_keys)} foreign keys, {sum(len(idx) for idx in indexes.values())} indexes")
    
    def analyze_orphaned_records(self):
        """Check for orphaned records"""
        print("\n🔍 CHECKING FOR ORPHANED RECORDS...")
        
        with self.conn.cursor() as cur:
            # Check responses without valid users
            cur.execute("""
                SELECT COUNT(*) as orphaned_responses
                FROM responses r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE u.id IS NULL
            """)
            orphaned_users = cur.fetchone()['orphaned_responses']
            
            if orphaned_users > 0:
                self.add_issue(
                    'referential_integrity', 
                    'CRITICAL', 
                    f"Found {orphaned_users} responses with invalid user_id references"
                )
            
            # Check responses without valid questions
            cur.execute("""
                SELECT COUNT(*) as orphaned_questions, 
                       array_agg(DISTINCT r.question_id) as invalid_question_ids
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                WHERE q.id IS NULL
            """)
            result = cur.fetchone()
            orphaned_questions = result['orphaned_questions']
            invalid_ids = result['invalid_question_ids']
            
            if orphaned_questions > 0:
                self.add_issue(
                    'referential_integrity', 
                    'CRITICAL', 
                    f"Found {orphaned_questions} responses with invalid question_id references",
                    count=orphaned_questions,
                    details={'invalid_question_ids': invalid_ids}
                )
            
            # Get specific orphaned response details
            cur.execute("""
                SELECT r.id, r.user_id, r.question_id, r.created_at, u.email
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                LEFT JOIN users u ON r.user_id = u.id
                WHERE q.id IS NULL
                ORDER BY r.created_at DESC
                LIMIT 10
            """)
            orphaned_details = cur.fetchall()
            
        self.stats['orphaned_records'] = {
            'orphaned_users': orphaned_users,
            'orphaned_questions': orphaned_questions,
            'sample_orphaned_responses': [dict(row) for row in orphaned_details]
        }
        
        print(f"🚨 Found {orphaned_users} orphaned user references, {orphaned_questions} orphaned question references")
    
    def analyze_null_critical_fields(self):
        """Check for NULL values in critical fields"""
        print("\n🔍 CHECKING FOR NULL CRITICAL FIELDS...")
        
        with self.conn.cursor() as cur:
            # Check for NULL response_text
            cur.execute("SELECT COUNT(*) FROM responses WHERE response_text IS NULL OR response_text = ''")
            null_responses = cur.fetchone()[0]
            
            # Check for NULL question_text
            cur.execute("SELECT COUNT(*) FROM questions WHERE question_text IS NULL OR question_text = ''")
            null_questions = cur.fetchone()[0]
            
            # Check for NULL user emails
            cur.execute("SELECT COUNT(*) FROM users WHERE email IS NULL OR email = ''")
            null_emails = cur.fetchone()[0]
            
            # Check word count inconsistencies
            cur.execute("""
                SELECT COUNT(*) as inconsistent_count
                FROM responses 
                WHERE word_count != array_length(string_to_array(response_text, ' '), 1)
                AND response_text IS NOT NULL
                AND response_text != ''
            """)
            inconsistent_words = cur.fetchone()['inconsistent_count']
            
        if null_responses > 0:
            self.add_issue('data_quality', 'HIGH', f"Found {null_responses} responses with NULL/empty response_text")
        
        if null_questions > 0:
            self.add_issue('data_quality', 'HIGH', f"Found {null_questions} questions with NULL/empty question_text")
        
        if null_emails > 0:
            self.add_issue('data_quality', 'CRITICAL', f"Found {null_emails} users with NULL/empty email")
        
        if inconsistent_words > 0:
            self.add_issue('data_quality', 'MEDIUM', f"Found {inconsistent_words} responses with incorrect word_count")
        
        self.stats['null_fields'] = {
            'null_responses': null_responses,
            'null_questions': null_questions,
            'null_emails': null_emails,
            'inconsistent_word_counts': inconsistent_words
        }
        
        print(f"📊 NULL fields: {null_responses} responses, {null_questions} questions, {null_emails} emails")
        print(f"📊 Word count inconsistencies: {inconsistent_words}")
    
    def analyze_duplicate_entries(self):
        """Check for duplicate entries"""
        print("\n🔍 CHECKING FOR DUPLICATE ENTRIES...")
        
        with self.conn.cursor() as cur:
            # Check duplicate users by email
            cur.execute("""
                SELECT email, COUNT(*) as count
                FROM users 
                WHERE email IS NOT NULL
                GROUP BY email 
                HAVING COUNT(*) > 1
            """)
            duplicate_users = cur.fetchall()
            
            # Check duplicate questions by text
            cur.execute("""
                SELECT question_text, COUNT(*) as count, array_agg(id) as question_ids
                FROM questions 
                WHERE question_text IS NOT NULL
                GROUP BY question_text 
                HAVING COUNT(*) > 1
                LIMIT 20
            """)
            duplicate_questions = cur.fetchall()
            
            # Check duplicate responses (same user, same question)
            cur.execute("""
                SELECT user_id, question_id, COUNT(*) as count, array_agg(id) as response_ids
                FROM responses
                GROUP BY user_id, question_id
                HAVING COUNT(*) > 1
                LIMIT 20
            """)
            duplicate_responses = cur.fetchall()
        
        if duplicate_users:
            self.add_issue(
                'duplicates', 
                'HIGH', 
                f"Found {len(duplicate_users)} duplicate user emails",
                details={'duplicate_emails': [dict(row) for row in duplicate_users]}
            )
        
        if duplicate_questions:
            self.add_issue(
                'duplicates', 
                'MEDIUM', 
                f"Found {len(duplicate_questions)} duplicate question texts",
                details={'sample_duplicates': [dict(row) for row in duplicate_questions]}
            )
        
        if duplicate_responses:
            self.add_issue(
                'duplicates', 
                'HIGH', 
                f"Found {len(duplicate_responses)} duplicate user-question pairs",
                details={'sample_duplicates': [dict(row) for row in duplicate_responses]}
            )
        
        self.stats['duplicates'] = {
            'duplicate_users': len(duplicate_users),
            'duplicate_questions': len(duplicate_questions),
            'duplicate_responses': len(duplicate_responses)
        }
        
        print(f"🔄 Duplicates: {len(duplicate_users)} users, {len(duplicate_questions)} questions, {len(duplicate_responses)} responses")
    
    def analyze_json_db_sync(self):
        """Analyze synchronization between questions.json and database"""
        print("\n🔍 ANALYZING JSON-DATABASE SYNCHRONIZATION...")
        
        # Load questions.json
        try:
            with open('/home/luke/echosofme-v2/src/data/questions.json', 'r') as f:
                json_questions = json.load(f)
        except Exception as e:
            self.add_issue('sync', 'CRITICAL', f"Cannot read questions.json: {e}")
            return
        
        json_ids = set(q['id'] for q in json_questions)
        json_by_id = {q['id']: q for q in json_questions}
        
        with self.conn.cursor() as cur:
            # Get all question IDs from database
            cur.execute("SELECT id, question_text, category FROM questions")
            db_questions = cur.fetchall()
            db_ids = set(q['id'] for q in db_questions)
            db_by_id = {q['id']: q for q in db_questions}
            
            # Check which question IDs are used in responses
            cur.execute("SELECT DISTINCT question_id FROM responses")
            used_ids = set(row['question_id'] for row in cur.fetchall())
        
        # Find sync issues
        json_only = json_ids - db_ids
        db_only = db_ids - json_ids
        missing_used = used_ids - db_ids
        
        if json_only:
            self.add_issue(
                'sync', 
                'HIGH', 
                f"Found {len(json_only)} questions in JSON but not in database",
                count=len(json_only),
                details={'sample_ids': list(json_only)[:10]}
            )
        
        if db_only:
            self.add_issue(
                'sync', 
                'MEDIUM', 
                f"Found {len(db_only)} questions in database but not in JSON",
                count=len(db_only),
                details={'sample_ids': list(db_only)[:10]}
            )
        
        if missing_used:
            self.add_issue(
                'sync', 
                'CRITICAL', 
                f"Found {len(missing_used)} question IDs used in responses but missing from questions table",
                count=len(missing_used),
                details={'missing_question_ids': list(missing_used)}
            )
        
        # Check category consistency
        category_mismatches = []
        for qid in json_ids & db_ids:
            if json_by_id[qid].get('category') != db_by_id[qid]['category']:
                category_mismatches.append({
                    'id': qid,
                    'json_category': json_by_id[qid].get('category'),
                    'db_category': db_by_id[qid]['category']
                })
        
        if category_mismatches:
            self.add_issue(
                'sync',
                'MEDIUM',
                f"Found {len(category_mismatches)} questions with category mismatches between JSON and database",
                count=len(category_mismatches),
                details={'sample_mismatches': category_mismatches[:10]}
            )
        
        self.stats['sync_analysis'] = {
            'json_questions': len(json_ids),
            'db_questions': len(db_ids),
            'used_in_responses': len(used_ids),
            'json_only': len(json_only),
            'db_only': len(db_only),
            'missing_used': len(missing_used),
            'category_mismatches': len(category_mismatches)
        }
        
        print(f"🔄 Sync status: JSON={len(json_ids)}, DB={len(db_ids)}, Used={len(used_ids)}")
        print(f"🚨 Issues: {len(json_only)} JSON-only, {len(db_only)} DB-only, {len(missing_used)} missing-used")
    
    def analyze_user_data_completeness(self):
        """Analyze user data completeness for LLM export"""
        print("\n🔍 ANALYZING USER DATA COMPLETENESS...")
        
        with self.conn.cursor() as cur:
            # Get Luke's user ID
            cur.execute("SELECT id FROM users WHERE email = 'lukemoeller@yahoo.com'")
            luke_user = cur.fetchone()
            
            if not luke_user:
                self.add_issue('llm_export', 'CRITICAL', "Luke's user account not found")
                return
            
            luke_id = luke_user['id']
            
            # Analyze Luke's reflections
            cur.execute("""
                SELECT 
                    COUNT(*) as total_reflections,
                    COUNT(CASE WHEN is_draft = false THEN 1 END) as completed_reflections,
                    COUNT(CASE WHEN is_draft = true THEN 1 END) as draft_reflections,
                    SUM(word_count) as total_words,
                    AVG(word_count) as avg_words_per_reflection,
                    MIN(created_at) as first_reflection,
                    MAX(created_at) as latest_reflection,
                    COUNT(DISTINCT DATE(created_at)) as active_days
                FROM responses 
                WHERE user_id = %s
            """, (luke_id,))
            
            luke_stats = cur.fetchone()
            
            # Get category breakdown
            cur.execute("""
                SELECT q.category, COUNT(*) as count, SUM(r.word_count) as total_words
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.user_id = %s AND r.is_draft = false
                GROUP BY q.category
                ORDER BY count DESC
            """)
            
            category_breakdown = cur.fetchall()
            
            # Check for problematic reflections
            cur.execute("""
                SELECT r.id, r.question_id, r.word_count, r.created_at,
                       CASE WHEN q.id IS NULL THEN 'ORPHANED' ELSE 'OK' END as status
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
            """)
            
            all_reflections = cur.fetchall()
            problematic = [r for r in all_reflections if r['status'] == 'ORPHANED' or r['word_count'] < 10]
            
        # Assess export readiness
        total_reflections = luke_stats['total_reflections']
        completed = luke_stats['completed_reflections']
        total_words = luke_stats['total_words'] or 0
        avg_words = luke_stats['avg_words_per_reflection'] or 0
        
        export_score = 0
        export_issues = []
        
        if total_reflections >= 100:
            export_score += 25
        elif total_reflections >= 50:
            export_score += 15
        else:
            export_issues.append(f"Only {total_reflections} total reflections (recommend 100+)")
        
        if completed >= 80:
            export_score += 25
        elif completed >= 50:
            export_score += 15
        else:
            export_issues.append(f"Only {completed} completed reflections (recommend 80+)")
        
        if total_words >= 20000:
            export_score += 25
        elif total_words >= 10000:
            export_score += 15
        else:
            export_issues.append(f"Only {total_words} total words (recommend 20,000+)")
        
        if avg_words >= 150:
            export_score += 15
        elif avg_words >= 100:
            export_score += 10
        else:
            export_issues.append(f"Average {avg_words:.1f} words per reflection (recommend 150+)")
        
        if len(problematic) == 0:
            export_score += 10
        else:
            export_issues.append(f"{len(problematic)} problematic reflections found")
        
        # Risk assessment
        if export_score >= 90:
            export_risk = "LOW"
        elif export_score >= 70:
            export_risk = "MEDIUM"
        else:
            export_risk = "HIGH"
        
        if len(problematic) > 0:
            self.add_issue(
                'llm_export',
                'HIGH' if len(problematic) > 5 else 'MEDIUM',
                f"Found {len(problematic)} problematic reflections for LLM export",
                details={'problematic_reflection_ids': [r['id'] for r in problematic]}
            )
        
        if export_risk == 'HIGH':
            self.add_issue(
                'llm_export',
                'HIGH',
                f"LLM export readiness score is low ({export_score}/100)",
                details={'issues': export_issues}
            )
        
        self.stats['luke_data'] = {
            'user_id': luke_id,
            'total_reflections': total_reflections,
            'completed_reflections': completed,
            'draft_reflections': luke_stats['draft_reflections'],
            'total_words': total_words,
            'avg_words_per_reflection': round(avg_words, 1),
            'category_breakdown': [dict(row) for row in category_breakdown],
            'first_reflection': luke_stats['first_reflection'].isoformat() if luke_stats['first_reflection'] else None,
            'latest_reflection': luke_stats['latest_reflection'].isoformat() if luke_stats['latest_reflection'] else None,
            'active_days': luke_stats['active_days'],
            'export_readiness_score': export_score,
            'export_risk': export_risk,
            'export_issues': export_issues,
            'problematic_reflections': len(problematic)
        }
        
        print(f"👤 Luke's data: {total_reflections} reflections, {total_words} words, {len(category_breakdown)} categories")
        print(f"📊 Export readiness: {export_score}/100 ({export_risk} risk)")
    
    def investigate_specific_issues(self):
        """Investigate the specific issues mentioned"""
        print("\n🔍 INVESTIGATING SPECIFIC ISSUES...")
        
        with self.conn.cursor() as cur:
            # Check reflection ID 33351
            cur.execute("""
                SELECT r.id, r.user_id, r.question_id, r.response_text, r.created_at,
                       u.email, q.question_text, q.category
                FROM responses r
                LEFT JOIN users u ON r.user_id = u.id
                LEFT JOIN questions q ON r.question_id = q.id
                WHERE r.id = 33351
            """)
            
            reflection_33351 = cur.fetchone()
            
            # Check question ID 5119 usage
            cur.execute("""
                SELECT r.id, r.user_id, u.email, r.created_at
                FROM responses r
                JOIN users u ON r.user_id = u.id
                WHERE r.question_id = 5119
                ORDER BY r.created_at DESC
            """)
            
            q5119_usage = cur.fetchall()
            
            # Check if question 5119 exists in database
            cur.execute("SELECT id, question_text, category FROM questions WHERE id = 5119")
            q5119_db = cur.fetchone()
            
        if reflection_33351:
            details = {
                'reflection_id': 33351,
                'user_email': reflection_33351['email'],
                'question_id': reflection_33351['question_id'],
                'question_text': reflection_33351['question_text'],
                'question_exists': reflection_33351['question_text'] is not None,
                'response_preview': reflection_33351['response_text'][:200] + '...' if reflection_33351['response_text'] else None
            }
            
            if not reflection_33351['question_text']:
                self.add_issue(
                    'specific_investigation',
                    'HIGH',
                    f"Reflection 33351 has orphaned question_id {reflection_33351['question_id']}",
                    details=details
                )
            else:
                print(f"✅ Reflection 33351 appears to be correctly linked")
        else:
            self.add_issue(
                'specific_investigation',
                'MEDIUM',
                "Reflection ID 33351 not found in database"
            )
        
        # Question 5119 analysis
        q5119_details = {
            'question_id': 5119,
            'exists_in_db': q5119_db is not None,
            'exists_in_json': True,  # We found it in the grep earlier
            'used_in_responses': len(q5119_usage),
            'usage_details': [dict(row) for row in q5119_usage] if q5119_usage else []
        }
        
        if q5119_db:
            q5119_details.update({
                'db_question_text': q5119_db['question_text'],
                'db_category': q5119_db['category']
            })
        
        if not q5119_db and q5119_usage:
            self.add_issue(
                'specific_investigation',
                'CRITICAL',
                f"Question ID 5119 is used in {len(q5119_usage)} responses but missing from questions table",
                details=q5119_details
            )
        elif q5119_db and not q5119_usage:
            print(f"ℹ️ Question 5119 exists in database but has not been answered yet")
        elif q5119_db and q5119_usage:
            print(f"✅ Question 5119 exists and is used in {len(q5119_usage)} responses")
        
        self.stats['specific_investigations'] = {
            'reflection_33351': dict(reflection_33351) if reflection_33351 else None,
            'question_5119': q5119_details
        }
    
    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        # Critical issues first
        critical_issues = [i for i in self.issues if i['severity'] == 'CRITICAL']
        if critical_issues:
            recommendations.append({
                'priority': 'IMMEDIATE',
                'category': 'data_integrity',
                'action': 'Fix critical referential integrity issues',
                'details': 'Orphaned records must be resolved before LLM export',
                'affected_records': sum(i.get('affected_records', 0) for i in critical_issues)
            })
        
        # Sync issues
        sync_issues = [i for i in self.issues if i['category'] == 'sync']
        if sync_issues:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'synchronization',
                'action': 'Implement robust sync mechanism between JSON and database',
                'details': 'Create automated sync process with conflict resolution',
                'implementation': 'Add database migration scripts and validation checks'
            })
        
        # Schema improvements
        if any(i['category'] == 'schema' for i in self.issues):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'schema',
                'action': 'Add missing foreign key constraints and indexes',
                'details': 'Implement proper referential integrity constraints',
                'sql_required': True
            })
        
        # LLM export recommendations
        luke_data = self.stats.get('luke_data', {})
        if luke_data.get('export_risk') in ['HIGH', 'MEDIUM']:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'llm_export',
                'action': 'Improve data quality for LLM training',
                'details': f"Current score: {luke_data.get('export_readiness_score', 0)}/100",
                'specific_issues': luke_data.get('export_issues', [])
            })
        
        return recommendations
    
    def run_analysis(self):
        """Run complete analysis"""
        print("🚀 STARTING COMPREHENSIVE DATABASE INTEGRITY ANALYSIS")
        print("=" * 60)
        
        self.connect()
        
        try:
            self.analyze_schema_structure()
            self.analyze_orphaned_records()
            self.analyze_null_critical_fields()
            self.analyze_duplicate_entries()
            self.analyze_json_db_sync()
            self.analyze_user_data_completeness()
            self.investigate_specific_issues()
            
            # Generate report
            print("\n" + "=" * 60)
            print("📊 ANALYSIS SUMMARY")
            print("=" * 60)
            
            # Issue summary
            severity_counts = Counter(i['severity'] for i in self.issues)
            print(f"\n🚨 ISSUES FOUND:")
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    print(f"  {severity}: {count}")
            
            if not self.issues:
                print("  ✅ No issues found!")
            
            # Key statistics
            print(f"\n📈 KEY STATISTICS:")
            print(f"  Database tables: {len(self.stats['schema']['tables'])}")
            print(f"  Foreign keys: {len(self.stats['schema']['foreign_keys'])}")
            print(f"  Luke's reflections: {self.stats['luke_data']['total_reflections']}")
            print(f"  Luke's total words: {self.stats['luke_data']['total_words']}")
            print(f"  Export readiness: {self.stats['luke_data']['export_readiness_score']}/100 ({self.stats['luke_data']['export_risk']} risk)")
            
            # Recommendations
            recommendations = self.generate_recommendations()
            if recommendations:
                print(f"\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. [{rec['priority']}] {rec['action']}")
                    print(f"     {rec['details']}")
            
            # Save detailed report
            report = {
                'analysis_timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_issues': len(self.issues),
                    'critical_issues': len([i for i in self.issues if i['severity'] == 'CRITICAL']),
                    'high_issues': len([i for i in self.issues if i['severity'] == 'HIGH']),
                    'export_readiness_score': self.stats['luke_data']['export_readiness_score'],
                    'export_risk': self.stats['luke_data']['export_risk']
                },
                'issues': self.issues,
                'statistics': self.stats,
                'recommendations': recommendations
            }
            
            with open('/home/luke/echosofme-v2/database_integrity_report.json', 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"\n💾 Detailed report saved to: database_integrity_report.json")
            
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    analyzer = DatabaseIntegrityAnalyzer()
    analyzer.run_analysis()