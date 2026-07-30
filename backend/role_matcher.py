import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "career_guidance.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_student_profile(profile_data, is_excel=False):
    """
    Normalizes both Excel-style and CSV-style student profile dictionaries into a standard structure.
    Returns:
        {
            'name': str,
            'branch': str,  # normalized to CSE, ECE, ME, CE, AE
            'year': int,    # 1 to 4
            'cgpa': float,
            'known_skills_ids': list of str,
            'known_skills_names': list of str,
            'career_goal': str, # role_name or role_id
            'daily_learning_hours': int
        }
    """
    normalized = {
        'name': 'Student',
        'branch': 'CSE',
        'year': 3,
        'cgpa': 8.0,
        'known_skills_ids': [],
        'known_skills_names': [],
        'career_goal': '',
        'daily_learning_hours': 2
    }
    
    conn = get_db_connection()
    
    try:
        # Load all skills mapping from DB for name <-> id conversion
        cursor = conn.cursor()
        cursor.execute("SELECT skill_id, skill_name FROM skills")
        skills_db = {row['skill_name'].lower().strip(): row['skill_id'] for row in cursor.fetchall()}
        
        cursor.execute("SELECT skill_id, skill_name FROM skills")
        skills_id_to_name = {row['skill_id']: row['skill_name'] for row in cursor.fetchall()}
        
        if is_excel:
            normalized['name'] = profile_data.get('name', 'Student')
            
            # Normalize branch
            course = str(profile_data.get('current_course', 'B.Tech')).upper()
            asp_role = str(profile_data.get('job_role_aspiration', ''))
            
            # Map Excel columns
            year_str = str(profile_data.get('year', '3rd Year'))
            year_match = [int(s) for s in year_str.split() if s.isdigit()]
            normalized['year'] = year_match[0] if year_match else 3
            
            # CGPA/Rating mapping
            coding_rating = profile_data.get('coding_rating', 3)
            # Map coding rating (1-5) to fake CGPA for scaling (e.g. rating 4 -> CGPA 8.0)
            normalized['cgpa'] = float(coding_rating) * 2.0
            
            normalized['daily_learning_hours'] = 3 # Default for excel profiles
            normalized['career_goal'] = asp_role
            
            # Gather skill names from 'technical_skills', 'programming_languages' and 'soft_skills'
            raw_tech = str(profile_data.get('technical_skills', ''))
            raw_prog = str(profile_data.get('programming_languages', ''))
            raw_soft = str(profile_data.get('soft_skills', ''))
            
            all_raw_skills = []
            for raw in [raw_tech, raw_prog, raw_soft]:
                if raw and raw != 'nan':
                    all_raw_skills.extend([s.strip().lower() for s in raw.split(',') if s.strip()])
            
            # Resolve skill names to IDs
            known_ids = []
            known_names = []
            for s_name in all_raw_skills:
                if s_name in skills_db:
                    known_ids.append(skills_db[s_name])
                    known_names.append(skills_id_to_name[skills_db[s_name]])
                else:
                    known_names.append(s_name.title())
                    
            normalized['known_skills_ids'] = list(set(known_ids))
            normalized['known_skills_names'] = list(set(known_names))
            
            # Guess branch from aspiration role or skills
            # Default branch mapping based on roles
            branch_guess = 'CSE'
            asp_lower = asp_role.lower()
            if any(x in asp_lower for x in ['vlsi', 'embedded', 'telecom', 'signal', 'hardware']):
                branch_guess = 'ECE'
            elif any(x in asp_lower for x in ['robotics', 'cad', 'mechanical', 'hvac', 'design', 'automotive']):
                branch_guess = 'ME'
            elif any(x in asp_lower for x in ['structure', 'civil', 'transportation', 'geotechnical', 'urban']):
                branch_guess = 'CE'
            elif any(x in asp_lower for x in ['propulsion', 'aerospace', 'avionics', 'aircraft', 'space']):
                branch_guess = 'AE'
            normalized['branch'] = branch_guess
            
        else:
            # CSV Profile format
            normalized['name'] = f"Student {profile_data.get('student_id', 'STU001')}"
            
            # Branch mapping mapping
            raw_branch = str(profile_data.get('branch', 'CSE'))
            # Normalize branch codes
            if 'computer' in raw_branch.lower() or 'information' in raw_branch.lower() or 'it' in raw_branch.lower() or 'cse' in raw_branch.lower() or 'ds' in raw_branch.lower():
                normalized['branch'] = 'CSE'
            elif 'electronics' in raw_branch.lower() or 'ece' in raw_branch.lower():
                normalized['branch'] = 'ECE'
            elif 'mechanical' in raw_branch.lower() or 'me' in raw_branch.lower():
                normalized['branch'] = 'ME'
            elif 'civil' in raw_branch.lower() or 'ce' in raw_branch.lower():
                normalized['branch'] = 'CE'
            elif 'aerospace' in raw_branch.lower() or 'ae' in raw_branch.lower():
                normalized['branch'] = 'AE'
            else:
                normalized['branch'] = raw_branch
                
            normalized['year'] = int(profile_data.get('year', 3))
            normalized['cgpa'] = float(profile_data.get('cgpa', 8.0))
            normalized['daily_learning_hours'] = int(profile_data.get('daily_learning_hours', 2))
            
            # Resolve career goal
            pref_role = profile_data.get('preferred_role', '')
            goal = profile_data.get('career_goal', '')
            normalized['career_goal'] = goal if goal else pref_role
            
            # Ingest skill IDs
            known_ids_str = str(profile_data.get('known_skills', ''))
            known_ids = [s.strip() for s in known_ids_str.split(',') if s.strip()]
            
            known_names = []
            for s_id in known_ids:
                if s_id in skills_id_to_name:
                    known_names.append(skills_id_to_name[s_id])
                    
            normalized['known_skills_ids'] = known_ids
            normalized['known_skills_names'] = known_names
            
    except Exception as e:
        print(f"Error normalising student profile: {e}")
    finally:
        conn.close()
        
    return normalized

def calculate_role_match_score(normalized_student, role_id):
    """
    Returns:
        {
            'match_score': int,
            'matching_skills': list of dict,
            'missing_skills': list of dict,
            'is_advanced': bool,
            'explanation': str
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    result = {
        'match_score': 0,
        'matching_skills': [],
        'missing_skills': [],
        'is_advanced': False,
        'explanation': ''
    }
    
    try:
        # Get target role details
        cursor.execute("SELECT * FROM roles WHERE role_id = ?", (role_id,))
        role = cursor.fetchone()
        if not role:
            return result
            
        role_name = role['role_name']
        difficulty = role['difficulty_level']
        
        # Determine if too advanced
        # If student is in year 1/2 and role is Advanced, flag it
        if normalized_student['year'] <= 2 and difficulty.lower() == 'advanced':
            result['is_advanced'] = True
            
        # Get skill mappings for this role
        cursor.execute("""
            SELECT rsm.skill_id, s.skill_name, s.skill_category, rsm.importance, rsm.mandatory, rsm.minimum_proficiency
            FROM role_skill_mapping rsm
            JOIN skills s ON rsm.skill_id = s.skill_id
            WHERE rsm.role_id = ?
        """, (role_id,))
        required_skills = cursor.fetchall()
        
        # Calculate scores
        total_weight = 0
        earned_weight = 0
        
        student_skill_ids = set(normalized_student['known_skills_ids'])
        # Also check name matching just in case
        student_skill_names_lower = {s.lower().strip() for s in normalized_student['known_skills_names']}
        
        for req in required_skills:
            skill_id = req['skill_id']
            skill_name = req['skill_name']
            importance = req['importance']
            mandatory = req['mandatory']
            
            # Score weight
            weight = 1
            if mandatory == 'Yes' or importance.lower() == 'high':
                weight = 3
            elif importance.lower() == 'medium':
                weight = 2
                
            total_weight += weight
            
            has_skill = (skill_id in student_skill_ids) or (skill_name.lower().strip() in student_skill_names_lower)
            
            skill_info = {
                'skill_id': skill_id,
                'skill_name': skill_name,
                'category': req['skill_category'],
                'importance': importance,
                'mandatory': mandatory,
                'min_proficiency': req['minimum_proficiency']
            }
            
            if has_skill:
                earned_weight += weight
                result['matching_skills'].append(skill_info)
            else:
                result['missing_skills'].append(skill_info)
                # If a mandatory skill is missing, also weight towards advanced if match score gets impacted
                if mandatory == 'Yes' and difficulty.lower() == 'advanced':
                    # Potentially advanced if student lacks core mandatory requirements
                    pass

        # Percentage calculation
        match_percentage = 0
        if total_weight > 0:
            match_percentage = int((earned_weight / total_weight) * 100)
        else:
            match_percentage = 50 # Default baseline
            
        # Adjust score with branch alignment
        # Check if this role is mapped to student's branch
        cursor.execute("""
            SELECT priority, recommended 
            FROM branch_role_mapping 
            WHERE role_id = ? AND branch_code = ?
        """, (role_id, normalized_student['branch']))
        mapping = cursor.fetchone()
        
        branch_aligned = False
        if mapping:
            branch_aligned = True
            # Small boosts for branch recommendation alignment
            if mapping['recommended'] == 'Yes':
                match_percentage = min(100, match_percentage + 5)
            if mapping['priority'] == 'High':
                match_percentage = min(100, match_percentage + 5)
        else:
            # Penalty for non-branch role
            match_percentage = max(10, match_percentage - 10)
            
        result['match_score'] = match_percentage
        
        # Recalculate is_advanced based on score thresholds too
        if match_percentage < 45 and difficulty.lower() == 'advanced':
            result['is_advanced'] = True
            
        # Create user-friendly explanation
        matching_count = len(result['matching_skills'])
        required_count = len(required_skills)
        missing_mandatory = [s['skill_name'] for s in result['missing_skills'] if s['mandatory'] == 'Yes']
        
        explanation = f"You possess {matching_count} out of {required_count} required skills for {role_name}. "
        if branch_aligned:
            explanation += f"This role strongly aligns with your {normalized_student['branch']} curriculum. "
        else:
            explanation += f"Note that this role is outside your core {normalized_student['student_id'] if 'student_id' in normalized_student else normalized_student['branch']} branch requirements. "
            
        if missing_mandatory:
            explanation += f"Core missing skills to acquire: {', '.join(missing_mandatory[:3])}."
        else:
            explanation += "You have all the mandatory core prerequisite skills!"
            
        result['explanation'] = explanation
        
    except Exception as e:
        print(f"Error calculating match score: {e}")
    finally:
        conn.close()
        
    return result

def get_recommendations_for_student(normalized_student, limit=6):
    """
    Returns list of role recommendations sorted by match score.
    Includes alternate roles if the target role is too advanced.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    recommendations = []
    
    try:
        # Load all roles
        cursor.execute("SELECT role_id, role_name, role_family, difficulty_level, salary_range, future_scope FROM roles")
        all_roles = cursor.fetchall()
        
        for r in all_roles:
            role_id = r['role_id']
            score_data = calculate_role_match_score(normalized_student, role_id)
            
            recommendations.append({
                'role_id': role_id,
                'role_name': r['role_name'],
                'role_family': r['role_family'],
                'difficulty': r['difficulty_level'],
                'salary_range': r['salary_range'],
                'future_scope': r['future_scope'],
                'match_score': score_data['match_score'],
                'is_advanced': score_data['is_advanced'],
                'explanation': score_data['explanation'],
                'matching_skills': score_data['matching_skills'],
                'missing_skills': score_data['missing_skills']
            })
            
        # Sort by match score descending
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Inject alternate/bridge role recommendations logic
        # If the student's top matching role is marked as advanced, recommend an entry-level bridge role in the same family
        final_list = []
        for rec in recommendations[:limit]:
            if rec['is_advanced']:
                # Find an entry/intermediate role in the same family with lower difficulty
                cursor.execute("""
                    SELECT role_id FROM roles 
                    WHERE role_family = ? AND difficulty_level IN ('Entry', 'Intermediate') 
                    ORDER BY difficulty_level DESC LIMIT 1
                """, (rec['role_family'],))
                alt = cursor.fetchone()
                if alt and alt['role_id'] != rec['role_id']:
                    # Find its details
                    alt_id = alt['role_id']
                    # Check if alternate is already in the list; if not, link it as a bridge!
                    rec['bridge_role_suggestion'] = alt_id
            final_list.append(rec)
            
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
    finally:
        conn.close()
        
    return final_list

if __name__ == "__main__":
    # Test normalization and scoring
    test_stu = {
        "student_id": "STU001",
        "branch": "Civil",
        "year": 2,
        "cgpa": 7.5,
        "known_skills": "SK001, SK002", # Python, Java
        "preferred_role": "ROLE001", # Data Scientist
        "daily_learning_hours": 2
    }
    norm = normalize_student_profile(test_stu)
    print("Normalized student:", norm)
    
    score = calculate_role_match_score(norm, "ROLE001")
    print("\nMatch score for ROLE001 (Data Scientist):", score['match_score'])
    print("Explanation:", score['explanation'])
    print("Is Advanced:", score['is_advanced'])
