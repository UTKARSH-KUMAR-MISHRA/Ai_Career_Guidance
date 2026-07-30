"""
Root Application Launcher (app.py)
Unified WSGI & Development launcher for AI Career Guidance System.
Serves both Frontend static assets & Backend Flask API.
"""
import sys
import os
import importlib.util

# Set base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(BASE_DIR, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    os.chdir(backend_dir)
except Exception:
    pass

# Dynamically import backend/app.py as backend_app_module to prevent circular import name collisions
backend_app_path = os.path.join(backend_dir, "app.py")
spec = importlib.util.spec_from_file_location("backend_app_module", backend_app_path)
backend_app = importlib.util.module_from_spec(spec)
sys.modules["backend_app_module"] = backend_app
spec.loader.exec_module(backend_app)

# Expose WSGI app object for Gunicorn / Render / Railway deployment
app = backend_app.app

# Initialize DB on import if missing
try:
    backend_app.init_chat_history_db()
except Exception as e:
    print(f"[WARN] DB init warning: {e}")

if __name__ == "__main__":
    if not os.path.exists(backend_app.ACTIVE_PROFILE_PATH):
        default_student = {
            "student_id": "STU0001",
            "branch": "Computer Science",
            "year": 3,
            "cgpa": 8.12,
            "known_skills": "SK001, SK006, SK008",
            "preferred_role": "ROLE001",
            "daily_learning_hours": 3,
            "is_excel": False
        }
        try:
            with open(backend_app.ACTIVE_PROFILE_PATH, 'w', encoding='utf-8') as f:
                import json
                json.dump(default_student, f, indent=2)
        except Exception:
            pass

    port = int(os.environ.get("PORT", 5000))
    print(f"\n================================================================================")
    print(f"[STARTUP] UNIFIED AI CAREER GUIDANCE PORTAL STARTED AT http://0.0.0.0:{port}")
    print(f"================================================================ drop\n")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
