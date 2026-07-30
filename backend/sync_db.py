import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join("data", "career_guidance.db")
CSV_DIR = os.path.join("data", "temp_cleaned")

# Map CSV filename to database table name
TABLE_MAPPING = {
    "branch_role_mapping": "branch_role_mapping",
    "career_comparison": "career_comparison",
    "career_faq": "career_faq",
    "certifications": "certifications",
    "courses": "courses",
    "industry_trends": "industry_trends",
    "interview_questions": "interview_questions",
    "learning_resources": "learning_resources",
    "projects": "projects",
    "resume_checklist": "resume_checklist",
    "roadmap": "roadmap",
    "roles": "roles",
    "role_skill_mapping": "role_skill_mapping",
    "skills": "skills",
    "soft_skills": "soft_skills",
    "student_profiles": "student_profiles"
}

def sync_data():
    # If currently in backend folder, navigate up
    db_path = DB_PATH
    csv_dir = CSV_DIR
    if not os.path.exists("data") and os.path.exists(os.path.join("..", "data")):
        db_path = os.path.join("..", db_path)
        csv_dir = os.path.join("..", csv_dir)
        
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {os.path.abspath(db_path)}")
        return
        
    conn = sqlite3.connect(db_path)
    print(f"Connected to database: {os.path.abspath(db_path)}")
    cursor = conn.cursor()
    
    for csv_name, table_name in TABLE_MAPPING.items():
        csv_path = os.path.join(csv_dir, f"{csv_name}.csv")
        if not os.path.exists(csv_path):
            print(f"Warning: CSV file {csv_path} not found. Skipping...")
            continue
            
        print(f"Syncing table '{table_name}' from {csv_name}.csv...")
        try:
            df = pd.read_csv(csv_path)
            
            # Clear existing table data
            cursor.execute(f"DELETE FROM {table_name}")
            
            # Write new data
            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Successfully synced {len(df)} rows into '{table_name}'.")
        except Exception as e:
            print(f"Error syncing {table_name}: {e}")
            
    conn.commit()
    conn.close()
    print("Database sync complete!")

if __name__ == "__main__":
    sync_data()
