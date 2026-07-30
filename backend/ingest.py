import os
import shutil
import sqlite3
import pandas as pd
import json

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
TEMP_ZIP_DIR = os.path.join(BASE_DIR, "temp_files_zip")
EXCEL_PATH = r"D:\career guidance ai\Final_Updated_DMA_DATASET_Indian_Names (1).xlsx"
DB_PATH = os.path.join(DATA_DIR, "career_guidance.db")

def main():
    print("Starting Ingestion Pipeline...")
    
    # 1. Create directories
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    print(f"Directories verified: {DATA_DIR}, {DOCS_DIR}")
    
    # 2. Copy markdown documents from D:\career guidance ai
    src_branch_md = r"D:\career guidance ai\career-paths-by-branch.md"
    src_interview_md = r"D:\career guidance ai\interview_Q.md"
    
    dest_roles_md = os.path.join(DOCS_DIR, "role_descriptions.md")
    dest_interview_md = os.path.join(DOCS_DIR, "interview_tips.md")
    dest_guide_md = os.path.join(DOCS_DIR, "career_guide.md")
    
    if os.path.exists(src_branch_md):
        shutil.copy2(src_branch_md, dest_roles_md)
        print(f"Copied {src_branch_md} -> {dest_roles_md}")
    else:
        print(f"Warning: {src_branch_md} not found!")
        
    if os.path.exists(src_interview_md):
        shutil.copy2(src_interview_md, dest_interview_md)
        print(f"Copied {src_interview_md} -> {dest_interview_md}")
    else:
        print(f"Warning: {src_interview_md} not found!")
        
    # Write a default career guide file if empty
    with open(dest_guide_md, "w", encoding="utf-8") as f:
        f.write("# Engineering Career Guide\n\nWelcome to the Career Guidance Assistant. This guide contains curated articles on choosing engineering branches, preparing for placements, mapping core skills, and preparing for HR and technical interviews.")
    print("Created career_guide.md")

    # 3. Create/Connect SQLite database
    print(f"Connecting to SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 4. Ingest Clean CSV Files from temp_files_zip
    csv_files = [
        "roles.csv", "skills.csv", "branch_role_mapping.csv", 
        "learning_resources.csv", "courses.csv", "projects.csv", 
        "roadmap.csv", "role_skill_mapping.csv", "soft_skills.csv", 
        "student_profiles.csv", "certifications.csv", "career_comparison.csv", 
        "career_faq.csv", "industry_trends.csv", "resume_checklist.csv",
        "interview_questions.csv"
    ]
    
    for csv_file in csv_files:
        csv_path = os.path.join(DATA_DIR, "temp_cleaned", csv_file)
        if not os.path.exists(csv_path):
            csv_path = os.path.join(TEMP_ZIP_DIR, csv_file)
        if not os.path.exists(csv_path):
            csv_path = os.path.join(r"D:\data", csv_file)
            
        if os.path.exists(csv_path):
            table_name = os.path.splitext(csv_file)[0]
            print(f"Ingesting CSV: {csv_file} -> Table: {table_name}")
            try:
                # Read with utf-8-sig to handle byte order mark (BOM) and special characters
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"  Successfully loaded {len(df)} rows into '{table_name}'")
            except Exception as e:
                print(f"  Error loading {csv_file}: {e}")
        else:
            print(f"Warning: CSV file not found: {csv_file}")
            
    # 5. Ingest Excel Student Profiles
    if os.path.exists(EXCEL_PATH):
        print(f"Ingesting Excel profiles from: {EXCEL_PATH}")
        try:
            df_excel = pd.read_excel(EXCEL_PATH)
            # Rename columns to avoid dot notations and clarify names
            df_excel.rename(columns={
                'rating': 'coding_rating',
                'rating.1': 'soft_skill_rating'
            }, inplace=True)
            df_excel.to_sql("excel_student_profiles", conn, if_exists='replace', index=False)
            print(f"  Successfully loaded {len(df_excel)} rows into 'excel_student_profiles'")
        except Exception as e:
            print(f"  Error loading Excel: {e}")
    else:
        print(f"Warning: Excel file not found at {EXCEL_PATH}")
        
    conn.commit()
    conn.close()
    print("Database Ingestion Completed successfully!")

    # 6. Generate schema metadata dictionary data/metadata_dictionary.json
    metadata = {
        "database_name": "career_guidance.db",
        "description": "Main database storing role schemas, student profiles, skill maps, roadmaps, and course listings.",
        "tables": {
            "roles": {
                "description": "Job roles descriptions, difficulty, and salaries.",
                "columns": ["role_id", "role_name", "role_family", "description", "difficulty_level", "average_learning_time", "entry_level", "salary_range", "future_scope", "required_degree", "work_mode", "roadmap_available"]
            },
            "skills": {
                "description": "Technical and core engineering skills repository.",
                "columns": ["skill_id", "skill_name", "skill_category", "skill_type", "difficulty_level", "estimated_learning_hours", "prerequisite_skill", "industry_demand", "description", "certification_available"]
            },
            "branch_role_mapping": {
                "description": "Maps engineering branches (CSE, ECE, ME, CE, etc.) to target career roles.",
                "columns": ["mapping_id", "branch_name", "branch_code", "role_id", "role_name", "priority", "recommended", "bridge_skills", "higher_studies_option", "career_path", "industry", "notes"]
            },
            "learning_resources": {
                "description": "Reference materials, books, and articles indexed by skill and role.",
                "columns": ["resource_id", "resource_name", "resource_type", "platform", "topic", "difficulty", "language", "duration", "free_paid", "skill_id", "role_id", "url"]
            },
            "courses": {
                "description": "Online courses from Coursera, Udemy, etc., mapped to skills.",
                "columns": ["course_id", "course_name", "platform", "provider", "difficulty", "duration_hours", "language", "certificate", "price", "rating", "skill_id", "role_id", "course_url"]
            },
            "projects": {
                "description": "Practical projects for students to build up portfolios, mapped to skills.",
                "columns": ["project_id", "project_name", "project_domain", "difficulty", "estimated_duration", "description", "required_skills", "github_available", "dataset_required", "portfolio_value", "related_role"]
            },
            "roadmap": {
                "description": "Weekly task roadmaps (30/60/90 days) mapped to specific roles and resources.",
                "columns": ["roadmap_id", "role_id", "roadmap_type", "week_number", "day_range", "topic", "skill_id", "course_id", "project_id", "milestone", "estimated_hours"]
            },
            "role_skill_mapping": {
                "description": "Detailed skill requirements and proficiency targets for each role.",
                "columns": ["mapping_id", "role_id", "skill_id", "importance", "minimum_proficiency", "mandatory", "recommended_learning_order"]
            },
            "soft_skills": {
                "description": "Interpersonal and workplace soft skills details.",
                "columns": ["soft_skill_id", "skill_name", "category", "description", "importance", "recommended_roles", "assessment_method", "improvement_resources", "practice_activity", "industry_relevance"]
            },
            "student_profiles": {
                "description": "Synthesized student profile templates representing branches, skills, and goals.",
                "columns": ["student_id", "branch", "year", "cgpa", "known_skills", "projects_completed", "internship_status", "preferred_domain", "preferred_role", "coding_level", "communication_level", "english_level", "daily_learning_hours", "career_goal"]
            },
            "excel_student_profiles": {
                "description": "Student profile data with Indian names loaded from Excel sheet.",
                "columns": ["name", "email_id", "year", "current_course", "technical_skills", "programming_languages", "coding_rating", "soft_skills", "soft_skill_rating", "projects", "job_role_aspiration", "challenges_faced", "career_support_needed", "preferred_learning_method"]
            },
            "certifications": {
                "description": "Professional certifications mapped to roles and skills.",
                "columns": ["cert_id", "certificate_name", "provider", "difficulty", "duration", "exam_fee", "validity", "skills_covered", "recognized_by_industry", "related_role"]
            },
            "career_comparison": {
                "description": "Direct comparison parameters between pairs of roles.",
                "columns": ["comparison_id", "role_1_id", "role_1_name", "role_2_id", "role_2_name", "comparison_category", "role_1_details", "role_2_details", "verdict"]
            },
            "career_faq": {
                "description": "Common questions and answers regarding branches, job trends, and skilling.",
                "columns": ["faq_id", "question", "answer", "category", "related_role", "related_skill", "difficulty", "keywords"]
            },
            "industry_trends": {
                "description": "Market demand, hiring outlook, and salary levels for different roles.",
                "columns": ["trend_id", "role_id", "industry", "technology", "trend_title", "trend_description", "hiring_demand", "future_growth", "automation_risk", "average_salary_india_lpa", "average_salary_global_usd", "top_companies", "required_skills", "recommended_certifications", "remote_opportunities", "experience_level", "job_openings_estimate", "market_outlook", "last_updated"]
            },
            "resume_checklist": {
                "description": "Actionable ATS-friendly resume checkpoints for different positions.",
                "columns": ["checklist_id", "role_id", "role_name", "section", "item", "importance", "description", "common_mistakes", "ats_required", "fresher_required", "experienced_required", "example"]
            }
        }
    }
    
    with open(os.path.join(DATA_DIR, "metadata_dictionary.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print("Created metadata_dictionary.json")

if __name__ == "__main__":
    main()
