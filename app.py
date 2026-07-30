"""
Root Application Launcher (app.py)
Unified launcher for AI Career Guidance System.
Executes backend/app.py to serve both Frontend & Backend on http://localhost:5000
"""
import sys
import os

# Add backend directory to Python sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

if __name__ == "__main__":
    import app as backend_app
    backend_app.init_chat_history_db()
    
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
        with open(backend_app.ACTIVE_PROFILE_PATH, 'w', encoding='utf-8') as f:
            import json
            json.dump(default_student, f, indent=2)
            
    from retriever import safe_print
    safe_print("\n" + "=" * 80)
    safe_print("[STARTUP] UNIFIED AI CAREER GUIDANCE PORTAL STARTED")
    safe_print("================================================================================")
    safe_print("[PORTAL URL] Serving Unified Application (Frontend + Backend) at: http://localhost:5000")
    safe_print("[LOGGING] All Requests, API Calls, & Terminal RAG Logs active in this window.")
    safe_print("================================================================ drop\n")
    
    import webbrowser, threading, time
    def auto_open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open("http://localhost:5000")
        except Exception:
            pass
            
    threading.Thread(target=auto_open_browser, daemon=True).start()
    backend_app.app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
