import os
import json
import sqlite3
import re
import time
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from pypdf import PdfReader

from role_matcher import normalize_student_profile, get_recommendations_for_student
from gap_analyzer import analyze_skill_gap, get_detailed_roadmap
import adaptive_rag
from retriever import safe_print

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "frontend"))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))
DB_PATH = os.path.join(DATA_DIR, "career_guidance.db")
ACTIVE_PROFILE_PATH = os.path.join(DATA_DIR, "active_student.json")
FEEDBACK_PATH = os.path.join(DATA_DIR, "feedback.json")

# Initialize Flask with frontend static folder
app = Flask(__name__, static_folder=FRONTEND_DIR)
# Real-Time Terminal Visibility Middleware for all incoming Frontend Requests & API Calls
@app.before_request
def log_frontend_request():
    if request.path.startswith('/static') or any(request.path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.ico', '.woff2']):
        return
    safe_print("\n" + "►"*85)
    safe_print(f"[FRONTEND REQUEST RECEIVED] {request.method} {request.path}")
    safe_print(f"  - Client IP: {request.remote_addr}")
    if request.is_json and request.json:
        safe_print(f"  - JSON Payload: {json.dumps(request.json, ensure_ascii=False)[:300]}")
    elif request.args:
        safe_print(f"  - Query Args: {dict(request.args)}")
    safe_print("►"*85)

@app.after_request
def log_frontend_response(response):
    if request.path.startswith('/static') or any(request.path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.ico', '.woff2']):
        return response
    safe_print(f"[FRONTEND RESPONSE SENT] {request.method} {request.path} -> Status Code: {response.status_code}\n")
    return response

# Unified Frontend Static Serving Routes
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Helper to initialize the SQLite conversation history table
def init_chat_history_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating chat_history table: {e}")
    finally:
        conn.close()

# Helper to read recent chat history for a student
def get_user_chat_history(email, limit=6):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT role, content FROM chat_history 
            WHERE email = ? 
            ORDER BY timestamp DESC LIMIT ?
        """, (email, limit))
        rows = cursor.fetchall()
        # Order chronologically
        history = [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
        return history
    except Exception as e:
        print(f"Error reading chat history: {e}")
        return []
    finally:
        conn.close()

# Helper to log messages to the chat history
def log_chat_message(email, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO chat_history (email, role, content) 
            VALUES (?, ?, ?)
        """, (email, role, content))
        conn.commit()
    except Exception as e:
        print(f"Error logging chat message: {e}")
    finally:
        conn.close()

# Helper to map skill names to database skill IDs
def map_profile_names_to_ids(skills_str):
    if not skills_str:
        return ""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT skill_id, skill_name FROM skills")
    skills_map = {row['skill_name'].lower().strip(): row['skill_id'] for row in cursor.fetchall()}
    conn.close()
    
    ids = []
    for s in skills_str.split(','):
        s_clean = s.strip().lower()
        if s_clean in skills_map:
            ids.append(skills_map[s_clean])
    return ", ".join(ids)

# Helper: Get currently active student profile
def get_active_student_profile():
    # Try fetching profile for authenticated user first using the header X-User-Email
    user_email = request.headers.get('X-User-Email')
    if user_email:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE email = ?", (user_email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            profile = dict(row)
            # Map skills to IDs
            skills_ids_str = map_profile_names_to_ids(profile.get('skills', ''))
            
            mapped_profile = {
                "student_id": profile.get("email"),
                "name": profile.get("name"),
                "email": profile.get("email"),
                "phone": profile.get("phone"),
                "college": profile.get("college"),
                "university": profile.get("university"),
                "degree": profile.get("degree"),
                "branch": profile.get("branch", "Computer Science"),
                "year": int(profile.get("year_of_study") or 3),
                "known_skills": skills_ids_str,
                "interests": profile.get("interests"),
                "preferred_role": profile.get("career_goal", "ROLE001"),
                "career_goal": profile.get("career_goal"),
                "preferred_industry": profile.get("preferred_industry"),
                "resume_path": profile.get("resume_path"),
                "photo_path": profile.get("photo_path"),
                "cgpa": 8.0, # default fallback
                "is_excel": False
            }
            return mapped_profile

    # Fallback to file-based active student profile
    if os.path.exists(ACTIVE_PROFILE_PATH):
        try:
            with open(ACTIVE_PROFILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading active student file: {e}")
            
    # Default fallback: return first CSV profile
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_profiles LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        profile = dict(row)
        profile['is_excel'] = False
        return profile
    return {}

# ==========================================
# AUTHENTICATION & PROFILE SETUP ENDPOINTS
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Full name is required', 'field': 'name'}), 400
    if not email:
        return jsonify({'error': 'Email is required', 'field': 'email'}), 400
    if not password:
        return jsonify({'error': 'Password is required', 'field': 'password'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'An account with this email already exists', 'field': 'email'}), 400
            
        password_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
                       (email, password_hash, name))
        conn.commit()
        return jsonify({
            'status': 'success', 
            'message': 'User registered successfully',
            'user': {
                'email': email,
                'name': name,
                'is_profile_setup': False
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
            
        is_setup = bool(user['is_profile_setup'])
        
        return jsonify({
            'status': 'success',
            'user': {
                'email': user['email'],
                'name': user['name'],
                'is_profile_setup': is_setup
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/auth/session', methods=['GET'])
def check_session():
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return jsonify({'authenticated': False}), 200
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email, name, is_profile_setup FROM users WHERE email = ?", (user_email,))
        user = cursor.fetchone()
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'email': user['email'],
                    'name': user['name'],
                    'is_profile_setup': bool(user['is_profile_setup'])
                }
            }), 200
        return jsonify({'authenticated': False}), 200
    except Exception:
        return jsonify({'authenticated': False}), 200
    finally:
        conn.close()

@app.route('/api/profile/setup', methods=['POST'])
def profile_setup():
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return jsonify({'error': 'Authentication required. Missing X-User-Email header'}), 401
        
    data = request.json or {}
    name = data.get('name')
    phone = data.get('phone')
    college = data.get('college')
    university = data.get('university')
    degree = data.get('degree')
    branch = data.get('branch')
    year_of_study = data.get('year_of_study')
    skills = data.get('skills', '')
    interests = data.get('interests', '')
    career_goal = data.get('career_goal')
    preferred_industry = data.get('preferred_industry')
    resume_path = data.get('resume_path')
    photo_path = data.get('photo_path')
    
    if isinstance(skills, list):
        skills = ", ".join(skills)
    if isinstance(interests, list):
        interests = ", ".join(interests)
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM user_profiles WHERE email = ?", (user_email,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE user_profiles SET 
                    name=?, phone=?, college=?, university=?, degree=?, branch=?, 
                    year_of_study=?, skills=?, interests=?, career_goal=?, 
                    preferred_industry=?, resume_path=?, photo_path=?, last_updated=CURRENT_TIMESTAMP
                WHERE email=?
            """, (name, phone, college, university, degree, branch, year_of_study, skills, interests, career_goal, preferred_industry, resume_path, photo_path, user_email))
        else:
            cursor.execute("""
                INSERT INTO user_profiles (
                    email, name, phone, college, university, degree, branch, 
                    year_of_study, skills, interests, career_goal, preferred_industry, 
                    resume_path, photo_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_email, name, phone, college, university, degree, branch, year_of_study, skills, interests, career_goal, preferred_industry, resume_path, photo_path))
            
        cursor.execute("UPDATE users SET is_profile_setup = 1 WHERE email = ?", (user_email,))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Profile setup completed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# ==========================================
# RESUME PARSING & ANALYSIS ENDPOINT
# ==========================================

@app.route('/api/resume/analyze', methods=['POST'])
def analyze_resume():
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return jsonify({'error': 'Authentication required. Missing X-User-Email header'}), 401
        
    role_id = request.form.get('role_id', 'ROLE001')
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    temp_dir = os.path.join(BASE_DIR, "data", "temp_resumes")
    os.makedirs(temp_dir, exist_ok=True)
    filename = f"{user_email.replace('@', '_').replace('.', '_')}_{int(time.time())}_{file.filename}"
    file_path = os.path.join(temp_dir, filename)
    file.save(file_path)
    
    text = ""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext == '.pdf':
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            print(f"Standard PDF reading failed: {e}. Will attempt Sarvam Vision API fallback.")
            
        # Fallback to Sarvam Vision if standard extraction yielded no text (scanned PDF)
        if len(text.strip()) < 100:
            print("PDF appears to be scanned or contains minimal selectable text. Calling Sarvam Vision API...")
            try:
                from sarvam_client import SarvamClient
                client = SarvamClient()
                digitized_text = client.digitize_document(file_path, output_format="md")
                if digitized_text:
                    text = digitized_text
                    print(f"Sarvam Vision successfully parsed scanned PDF ({len(text)} characters).")
            except Exception as vision_err:
                print(f"Sarvam Vision fallback failed: {vision_err}")
    elif ext in ['.png', '.jpg', '.jpeg']:
        print("Image upload detected. Calling Sarvam Vision API...")
        try:
            from sarvam_client import SarvamClient
            client = SarvamClient()
            digitized_text = client.digitize_document(file_path, output_format="md")
            if digitized_text:
                text = digitized_text
                print(f"Sarvam Vision successfully parsed image resume ({len(text)} characters).")
        except Exception as vision_err:
            print(f"Sarvam Vision image parsing failed: {vision_err}")
    else:
        try:
            text = file.read().decode('utf-8', errors='ignore')
        except Exception as e:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
                
    if not text.strip():
        return jsonify({'error': 'Could not extract text from the resume file. Please upload a valid PDF, Image or Text file.'}), 400

    clean_text = text.lower()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT skill_id, skill_name, skill_category FROM skills")
    all_skills = [dict(row) for row in cursor.fetchall()]
    
    matched_skills = []
    for s in all_skills:
        name = s['skill_name'].lower().strip()
        if name in clean_text:
            matched_skills.append(s)
            
    matched_skill_ids = [s['skill_id'] for s in matched_skills]
    matched_skill_names = [s['skill_name'] for s in matched_skills]
    
    cursor.execute("""
        SELECT s.skill_id, s.skill_name, m.mandatory, m.importance 
        FROM role_skill_mapping m 
        JOIN skills s ON m.skill_id = s.skill_id 
        WHERE m.role_id = ?
    """, (role_id,))
    role_requirements = [dict(row) for row in cursor.fetchall()]
    
    mandatory_reqs = [r for r in role_requirements if str(r['mandatory']).strip().lower() in ('yes', '1')]
    recommended_reqs = [r for r in role_requirements if str(r['mandatory']).strip().lower() in ('no', '0')]
    
    missing_mandatory = []
    matched_mandatory = []
    for r in mandatory_reqs:
        if r['skill_id'] in matched_skill_ids:
            matched_mandatory.append(r)
        else:
            missing_mandatory.append(r)
            
    missing_recommended = []
    matched_recommended = []
    for r in recommended_reqs:
        if r['skill_id'] in matched_skill_ids:
            matched_recommended.append(r)
        else:
            missing_recommended.append(r)
            
    score = 55
    
    if mandatory_reqs:
        score += int((len(matched_mandatory) / len(mandatory_reqs)) * 25)
    else:
        score += 25
        
    if recommended_reqs:
        score += int((len(matched_recommended) / len(recommended_reqs)) * 15)
    else:
        score += 15
        
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', clean_text)
    phone_match = re.search(r'[\+\d\s\(\)-]{10,20}', clean_text)
    
    if email_match: score += 2
    if phone_match: score += 2
    if any(k in clean_text for k in ['education', 'college', 'university', 'btech', 'b.tech', 'degree']):
        score += 3
    if any(k in clean_text for k in ['experience', 'project', 'internship', 'work', 'publication']):
        score += 3
        
    score = min(max(score, 30), 98)
    
    suggestions = []
    if not email_match or not phone_match:
        suggestions.append("Ensure your contact details (Email, Phone) are clearly visible at the top.")
    if not any(k in clean_text for k in ['project', 'github', 'link']):
        suggestions.append("Add links to your portfolio or GitHub repositories to showcase practical coding work.")
        
    if missing_mandatory:
        suggestions.append(f"Critical: You are missing core mandatory skills for this role: {', '.join([s['skill_name'] for s in missing_mandatory[:3]])}. Add coursework or projects covering these.")
    if missing_recommended:
        suggestions.append(f"Recommended: Consider learning {', '.join([s['skill_name'] for s in missing_recommended[:3]])} to improve your candidacy.")
        
    if len(matched_skills) < 5:
        suggestions.append("Explicitly list more of your technical skills in a dedicated section to help ATS scanners index your profile.")
        
    recommended_courses = []
    if missing_mandatory or missing_recommended:
        missing_ids = [s['skill_id'] for s in missing_mandatory + missing_recommended][:4]
        if missing_ids:
            placeholders = ','.join(['?'] * len(missing_ids))
            cursor.execute(f"""
                SELECT course_id, course_name, platform, provider, rating, course_url, skill_id
                FROM courses
                WHERE skill_id IN ({placeholders})
                LIMIT 6
            """, missing_ids)
            recommended_courses = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    
    return jsonify({
        'ats_score': score,
        'matched_skills': matched_skill_names[:15],
        'missing_skills': {
            'mandatory': [s['skill_name'] for s in missing_mandatory],
            'recommended': [s['skill_name'] for s in missing_recommended]
        },
        'parsed_details': {
            'email': email_match.group(0) if email_match else None,
            'phone': phone_match.group(0).strip() if phone_match else None
        },
        'suggestions': suggestions,
        'recommended_courses': recommended_courses
    })

# 1. API: List all students for student switcher
@app.route('/api/students', methods=['GET'])
def list_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    students_list = []
    
    try:
        # Load CSV students
        cursor.execute("SELECT student_id, branch, year, cgpa, career_goal FROM student_profiles LIMIT 10")
        csv_rows = cursor.fetchall()
        for r in csv_rows:
            students_list.append({
                'id': r['student_id'],
                'name': f"Template Profile {r['student_id']}",
                'branch': r['branch'],
                'year': r['year'],
                'cgpa': r['cgpa'],
                'career_goal': r['career_goal'],
                'is_excel': False
            })
            
        # Load Excel students
        cursor.execute("SELECT name, email_id, year, current_course, job_role_aspiration FROM excel_student_profiles LIMIT 15")
        excel_rows = cursor.fetchall()
        for r in excel_rows:
            students_list.append({
                'id': r['email_id'],
                'name': r['name'],
                'branch': r['current_course'], # B.Tech
                'year': r['year'],
                'cgpa': 7.5, # Default mock
                'career_goal': r['job_role_aspiration'],
                'is_excel': True
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
    return jsonify(students_list)

# 2. API: Get or Update active student profile
@app.route('/api/profile', methods=['GET', 'POST'])
def manage_profile():
    if request.method == 'GET':
        active = get_active_student_profile()
        normalized = normalize_student_profile(active, active.get('is_excel', False))
        return jsonify({
            'raw': active,
            'normalized': normalized
        })
        
    elif request.method == 'POST':
        data = request.json or {}
        resolve_id = data.get('resolve_id')
        is_excel = data.get('is_excel', False)
        
        try:
            if resolve_id:
                conn = get_db_connection()
                cursor = conn.cursor()
                if is_excel:
                    cursor.execute("SELECT * FROM excel_student_profiles WHERE email_id = ?", (resolve_id,))
                    row = cursor.fetchone()
                    if row:
                        profile = dict(row)
                        profile['is_excel'] = True
                    else:
                        return jsonify({'error': 'Student not found in Excel profiles'}), 404
                else:
                    cursor.execute("SELECT * FROM student_profiles WHERE student_id = ?", (resolve_id,))
                    row = cursor.fetchone()
                    if row:
                        profile = dict(row)
                        profile['is_excel'] = False
                    else:
                        return jsonify({'error': 'Student not found in CSV profiles'}), 404
                conn.close()
            else:
                profile = data
                
            # Save active profile
            with open(ACTIVE_PROFILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2)
            return jsonify({'status': 'success', 'message': 'Profile updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# 3. API: Get personalized job recommendations
@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    active = get_active_student_profile()
    if not active:
        return jsonify({'error': 'No active student profile'}), 400
        
    normalized = normalize_student_profile(active, active.get('is_excel', False))
    recs = get_recommendations_for_student(normalized, limit=8)
    return jsonify(recs)

# 4. API: Analyze skill gap for target role
@app.route('/api/skill-gap', methods=['GET'])
def get_skill_gap():
    role_id = request.args.get('role_id')
    if not role_id:
        return jsonify({'error': 'role_id is required'}), 400
        
    active = get_active_student_profile()
    normalized = normalize_student_profile(active, active.get('is_excel', False))
    gap = analyze_skill_gap(normalized, role_id)
    return jsonify(gap)

# 5. API: Get weekly roadmap
@app.route('/api/roadmap', methods=['GET'])
def get_roadmap():
    role_id = request.args.get('role_id')
    roadmap_type = request.args.get('type', '90-Day')
    if not role_id:
        return jsonify({'error': 'role_id is required'}), 400
        
    active = get_active_student_profile()
    normalized = normalize_student_profile(active, active.get('is_excel', False))
    roadmap = get_detailed_roadmap(role_id, roadmap_type, normalized)
    return jsonify(roadmap)

# 6. API: Get interview questions and evaluate answers
@app.route('/api/interview', methods=['GET', 'POST'])
def manage_interview():
    if request.method == 'GET':
        role_id = request.args.get('role_id')
        safe_print(f"[API INVOCATION] GET /api/interview for role_id='{role_id}'")
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            questions = []
            if role_id and role_id != 'undefined':
                cursor.execute("""
                    SELECT question_id, question, difficulty, question_type, expected_answer, keywords, company_level 
                    FROM interview_questions 
                    WHERE role_id = ? LIMIT 6
                """, (role_id,))
                questions = [dict(row) for row in cursor.fetchall()]
                
            if not questions:
                safe_print(f"[INTERVIEW API] Fetching default interview question set...")
                cursor.execute("""
                    SELECT question_id, question, difficulty, question_type, expected_answer, keywords, company_level 
                    FROM interview_questions 
                    LIMIT 6
                """)
                questions = [dict(row) for row in cursor.fetchall()]
                
            safe_print(f"[INTERVIEW API] Returned {len(questions)} interview questions")
            return jsonify(questions)
        except Exception as e:
            safe_print(f"[INTERVIEW API ERROR] {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
            
    elif request.method == 'POST':
        # Grade standard answers based on keywords
        data = request.json
        question_id = data.get('question_id')
        student_answer = data.get('student_answer', '')
        
        if not question_id:
            return jsonify({'error': 'question_id is required'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT expected_answer, keywords FROM interview_questions WHERE question_id = ?", (question_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': 'Question not found'}), 404
                
            expected = row['expected_answer']
            keywords_str = row['keywords'] or ""
            keywords = [k.strip().lower() for k in keywords_str.split(',') if k.strip()]
            
            # Simple keyword matching scoring
            matched = []
            missing = []
            answer_lower = student_answer.lower()
            
            for kw in keywords:
                if kw in answer_lower:
                    matched.append(kw)
                else:
                    missing.append(kw)
                    
            total_kws = len(keywords)
            score = 0
            if total_kws > 0:
                score = int((len(matched) / total_kws) * 100)
            else:
                score = 50 # Default baseline
                
            # Grade feedback
            feedback = ""
            if score >= 80:
                feedback = "Excellent answer! You hit almost all the core conceptual keywords."
            elif score >= 50:
                feedback = "Good attempt. However, you could improve by talking about: " + ", ".join(missing[:3])
            else:
                feedback = "Your answer is too brief or missing core keywords. Be sure to reference: " + ", ".join(missing[:3])
                
            return jsonify({
                'score': score,
                'feedback': feedback,
                'matched_keywords': matched,
                'missing_keywords': missing,
                'expected_answer': expected
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()

# 7. API: Grounded RAG Chatbot with translation and streaming
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '')
    lang = data.get('lang', 'en')
    stream = data.get('stream', False)
    
    if not message:
        return jsonify({'error': 'message is required'}), 400
        
    user_email = request.headers.get('X-User-Email', 'STU0001')
    
    safe_print("\n" + "#"*100)
    safe_print(f"[RAG PIPELINE / CHAT ENDPOINT] RECEIVED INCOMING REQUEST:")
    safe_print(f"  - User Session Email: '{user_email}'")
    safe_print(f"  - Message Content:    '{message}'")
    safe_print(f"  - Selected Language:  '{lang}'")
    safe_print(f"  - Streaming Enabled:  {stream}")
    safe_print("#"*100 + "\n")
    
    try:
        active_profile = get_active_student_profile()
        
        # Load recent conversation history from SQLite
        history = get_user_chat_history(user_email)
        
        # Log user query to history
        log_chat_message(user_email, 'user', message)
        
        # Translate to English if needed
        message_en = message
        if lang != 'en':
            from sarvam_client import SarvamClient
            s_client = SarvamClient()
            message_en = s_client.translate_to_english(message, lang)
            safe_print(f"Translated query: '{message}' ({lang}) -> '{message_en}' (en)")
            
        # Get response from Adaptive RAG (passing the conversation history context)
        safe_print(f"Calling Adaptive RAG for query: {message_en}")
        res_tuple = adaptive_rag.ask(message_en, active_profile, history=history)
        if res_tuple and isinstance(res_tuple, tuple):
            response_en, sources = res_tuple
        else:
            response_en, sources = res_tuple, []
            
        if response_en is None:
            response_en = "I'm sorry, I couldn't generate a response. Please verify if the API services are fully operational."
            sources = []
        
        # Post-processing disclaimer
        disclaimer = "\n\n*Disclaimer: Guidance is based on historical database placements.*"
        if "Disclaimer:" not in response_en:
            response_en_full = response_en + disclaimer
        else:
            response_en_full = response_en
        
        # Translate response back to the user's selected language
        final_answer = response_en_full
        if lang != 'en':
            from sarvam_client import SarvamClient
            s_client = SarvamClient()
            final_answer = s_client.translate_from_english(response_en_full, lang)
            
        # Log assistant response to history
        log_chat_message(user_email, 'assistant', final_answer)
            
        # Support Server-Sent Events (SSE) Streaming
        if stream:
            def generate_stream():
                # Yield chunks of final_answer in batches of 4 words to prevent timeout while keeping typing effect
                words = final_answer.split(' ')
                chunk_size = 4
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size]) + " "
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    time.sleep(0.02) # 20ms delay per chunk
                # Yield sources metadata at the end of the stream
                yield f"data: {json.dumps({'chunk': '', 'sources': sources})}\n\n"
                yield "data: [DONE]\n\n"
            return Response(generate_stream(), mimetype='text/event-stream')
            
        # Standard JSON response
        return jsonify({
            'answer': final_answer,
            'sources': sources,
            'lang': lang
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500


# 8. API: User feedback logging
@app.route('/api/feedback', methods=['POST'])
def log_feedback():
    data = request.json or {}
    rating = data.get('rating') # 'up' or 'down'
    query = data.get('query')
    response = data.get('response')
    
    log_entry = {
        'rating': rating,
        'query': query,
        'response': response
    }
    
    # Save log
    feedback_list = []
    if os.path.exists(FEEDBACK_PATH):
        try:
            with open(FEEDBACK_PATH, 'r', encoding='utf-8') as f:
                feedback_list = json.load(f)
        except Exception:
            pass
            
    feedback_list.append(log_entry)
    
    try:
        with open(FEEDBACK_PATH, 'w', encoding='utf-8') as f:
            json.dump(feedback_list, f, indent=2)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 9. API: Placement Cell / Mentor Insights
@app.route('/api/mentor/insights', methods=['GET'])
def get_mentor_insights():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    insights = {
        'total_students_logged': 1500, # CSV + Excel
        'branch_distribution': {},
        'top_aspirations': {},
        'branch_average_score': {},
        'common_skill_gaps': []
    }
    
    try:
        # 1. Branch distribution count
        cursor.execute("SELECT branch, COUNT(*) as cnt FROM student_profiles GROUP BY branch")
        for row in cursor.fetchall():
            insights['branch_distribution'][row['branch']] = row['cnt']
            
        # Add Excel counts
        cursor.execute("SELECT current_course, COUNT(*) as cnt FROM excel_student_profiles GROUP BY current_course")
        for row in cursor.fetchall():
            course = row['current_course']
            insights['branch_distribution'][course] = insights['branch_distribution'].get(course, 0) + row['cnt']
            
        # 2. Top aspirations
        cursor.execute("SELECT career_goal, COUNT(*) as cnt FROM student_profiles GROUP BY career_goal ORDER BY cnt DESC LIMIT 5")
        for row in cursor.fetchall():
            goal = row['career_goal']
            if goal:
                insights['top_aspirations'][goal] = row['cnt']
                
        # 3. Aggregated mock skill gap metrics
        cursor.execute("""
            SELECT s.skill_name, COUNT(*) as cnt
            FROM role_skill_mapping rsm
            JOIN skills s ON rsm.skill_id = s.skill_id
            WHERE rsm.mandatory = 'Yes'
            GROUP BY s.skill_name ORDER BY cnt DESC LIMIT 5
        """)
        for row in cursor.fetchall():
            insights['common_skill_gaps'].append({
                'skill_name': row['skill_name'],
                'importance': 'Critical Gap (Mandatory across roles)'
            })
            # 4. Load recent feedback entries
            feedback_list = []
            if os.path.exists(FEEDBACK_PATH):
                try:
                    with open(FEEDBACK_PATH, 'r', encoding='utf-8') as f:
                        feedback_list = json.load(f)
                except Exception:
                    pass
            insights['recent_feedback'] = feedback_list[-5:]
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
        
    return jsonify(insights)

# 10. API: List all courses
@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT c.*, s.skill_name FROM courses c JOIN skills s ON c.skill_id = s.skill_id LIMIT 60")
        courses = [dict(row) for row in cursor.fetchall()]
        return jsonify(courses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 11. API: Industry Trends
@app.route('/api/industry-trends', methods=['GET'])
def get_industry_trends():
    role_id = request.args.get('role_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if role_id:
            cursor.execute("SELECT t.*, r.role_name FROM industry_trends t JOIN roles r ON t.role_id = r.role_id WHERE t.role_id = ?", (role_id,))
        else:
            cursor.execute("SELECT t.*, r.role_name FROM industry_trends t JOIN roles r ON t.role_id = r.role_id LIMIT 50")
        trends = [dict(row) for row in cursor.fetchall()]
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 12. API: Career Comparison
@app.route('/api/career-comparison', methods=['GET'])
def get_career_comparison():
    role_1_id = request.args.get('role_1_id')
    role_2_id = request.args.get('role_2_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if role_1_id and role_2_id:
            cursor.execute("""
                SELECT * FROM career_comparison 
                WHERE (role_1_id = ? AND role_2_id = ?) 
                   OR (role_1_id = ? AND role_2_id = ?)
            """, (role_1_id, role_2_id, role_2_id, role_1_id))
            comparison = [dict(row) for row in cursor.fetchall()]
            if comparison:
                return jsonify(comparison[0])
            else:
                cursor.execute("SELECT * FROM roles WHERE role_id IN (?, ?)", (role_1_id, role_2_id))
                roles = [dict(row) for row in cursor.fetchall()]
                if len(roles) >= 2:
                    r1, r2 = roles[0], roles[1]
                    return jsonify({
                        'role_1_name': r1['role_name'],
                        'role_2_name': r2['role_name'],
                        'salary_comparison': f"Salary Range: {r1['salary_range']} vs {r2['salary_range']}",
                        'required_skills_role_1': r1['description'] or "Key tech skills",
                        'required_skills_role_2': r2['description'] or "Key tech skills",
                        'job_growth': "Steady industry growth estimated at 12-15% annually.",
                        'work_life_balance': "Depends on company profile.",
                        'difficulty_to_enter': "Medium/High - requires preparation.",
                        'remote_opportunities': "Flexible options available.",
                        'best_for': f"{r1['role_name']} is best for analytic minds. {r2['role_name']} is best for system builders.",
                        'summary': f"Comparison of career opportunities in {r1['role_name']} vs {r2['role_name']}."
                    })
                return jsonify({'error': 'Roles not found'}), 404
        else:
            cursor.execute("SELECT * FROM career_comparison LIMIT 50")
            comparisons = [dict(row) for row in cursor.fetchall()]
            return jsonify(comparisons)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 13. API: Soft Skills
@app.route('/api/soft-skills', methods=['GET'])
def get_soft_skills():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM soft_skills")
        soft_skills = [dict(row) for row in cursor.fetchall()]
        return jsonify(soft_skills)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 14. API: Job Board
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    role_id = request.args.get('role_id')
    user_email = request.headers.get('X-User-Email')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Try resolving role_id from user profile if not passed
        if not role_id and user_email:
            cursor.execute("SELECT preferred_role FROM user_profiles WHERE email = ?", (user_email,))
            row = cursor.fetchone()
            if row:
                role_id = row['preferred_role']
        
        if role_id:
            cursor.execute("SELECT * FROM jobs WHERE role_id = ?", (role_id,))
        else:
            cursor.execute("SELECT * FROM jobs LIMIT 100")
            
        jobs = [dict(row) for row in cursor.fetchall()]
        return jsonify(jobs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 15. API: Change Password
@app.route('/api/auth/change-password', methods=['POST'])
def change_password():
    data = request.json or {}
    user_email = request.headers.get('X-User-Email')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not user_email or not old_password or not new_password:
        return jsonify({'error': 'All fields are required'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE email = ?", (user_email,))
        user = cursor.fetchone()
        if not user or not check_password_hash(user['password_hash'], old_password):
            return jsonify({'error': 'Incorrect current password'}), 401
            
        new_hash = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, user_email))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Password updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


# 16. API: Text to Speech (TTS) using Sarvam Bulbul
@app.route('/api/tts', methods=['POST'])
def text_to_speech_api():
    data = request.json or {}
    text = data.get('text', '')
    lang = data.get('lang', 'en')
    
    if not text:
        return jsonify({'error': 'text is required'}), 400
        
    try:
        from sarvam_client import SarvamClient
        client = SarvamClient()
        audio_base64 = client.text_to_speech(text, lang)
        if audio_base64:
            return jsonify({'audio': audio_base64})
        else:
            return jsonify({'error': 'Failed to synthesize speech'}), 500
    except Exception as e:
        print(f"Error in TTS endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# 17. API: Speech to Text (STT) using Sarvam Saaras
@app.route('/api/stt', methods=['POST'])
def speech_to_text_api():
    if 'file' not in request.files:
        return jsonify({'error': 'audio file is required'}), 400
        
    audio_file = request.files['file']
    lang = request.form.get('lang', 'en')
    
    lang_map = {
        "hi": "hi-IN",
        "hinglish": "hi-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "en": "en-IN"
    }
    lang_code = lang_map.get(lang.lower(), "en-IN")
    
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    ext = os.path.splitext(audio_file.filename)[1] or ".wav"
    temp_path = os.path.join(temp_dir, f"audio_{int(time.time())}{ext}")
    
    try:
        audio_file.save(temp_path)
        
        from sarvam_client import SarvamClient
        client = SarvamClient()
        transcript = client.speech_to_text(temp_path, lang_code)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return jsonify({'transcript': transcript})
    except Exception as e:
        print(f"Error in STT endpoint: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500


# 18. API: Image OCR Text Extraction for Resumes, Documents & Code Snippets
@app.route('/api/ocr', methods=['POST'])
def extract_text_from_image_api():
    safe_print("\n" + "#"*100)
    safe_print("[OCR PIPELINE] INCOMING IMAGE OCR TEXT EXTRACTION REQUEST")
    
    extracted_text = ""
    
    try:
        if 'file' in request.files or 'image' in request.files:
            image_file = request.files.get('file') or request.files.get('image')
            safe_print(f"  - Received Image File: '{image_file.filename}'")
            
            from PIL import Image
            img = Image.open(image_file.stream)
            
            # 1. Pytesseract OCR
            try:
                import pytesseract
                extracted_text = pytesseract.image_to_string(img)
                safe_print(f"  - Pytesseract OCR succeeded! Extracted {len(extracted_text)} chars.")
            except Exception as pe:
                safe_print(f"  - Pytesseract fallback info: {pe}")
                
            # 2. EasyOCR fallback if empty
            if not extracted_text.strip():
                try:
                    import easyocr
                    reader = easyocr.Reader(['en'], gpu=False)
                    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_audio")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_img_path = os.path.join(temp_dir, f"ocr_{int(time.time())}.png")
                    img.save(temp_img_path)
                    
                    results = reader.readtext(temp_img_path)
                    extracted_text = " ".join([res[1] for res in results])
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                    safe_print(f"  - EasyOCR succeeded! Extracted {len(extracted_text)} chars.")
                except Exception as ee:
                    safe_print(f"  - EasyOCR fallback info: {ee}")
                    
        elif request.json and ('image_base64' in request.json or 'image' in request.json):
            b64_str = request.json.get('image_base64') or request.json.get('image')
            safe_print("  - Received Base64 Encoded Image Payload")
            import base64
            from io import BytesIO
            from PIL import Image
            
            if ',' in b64_str:
                b64_str = b64_str.split(',')[1]
                
            img_data = base64.b64decode(b64_str)
            img = Image.open(BytesIO(img_data))
            
            try:
                import pytesseract
                extracted_text = pytesseract.image_to_string(img)
                safe_print(f"  - Base64 Pytesseract OCR succeeded! Extracted {len(extracted_text)} chars.")
            except Exception as pe:
                safe_print(f"  - Base64 Pytesseract info: {pe}")

        extracted_text = extracted_text.strip()
        safe_print(f"[OCR PIPELINE] Extraction complete. Extracted Snippet: '{extracted_text[:120]}...'")
        safe_print("#"*100 + "\n")
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'char_count': len(extracted_text)
        })
    except Exception as e:
        safe_print(f"[OCR PIPELINE ERROR] Exception during OCR extraction: {e}")
        return jsonify({'error': str(e), 'text': ''}), 500


@app.route('/<path:filename>')
def serve_static(filename):
    target = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(target) and not os.path.isdir(target):
        return send_from_directory(FRONTEND_DIR, filename)
    return send_from_directory(FRONTEND_DIR, 'index.html')

if __name__ == '__main__':
    # Initialize SQLite chat history DB table
    init_chat_history_db()
    
    # Initialize active student if not set
    if not os.path.exists(ACTIVE_PROFILE_PATH):
        default_student = {
            "student_id": "STU0001",
            "branch": "Computer Science",
            "year": 3,
            "cgpa": 8.12,
            "known_skills": "SK001, SK006, SK008", # Python, Data Structures, Algorithms
            "preferred_role": "ROLE001", # Data Scientist
            "daily_learning_hours": 3,
            "is_excel": False
        }
        with open(ACTIVE_PROFILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_student, f, indent=2)
            
    safe_print("\n" + "=" * 80)
    safe_print("[STARTUP] UNIFIED AI CAREER GUIDANCE PORTAL STARTED")
    safe_print("================================================================================")
    safe_print("[PORTAL URL] Serving Unified Application (Frontend + Backend) at: http://localhost:5000")
    safe_print("[LOGGING] All Requests, API Calls, & Terminal RAG Logs active in this window.")
    safe_print("================================================================================\n")
    
    # Auto-open browser window after server initializes
    import webbrowser, threading
    def auto_open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open("http://localhost:5000")
        except Exception:
            pass
            
    threading.Thread(target=auto_open_browser, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False, threaded=True)
