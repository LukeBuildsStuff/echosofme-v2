#!/usr/bin/env python3
"""
LLM Export Preparation Script for Echoes of Me
Prepares and validates user data for LLM training dataset creation
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import sys
import re
from collections import defaultdict, Counter

# Database configuration
DATABASE_CONFIG = {
    'host': 'host.docker.internal',
    'database': 'echosofme_dev',
    'user': 'echosofme',
    'password': 'secure_dev_password',
    'port': 5432
}

class LLMExportPreparator:
    def __init__(self, user_email="lukemoeller@yahoo.com"):
        self.conn = None
        self.user_email = user_email
        self.user_id = None
        self.export_data = []
        self.quality_issues = []
        self.export_stats = {}
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def get_user_info(self):
        """Get user information"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM users WHERE email = %s", (self.user_email,))
            user = cur.fetchone()
            
            if not user:
                print(f"❌ User not found: {self.user_email}")
                sys.exit(1)
            
            self.user_id = user['id']
            print(f"📧 Found user: {user['name']} ({user['email']})")
            return dict(user)
    
    def analyze_text_quality(self, text):
        """Analyze text quality for LLM training"""
        if not text or not text.strip():
            return {'score': 0, 'issues': ['empty_text']}
        
        issues = []
        score = 100
        
        # Length checks
        word_count = len(text.split())
        if word_count < 10:
            issues.append('too_short')
            score -= 30
        elif word_count < 50:
            issues.append('short')
            score -= 10
        
        # Content quality checks
        if text.count('.') == 0 and text.count('!') == 0 and text.count('?') == 0:
            issues.append('no_sentences')
            score -= 20
        
        # Check for repetitive patterns
        words = text.lower().split()
        if len(set(words)) / len(words) < 0.3:  # Less than 30% unique words
            issues.append('repetitive')
            score -= 15
        
        # Check for extremely long sentences
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        if avg_sentence_length > 50:
            issues.append('overly_long_sentences')
            score -= 10
        
        # Check for coherence indicators
        coherence_indicators = ['because', 'therefore', 'however', 'although', 'since', 'while', 'but', 'and', 'or']
        coherence_count = sum(1 for word in coherence_indicators if word in text.lower())
        if coherence_count == 0 and word_count > 20:
            issues.append('lacks_coherence_indicators')
            score -= 10
        
        return {'score': max(0, score), 'issues': issues}
    
    def load_training_data(self):
        """Load and prepare training data"""
        print("\n📚 LOADING USER REFLECTIONS FOR LLM TRAINING...")
        
        with self.conn.cursor() as cur:
            # Get all user reflections with question context
            cur.execute("""
                SELECT 
                    r.id,
                    r.question_id,
                    r.response_text,
                    r.word_count,
                    r.is_draft,
                    r.created_at,
                    r.updated_at,
                    q.question_text,
                    q.category,
                    q.subcategory,
                    CASE 
                        WHEN q.id IS NULL THEN 'ORPHANED'
                        WHEN r.response_text IS NULL OR r.response_text = '' THEN 'EMPTY'
                        ELSE 'OK'
                    END as status
                FROM responses r
                LEFT JOIN questions q ON r.question_id = q.id
                WHERE r.user_id = %s
                ORDER BY r.created_at ASC
            """, (self.user_id,))
            
            raw_reflections = cur.fetchall()
        
        print(f"📊 Found {len(raw_reflections)} total reflections")
        
        # Process each reflection
        valid_reflections = 0
        total_words = 0
        category_counts = defaultdict(int)
        quality_scores = []
        
        for reflection in raw_reflections:
            reflection_dict = dict(reflection)
            
            # Skip drafts and problematic entries
            if reflection_dict['is_draft']:
                self.quality_issues.append({
                    'id': reflection_dict['id'],
                    'issue': 'draft_entry',
                    'severity': 'medium'
                })
                continue
            
            if reflection_dict['status'] == 'ORPHANED':
                self.quality_issues.append({
                    'id': reflection_dict['id'],
                    'issue': 'orphaned_question',
                    'question_id': reflection_dict['question_id'],
                    'severity': 'high'
                })
                continue
            
            if reflection_dict['status'] == 'EMPTY':
                self.quality_issues.append({
                    'id': reflection_dict['id'],
                    'issue': 'empty_response',
                    'severity': 'high'
                })
                continue
            
            # Analyze text quality
            quality_analysis = self.analyze_text_quality(reflection_dict['response_text'])
            quality_scores.append(quality_analysis['score'])
            
            if quality_analysis['score'] < 50:
                self.quality_issues.append({
                    'id': reflection_dict['id'],
                    'issue': 'low_quality_text',
                    'score': quality_analysis['score'],
                    'issues': quality_analysis['issues'],
                    'severity': 'medium'
                })
            
            # Create training example
            training_example = {
                'id': reflection_dict['id'],
                'question': reflection_dict['question_text'],
                'response': reflection_dict['response_text'],
                'category': reflection_dict['category'],
                'subcategory': reflection_dict['subcategory'],
                'word_count': reflection_dict['word_count'],
                'quality_score': quality_analysis['score'],
                'created_at': reflection_dict['created_at'].isoformat(),
                'metadata': {
                    'question_id': reflection_dict['question_id'],
                    'response_id': reflection_dict['id'],
                    'quality_issues': quality_analysis['issues']
                }
            }
            
            self.export_data.append(training_example)
            valid_reflections += 1
            total_words += reflection_dict['word_count'] or 0
            category_counts[reflection_dict['category']] += 1
        
        # Calculate statistics
        self.export_stats = {
            'total_reflections': len(raw_reflections),
            'valid_for_training': valid_reflections,
            'excluded_reflections': len(raw_reflections) - valid_reflections,
            'total_words': total_words,
            'average_words_per_reflection': total_words / max(valid_reflections, 1),
            'average_quality_score': sum(quality_scores) / max(len(quality_scores), 1),
            'category_distribution': dict(category_counts),
            'quality_issues_count': len(self.quality_issues),
            'date_range': {
                'first': min(r['created_at'] for r in self.export_data).isoformat() if self.export_data else None,
                'last': max(r['created_at'] for r in self.export_data).isoformat() if self.export_data else None
            }
        }
        
        print(f"✅ Prepared {valid_reflections} reflections for LLM training")
        print(f"📊 Total words: {total_words:,}")
        print(f"📊 Average quality score: {self.export_stats['average_quality_score']:.1f}/100")
        
        return self.export_data
    
    def assess_training_readiness(self):
        """Assess readiness for LLM training"""
        print("\n🎯 ASSESSING LLM TRAINING READINESS...")
        
        readiness_score = 0
        recommendations = []
        
        # Quantity assessment
        valid_count = self.export_stats['valid_for_training']
        if valid_count >= 150:
            readiness_score += 30
        elif valid_count >= 100:
            readiness_score += 25
            recommendations.append("Consider adding more reflections for better training diversity")
        elif valid_count >= 50:
            readiness_score += 15
            recommendations.append("Minimum viable dataset - strongly recommend adding more content")
        else:
            readiness_score += 5
            recommendations.append("CRITICAL: Too few reflections for effective training")
        
        # Word count assessment
        total_words = self.export_stats['total_words']
        if total_words >= 30000:
            readiness_score += 25
        elif total_words >= 20000:
            readiness_score += 20
            recommendations.append("Good word count - could benefit from more detailed responses")
        elif total_words >= 10000:
            readiness_score += 15
            recommendations.append("Moderate word count - encourage longer, more detailed responses")
        else:
            readiness_score += 5
            recommendations.append("CRITICAL: Insufficient word count for effective training")
        
        # Quality assessment
        avg_quality = self.export_stats['average_quality_score']
        if avg_quality >= 80:
            readiness_score += 20
        elif avg_quality >= 70:
            readiness_score += 15
            recommendations.append("Good quality - review low-quality entries for improvement")
        elif avg_quality >= 60:
            readiness_score += 10
            recommendations.append("Moderate quality - consider improving response depth and coherence")
        else:
            readiness_score += 5
            recommendations.append("CRITICAL: Quality issues need addressing before training")
        
        # Diversity assessment
        categories = len(self.export_stats['category_distribution'])
        if categories >= 8:
            readiness_score += 15
        elif categories >= 5:
            readiness_score += 12
            recommendations.append("Good category diversity - consider expanding into more areas")
        elif categories >= 3:
            readiness_score += 8
            recommendations.append("Limited category diversity - expand into more topic areas")
        else:
            readiness_score += 3
            recommendations.append("CRITICAL: Very limited topic diversity")
        
        # Data integrity assessment
        quality_issues = self.export_stats['quality_issues_count']
        if quality_issues == 0:
            readiness_score += 10
        elif quality_issues <= 5:
            readiness_score += 8
            recommendations.append("Minor data integrity issues - review and fix if possible")
        elif quality_issues <= 15:
            readiness_score += 5
            recommendations.append("Moderate data issues - recommend fixing before training")
        else:
            readiness_score += 2
            recommendations.append("CRITICAL: Significant data integrity issues need resolution")
        
        # Risk assessment
        if readiness_score >= 90:
            risk_level = "LOW"
            overall_recommendation = "Excellent dataset - ready for high-quality LLM training"
        elif readiness_score >= 75:
            risk_level = "MEDIUM-LOW"
            overall_recommendation = "Good dataset - minor improvements would enhance training quality"
        elif readiness_score >= 60:
            risk_level = "MEDIUM"
            overall_recommendation = "Viable dataset - several improvements recommended before training"
        elif readiness_score >= 45:
            risk_level = "MEDIUM-HIGH"
            overall_recommendation = "Marginal dataset - significant improvements needed for quality training"
        else:
            risk_level = "HIGH"
            overall_recommendation = "Poor dataset - major improvements required before attempting training"
        
        assessment = {
            'readiness_score': readiness_score,
            'risk_level': risk_level,
            'overall_recommendation': overall_recommendation,
            'specific_recommendations': recommendations,
            'assessment_breakdown': {
                'quantity_score': min(30, (valid_count / 150) * 30),
                'word_count_score': min(25, (total_words / 30000) * 25),
                'quality_score': (avg_quality / 100) * 20,
                'diversity_score': min(15, (categories / 8) * 15),
                'integrity_score': max(0, 10 - quality_issues)
            }
        }
        
        print(f"🎯 Training Readiness Score: {readiness_score}/100")
        print(f"⚠️ Risk Level: {risk_level}")
        print(f"💡 Overall: {overall_recommendation}")
        
        return assessment
    
    def create_training_dataset(self, output_format='jsonl'):
        """Create the actual training dataset file"""
        print(f"\n📁 CREATING TRAINING DATASET ({output_format.upper()})...")
        
        if not self.export_data:
            print("❌ No valid training data available")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format == 'jsonl':
            # JSONL format - each line is a JSON object
            filename = f'/home/luke/echosofme-v2/luke_echo_training_data_{timestamp}.jsonl'
            
            with open(filename, 'w') as f:
                for example in self.export_data:
                    # Format for instruction-following fine-tuning
                    training_record = {
                        'instruction': f"You are Luke Moeller's digital Echo. Answer this reflection question as Luke would, based on his personality, experiences, and perspective: {example['question']}",
                        'input': "",
                        'output': example['response'],
                        'metadata': {
                            'category': example['category'],
                            'word_count': example['word_count'],
                            'quality_score': example['quality_score'],
                            'created_at': example['created_at'],
                            'source_id': example['id']
                        }
                    }
                    f.write(json.dumps(training_record) + '\n')
        
        elif output_format == 'chat':
            # ChatML format for conversation fine-tuning
            filename = f'/home/luke/echosofme-v2/luke_echo_chat_data_{timestamp}.jsonl'
            
            with open(filename, 'w') as f:
                for example in self.export_data:
                    chat_record = {
                        'messages': [
                            {
                                'role': 'user',
                                'content': example['question']
                            },
                            {
                                'role': 'assistant', 
                                'content': example['response']
                            }
                        ],
                        'metadata': example['metadata']
                    }
                    f.write(json.dumps(chat_record) + '\n')
        
        elif output_format == 'alpaca':
            # Alpaca format
            filename = f'/home/luke/echosofme-v2/luke_echo_alpaca_data_{timestamp}.json'
            
            alpaca_data = []
            for example in self.export_data:
                alpaca_record = {
                    'instruction': "Answer this personal reflection question as Luke Moeller would answer it.",
                    'input': example['question'],
                    'output': example['response'],
                    'metadata': example['metadata']
                }
                alpaca_data.append(alpaca_record)
            
            with open(filename, 'w') as f:
                json.dump(alpaca_data, f, indent=2, default=str)
        
        print(f"💾 Training dataset saved: {filename}")
        print(f"📊 Dataset contains {len(self.export_data)} training examples")
        
        return filename
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive export report"""
        print("\n📋 GENERATING COMPREHENSIVE REPORT...")
        
        assessment = self.assess_training_readiness()
        
        report = {
            'export_timestamp': datetime.now().isoformat(),
            'user_email': self.user_email,
            'user_id': self.user_id,
            'dataset_statistics': self.export_stats,
            'training_readiness': assessment,
            'quality_issues': {
                'total_issues': len(self.quality_issues),
                'issues_by_severity': {
                    'high': len([i for i in self.quality_issues if i['severity'] == 'high']),
                    'medium': len([i for i in self.quality_issues if i['severity'] == 'medium']),
                    'low': len([i for i in self.quality_issues if i['severity'] == 'low'])
                },
                'detailed_issues': self.quality_issues
            },
            'recommendations': {
                'immediate_actions': [],
                'quality_improvements': [],
                'dataset_expansion': []
            }
        }
        
        # Generate specific recommendations
        if assessment['readiness_score'] < 60:
            report['recommendations']['immediate_actions'].extend([
                'Address critical data integrity issues',
                'Expand dataset before attempting training',
                'Review and improve low-quality responses'
            ])
        
        if self.export_stats['average_quality_score'] < 70:
            report['recommendations']['quality_improvements'].extend([
                'Encourage more detailed, thoughtful responses',
                'Add coherence indicators to responses',
                'Review responses flagged as low quality'
            ])
        
        if self.export_stats['valid_for_training'] < 100:
            report['recommendations']['dataset_expansion'].extend([
                f"Add {100 - self.export_stats['valid_for_training']} more quality reflections",
                'Expand into underrepresented categories',
                'Aim for 20,000+ total words'
            ])
        
        # Save report
        report_filename = f'/home/luke/echosofme-v2/luke_echo_export_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"💾 Comprehensive report saved: {report_filename}")
        return report
    
    def run_export_preparation(self):
        """Run complete export preparation process"""
        print("🚀 STARTING LLM EXPORT PREPARATION")
        print("=" * 60)
        
        self.connect()
        
        try:
            # Get user info
            user_info = self.get_user_info()
            
            # Load and prepare training data
            self.load_training_data()
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report()
            
            # Create training datasets in multiple formats
            print(f"\n📁 CREATING TRAINING DATASETS...")
            jsonl_file = self.create_training_dataset('jsonl')
            chat_file = self.create_training_dataset('chat')
            alpaca_file = self.create_training_dataset('alpaca')
            
            # Final summary
            print("\n" + "=" * 60)
            print("🎉 EXPORT PREPARATION COMPLETE")
            print("=" * 60)
            
            print(f"\n📊 DATASET SUMMARY:")
            print(f"  User: {user_info['name']} ({user_info['email']})")
            print(f"  Valid reflections: {self.export_stats['valid_for_training']}")
            print(f"  Total words: {self.export_stats['total_words']:,}")
            print(f"  Categories covered: {len(self.export_stats['category_distribution'])}")
            print(f"  Quality score: {self.export_stats['average_quality_score']:.1f}/100")
            print(f"  Training readiness: {report['training_readiness']['readiness_score']}/100 ({report['training_readiness']['risk_level']} risk)")
            
            print(f"\n📁 FILES CREATED:")
            if jsonl_file:
                print(f"  - Instruction format: {jsonl_file}")
            if chat_file:
                print(f"  - Chat format: {chat_file}")
            if alpaca_file:
                print(f"  - Alpaca format: {alpaca_file}")
            
            if report['training_readiness']['risk_level'] in ['HIGH', 'MEDIUM-HIGH']:
                print(f"\n⚠️  WARNING: {report['training_readiness']['overall_recommendation']}")
                print("   Review the detailed report before proceeding with training.")
            else:
                print(f"\n✅ SUCCESS: Dataset is ready for LLM training!")
            
        finally:
            if self.conn:
                self.conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare user data for LLM training')
    parser.add_argument('--user-email', default='lukemoeller@yahoo.com', help='User email to export data for')
    args = parser.parse_args()
    
    preparator = LLMExportPreparator(user_email=args.user_email)
    preparator.run_export_preparation()