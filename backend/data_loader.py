"""
Data Loader Module (backend/data_loader.py)
Provides structured, fast JSON data loading for roles, skills, roadmaps, and feedback datasets.
"""
import json
import os

class DataLoader:
    def __init__(self):
        base = os.path.dirname(__file__)
        data_dir = os.path.join(os.path.dirname(base), "data")
        
        self.roles = self._load_json(os.path.join(data_dir, "roles.json"))
        self.skills = self._load_json(os.path.join(data_dir, "skills.json"))
        self.roadmaps = self._load_json(os.path.join(data_dir, "roadmaps.json"))
        self.feedback = self._load_json(os.path.join(data_dir, "feedback.json"))

    def _load_json(self, path):
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except Exception:
            return []

    def get_role(self, role_id):
        return next((role for role in self.roles if role.get("id") == role_id), None)

    def get_roles_by_title(self, title):
        matches = []
        for role in self.roles:
            if title.lower() in role.get("title", "").lower():
                matches.append(role)
        return matches

    def get_roadmaps_by_role(self, role_id):
        return [r for r in self.roadmaps if r.get("role_id") == role_id]

# Singleton instance
data_loader = DataLoader()
