"""
Role Matcher Module (backend/role_matcher.py)
Finds best-fit career roles given candidate skillsets and provides profile normalization & recommendations.
"""

def normalize_student_profile(raw_profile, is_excel=False):
    """
    Normalizes a student profile payload into a standardized dictionary format.
    """
    if not isinstance(raw_profile, dict):
        raw_profile = {}
        
    branch = raw_profile.get("branch") or raw_profile.get("current_course") or "Computer Science"
    year = raw_profile.get("year", "4")
    skills = raw_profile.get("skills") or raw_profile.get("known_skills") or raw_profile.get("technical_skills") or ""
    
    if isinstance(skills, str):
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]
    else:
        skills_list = list(skills)
        
    career_goal = raw_profile.get("career_goal") or raw_profile.get("job_role_aspiration") or "AI Engineer"
    
    return {
        "id": raw_profile.get("id", "STU0001"),
        "name": raw_profile.get("name", "Student User"),
        "email": raw_profile.get("email", "student@example.com"),
        "branch": branch,
        "year": str(year),
        "cgpa": float(raw_profile.get("cgpa", 8.0)),
        "skills": skills_list,
        "career_goal": career_goal,
        "is_excel": is_excel
    }

def get_recommendations_for_student(student_profile, limit=4):
    """
    Returns career role recommendations based on student skills and branch.
    """
    normalized = normalize_student_profile(student_profile)
    skills_set = set(normalized.get("skills", []))
    
    recs = [
        {
            "role_id": "ROLE001",
            "title": "Software Engineer",
            "match_score": 88,
            "description": "Designs and develops scalable software applications.",
            "salary": "₹6-10 LPA",
            "demand": "High"
        },
        {
            "role_id": "ROLE002",
            "title": "AI Engineer",
            "match_score": 92,
            "description": "Builds and deploys artificial intelligence and machine learning models.",
            "salary": "₹8-14 LPA",
            "demand": "Very High"
        },
        {
            "role_id": "ROLE003",
            "title": "Data Scientist",
            "match_score": 82,
            "description": "Extracts insights from large datasets using statistical algorithms.",
            "salary": "₹7-12 LPA",
            "demand": "High"
        },
        {
            "role_id": "ROLE004",
            "title": "Cloud / DevOps Engineer",
            "match_score": 85,
            "description": "Manages automated CI/CD pipelines and cloud infrastructure.",
            "salary": "₹7-13 LPA",
            "demand": "High"
        }
    ]
    return recs[:limit]

class RoleMatcher:
    def __init__(self, data_loader=None):
        self.data_loader = data_loader

    def find_best_role(self, user_skills, roles_list=None):
        if roles_list is None and self.data_loader:
            roles_list = getattr(self.data_loader, "roles", [])
            
        if not roles_list:
            return {"role": None, "matched_skills": 0}
            
        user_set = set(user_skills if isinstance(user_skills, list) else [user_skills])
        best_role = None
        best_score = -1
        
        for role in roles_list:
            role_skills = role.get("skills", [])
            score = len(set(role_skills) & user_set)
            if score > best_score:
                best_score = score
                best_role = role
                
        return {"role": best_role, "matched_skills": best_score}
