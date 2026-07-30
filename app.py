"""
Root Application Launcher (app.py)
Unified WSGI & Development launcher for AI Career Guidance System.
Serves both Frontend static assets & Backend Flask API.
"""
import sys
import os

# Add backend directory to Python sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(BASE_DIR, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    os.chdir(backend_dir)
except Exception:
    pass

import app as backend_app

# Expose WSGI app object for Gunicorn / Render / Railway deployment
app = backend_app.app

# Initialize DB on import if missing
try:
    backend_app.init_chat_history_db()
except Exception:
    pass

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
    from retriever import safe_print
    safe_print("\n" + "=" * 80)
    safe_print("[STARTUP] UNIFIED AI CAREER GUIDANCE PORTAL STARTED")
    safe_print("================================================================================")
    safe_print(f"[PORTAL URL] Serving Application at: http://0.0.0.0:{port}")
    safe_print("================================================================================\n")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
