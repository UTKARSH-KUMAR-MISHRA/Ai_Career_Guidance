"""
Gap Analyzer Module (backend/gap_analyzer.py)
Provides skill gap analysis and personalized learning roadmaps.
"""

def analyze_skill_gap(role_id, student_skills):
    """
    Performs skill gap analysis between student skills and target role requirements.
    """
    if isinstance(student_skills, str):
        skills_set = set([s.strip() for s in student_skills.split(",") if s.strip()])
    else:
        skills_set = set(student_skills)
        
    required = ["Python", "SQL", "Data Structures", "Machine Learning", "Git"]
    matched = list(set(required) & skills_set)
    missing = list(set(required) - skills_set)
    
    score = round((len(matched) / max(len(required), 1)) * 100, 1)
    
    return {
        "role_id": role_id,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": score
    }

def get_detailed_roadmap(role_id, duration_type="90-Day"):
    """
    Generates a phase-by-phase roadmap for a given role.
    """
    return {
        "role_id": role_id,
        "duration_type": duration_type,
        "phases": [
            {
                "phase": "Phase 1: Foundations & Core Concepts",
                "duration": "Weeks 1-3",
                "topics": ["Programming Fundamentals", "Version Control with Git", "SQL & Database Basics"]
            },
            {
                "phase": "Phase 2: Intermediate Domain Mastery",
                "duration": "Weeks 4-7",
                "topics": ["Data Structures & Algorithms", "API Integration", "Machine Learning Basics"]
            },
            {
                "phase": "Phase 3: Production Projects & Deployment",
                "duration": "Weeks 8-12",
                "topics": ["Full-Stack / AI Capstone Project", "Containerization (Docker)", "Resume & Interview Prep"]
            }
        ]
    }

class GapAnalyzer:
    def __init__(self, data_loader=None):
        self.data_loader = data_loader

    def analyze(self, role_id, current_skills, role_data=None):
        if role_data is None and self.data_loader:
            role_data = self.data_loader.get_role(role_id)
            
        if not role_data:
            return {"error": "Role not found"}
            
        required_skills = set(role_data.get("skills", []))
        current_set = set(current_skills if isinstance(current_skills, list) else [current_skills])
        missing = list(required_skills - current_set)
        matched = list(required_skills & current_set)
        
        match_percentage = round((len(matched) / max(len(required_skills), 1)) * 100, 1)
        
        return {
            "role": role_data,
            "missing_skills": missing,
            "matched_skills": matched,
            "current_skills": list(current_set),
            "match_score": match_percentage
        }
