import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "career_guidance.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_skill_gap(normalized_student, target_role_id):
    """
    Analyzes missing skills and fetches target courses, projects, and certifications.
    Returns:
        {
            'role_id': str,
            'role_name': str,
            'missing_skills': list of dicts,
            'matching_skills': list of dicts,
            'recommended_courses': list of dicts,
            'recommended_projects': list of dicts,
            'recommended_certifications': list of dicts,
            'study_timeline': {
                'total_hours': int,
                'days_required': int,
                'weeks_required': int,
                'timeline_summary': str
            }
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = {
        'role_id': target_role_id,
        'role_name': '',
        'missing_skills': [],
        'matching_skills': [],
        'recommended_courses': [],
        'recommended_projects': [],
        'recommended_certifications': [],
        'study_timeline': {}
    }
    
    try:
        # Get target role name
        cursor.execute("SELECT role_name FROM roles WHERE role_id = ?", (target_role_id,))
        role_row = cursor.fetchone()
        if not role_row:
            return result
        result['role_name'] = role_row['role_name']
        
        # 1. Map skills (already matching vs missing)
        # Query role-skill mappings joined with skill info
        cursor.execute("""
            SELECT rsm.skill_id, s.skill_name, s.skill_category, s.difficulty_level, s.estimated_learning_hours, rsm.importance, rsm.mandatory
            FROM role_skill_mapping rsm
            JOIN skills s ON rsm.skill_id = s.skill_id
            WHERE rsm.role_id = ?
        """, (target_role_id,))
        role_skills = cursor.fetchall()
        
        student_skill_ids = set(normalized_student['known_skills_ids'])
        student_skill_names_lower = {s.lower().strip() for s in normalized_student['known_skills_names']}
        
        missing_skill_ids = []
        
        for rs in role_skills:
            skill_id = rs['skill_id']
            skill_name = rs['skill_name']
            
            has_skill = (skill_id in student_skill_ids) or (skill_name.lower().strip() in student_skill_names_lower)
            
            skill_info = {
                'skill_id': skill_id,
                'skill_name': skill_name,
                'category': rs['skill_category'],
                'difficulty': rs['difficulty_level'],
                'learning_hours': rs['estimated_learning_hours'],
                'importance': rs['importance'],
                'mandatory': rs['mandatory']
            }
            
            if has_skill:
                result['matching_skills'].append(skill_info)
            else:
                result['missing_skills'].append(skill_info)
                missing_skill_ids.append(skill_id)
                
        # 2. Get Recommended Courses for the missing skills
        if missing_skill_ids:
            # Format list of skill ids for SQL
            placeholders = ",".join(["?"] * len(missing_skill_ids))
            query_courses = f"""
                SELECT course_id, course_name, platform, provider, difficulty, duration_hours, rating, skill_id, course_url
                FROM courses
                WHERE role_id = ? AND skill_id IN ({placeholders})
                ORDER BY rating DESC LIMIT 5
            """
            cursor.execute(query_courses, [target_role_id] + missing_skill_ids)
            result['recommended_courses'] = [dict(row) for row in cursor.fetchall()]
        
        # If not enough courses, fetch any courses for this role
        if len(result['recommended_courses']) < 3:
            cursor.execute("""
                SELECT course_id, course_name, platform, provider, difficulty, duration_hours, rating, skill_id, course_url
                FROM courses
                WHERE role_id = ?
                ORDER BY rating DESC LIMIT 5
            """, (target_role_id,))
            result['recommended_courses'] = [dict(row) for row in cursor.fetchall()]
            
        # 3. Get Recommended Projects addressing missing skills
        if missing_skill_ids:
            query_projects = """
                SELECT project_id, project_name, project_domain, difficulty, estimated_duration, description, required_skills, portfolio_value
                FROM projects
                WHERE related_role = ?
                LIMIT 5
            """
            cursor.execute(query_projects, (target_role_id,))
            all_projects = cursor.fetchall()
            
            recommended_projects = []
            for p in all_projects:
                req_skills = [s.strip() for s in str(p['required_skills']).split(',') if s.strip()]
                # Check if this project requires any of the missing skills
                overlap = set(req_skills).intersection(set(missing_skill_ids))
                if overlap:
                    recommended_projects.append(dict(p))
            result['recommended_projects'] = recommended_projects
            
        if not result['recommended_projects']:
            # Fallback
            cursor.execute("SELECT * FROM projects WHERE related_role = ? LIMIT 3", (target_role_id,))
            result['recommended_projects'] = [dict(row) for row in cursor.fetchall()]
            
        # 4. Get Recommended Certifications
        cursor.execute("""
            SELECT cert_id as certification_id, certificate_name as certification_name, provider, exam_fee as cost, difficulty as difficulty_level, 'https://example.com/cert' as url
            FROM certifications
            WHERE related_role = ?
            LIMIT 3
        """, (target_role_id,))
        result['recommended_certifications'] = [dict(row) for row in cursor.fetchall()]
        
        # 5. Study Timeline calculations
        # Sum estimated learning hours for missing skills
        total_hours = sum([int(s['learning_hours']) for s in result['missing_skills']])
        
        # If no missing skills, set a nominal baseline to review advanced concepts
        if total_hours == 0:
            total_hours = 20 # 20 hours review
            
        daily_hours = max(1, normalized_student['daily_learning_hours'])
        days_required = int(total_hours / daily_hours)
        weeks_required = max(1, int(days_required / 7))
        
        timeline_summary = (
            f"Based on your target role '{result['role_name']}', you have a skill gap of {len(result['missing_skills'])} skills. "
            f"To bridge this gap, you require approximately {total_hours} hours of study. "
            f"At your pace of {daily_hours} hours/day, you will be job-ready in about {days_required} days ({weeks_required} weeks)."
        )
        
        result['study_timeline'] = {
            'total_hours': total_hours,
            'days_required': days_required,
            'weeks_required': weeks_required,
            'timeline_summary': timeline_summary
        }
        
    except Exception as e:
        print(f"Error analyzing skill gap: {e}")
    finally:
        conn.close()
        
    return result

def get_detailed_roadmap(target_role_id, roadmap_type='90-Day', normalized_student=None):
    """
    Pulls the week-by-week roadmap and annotates it with student progress.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    roadmap_steps = []
    
    try:
        # Load roadmap steps
        cursor.execute("""
            SELECT r.*, s.skill_name, c.course_name, c.platform as course_platform, p.project_name
            FROM roadmap r
            LEFT JOIN skills s ON r.skill_id = s.skill_id
            LEFT JOIN courses c ON r.course_id = c.course_id
            LEFT JOIN projects p ON r.project_id = p.project_id
            WHERE r.role_id = ? AND r.roadmap_type = ?
            ORDER BY r.week_number
        """, (target_role_id, roadmap_type))
        rows = cursor.fetchall()
        
        student_skill_ids = set()
        student_skill_names_lower = set()
        
        if normalized_student:
            student_skill_ids = set(normalized_student['known_skills_ids'])
            student_skill_names_lower = {s.lower().strip() for s in normalized_student['known_skills_names']}
            
        for row in rows:
            step = dict(row)
            skill_id = step['skill_id']
            skill_name = step['skill_name']
            
            # Mapped status
            status = 'Todo'
            if skill_id:
                if skill_id in student_skill_ids or (skill_name and skill_name.lower().strip() in student_skill_names_lower):
                    status = 'Completed'
                    
            step['status'] = status
            
            # Mapped timeline scaling
            est_hours = step['estimated_hours'] or 10
            if normalized_student:
                daily = normalized_student['daily_learning_hours'] or 2
                step['days_estimate'] = max(1, round(est_hours / daily, 1))
            else:
                step['days_estimate'] = round(est_hours / 2, 1)
                
            roadmap_steps.append(step)
            
    except Exception as e:
        print(f"Error fetching detailed roadmap: {e}")
    finally:
        conn.close()
        
    return roadmap_steps

if __name__ == "__main__":
    # Test gap analysis
    test_stu = {
        'known_skills_ids': ['SK001', 'SK002'], # Python, Java
        'known_skills_names': ['Python', 'Java'],
        'daily_learning_hours': 3
    }
    gap = analyze_skill_gap(test_stu, "ROLE001")
    print("Gap Analysis for ROLE001 (Data Scientist):")
    print(f"Missing skills count: {len(gap['missing_skills'])}")
    print(f"Timeline: {gap['study_timeline']['timeline_summary']}")
    print(f"Recommended course count: {len(gap['recommended_courses'])}")
    
    roadmap = get_detailed_roadmap("ROLE001", "30-Day", test_stu)
    print(f"\nDetailed Roadmap week 1 sample: {roadmap[0] if roadmap else 'None'}")
