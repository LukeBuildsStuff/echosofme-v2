#!/usr/bin/env python3
"""
Export all dating_experiences questions to CSV file
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import csv
import os
from datetime import datetime

def get_db_connection():
    return psycopg2.connect(
        host='host.docker.internal',
        database='echosofme_dev',
        user='echosofme',
        password='secure_dev_password',
        port=5432
    )

def export_dating_questions():
    """Export all dating_experiences questions to CSV"""
    print("📊 Exporting dating_experiences questions to CSV...")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all dating questions
            cur.execute("""
                SELECT id, question_text, category
                FROM questions
                WHERE category = 'dating_experiences'
                ORDER BY id ASC
            """)

            questions = cur.fetchall()
            print(f"✅ Found {len(questions)} dating_experiences questions")

            # Create CSV file path - Windows Downloads folder from WSL
            windows_username = "Luke"  # Your Windows username
            csv_path = f"/mnt/c/Users/{windows_username}/Downloads/dating_questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            # Write to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'question_text', 'category']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for question in questions:
                    writer.writerow({
                        'id': question['id'],
                        'question_text': question['question_text'],
                        'category': question['category']
                    })

            print(f"💾 CSV exported successfully to:")
            print(f"   {csv_path}")
            print(f"\n📁 Windows path:")
            print(f"   C:\\Users\\{windows_username}\\Downloads\\{os.path.basename(csv_path)}")

            # Print summary
            print(f"\n📈 Summary:")
            print(f"   Total questions: {len(questions)}")

            # Count unique questions
            unique_texts = set(q['question_text'] for q in questions)
            print(f"   Unique questions: {len(unique_texts)}")

            if len(unique_texts) < len(questions):
                print(f"   ⚠️ Warning: Found {len(questions) - len(unique_texts)} duplicate questions")
            else:
                print(f"   ✨ All questions are unique!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_dating_questions()