/* =======================================================
   AI Career Guidance - Interview Prep Page Controller
   ======================================================= */

const API_ROOT_URL = (window.getApiBaseUrl ? window.getApiBaseUrl() : (window.location.origin + "/api"));
let currentQuestions = [];
let activeQIdx = 0;

function initInterviewPage() {
    setTimeout(initInterview, 300);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initInterviewPage);
} else {
    initInterviewPage();
}

async function initInterview() {
    let roleId = "ROLE001";
    try {
        const recRes = await fetch(`${API_ROOT_URL}/recommendations`);
        if (recRes.ok) {
            const recs = await recRes.json();
            if (recs && recs.length > 0 && recs[0].role_id) {
                roleId = recs[0].role_id;
            }
        }
    } catch (err) {
        console.warn("Could not fetch recommendations, using default role:", err);
    }
    await loadQuestions(roleId);
}

async function loadQuestions(roleId) {
    const qText = document.getElementById("questionText");
    if (!qText) return;
    
    try {
        const res = await fetch(`${API_ROOT_URL}/interview?role_id=${roleId || 'ROLE001'}`);
        if (!res.ok) {
            console.warn("Retrying default interview questions...");
            const fallbackRes = await fetch(`${API_ROOT_URL}/interview`);
            currentQuestions = await fallbackRes.json();
        } else {
            currentQuestions = await res.json();
        }
        
        if (!currentQuestions || currentQuestions.length === 0) {
            qText.textContent = "Loading default technical interview questions...";
            return;
        }
        
        activeQIdx = 0;
        renderActiveQuestion();
        
        // Wire up buttons
        document.getElementById("prevQBtn").onclick = () => {
            if (activeQIdx > 0) {
                activeQIdx--;
                renderActiveQuestion();
            }
        };
        
        document.getElementById("nextQBtn").onclick = () => {
            if (activeQIdx < currentQuestions.length - 1) {
                activeQIdx++;
                renderActiveQuestion();
            }
        };
        
        document.getElementById("gradeAnswerBtn").onclick = handleAnswerGrading;
        
    } catch (err) {
        console.error("Error loading questions list:", err);
        qText.textContent = "Error connecting to Flask backend.";
    }
}

function renderActiveQuestion() {
    if (currentQuestions.length === 0) return;
    
    const q = currentQuestions[activeQIdx];
    
    document.getElementById("qNumberLabel").textContent = `Question ${activeQIdx + 1} of ${currentQuestions.length}`;
    document.getElementById("questionText").textContent = q.question;
    
    const metaLabel = document.getElementById("qMetaLabel");
    metaLabel.textContent = `${q.question_type.toUpperCase()} · ${q.difficulty.toUpperCase()} · ${q.company_level.toUpperCase()} LEVEL`;
    
    // Clear answer input and result panel
    document.getElementById("studentAnswerText").value = "";
    document.getElementById("resultsContent").innerHTML = `
        <div style="text-align:center; padding:40px 10px; color:#9CA3AF; font-size:11.5px;">
            Draft your explanation and submit the answer to calculate matching keywords and retrieve mentor grade evaluations.
        </div>
    `;
}

async function handleAnswerGrading() {
    const text = document.getElementById("studentAnswerText").value.trim();
    if (!text) {
        alert("Please write your answer response before grading.");
        return;
    }
    
    const q = currentQuestions[activeQIdx];
    const resultsContainer = document.getElementById("resultsContent");
    
    // Show loading
    resultsContainer.innerHTML = `
        <div style="text-align:center; padding:30px; color:#9CA3AF;">
            <i class="ti ti-loader" style="font-size:24px; animation:spin 1s linear infinite;"></i>
            <p style="font-size:11px; margin-top:8px;">Evaluating conceptual keywords...</p>
        </div>
    `;
    
    try {
        const res = await fetch(`${API_ROOT_URL}/interview`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_id: q.question_id,
                student_answer: text
            })
        });
        
        if (res.ok) {
            const grade = await res.json();
            
            // Build keyword tags
            const matchedTags = grade.matched_keywords.map(k => 
                `<span class="keyword-tag matched"><i class="ti ti-check"></i> ${k}</span>`
            ).join("");
            
            const missingTags = grade.missing_keywords.map(k => 
                `<span class="keyword-tag missing"><i class="ti ti-x"></i> ${k}</span>`
            ).join("");
            
            // Determine score color
            let scoreColor = "#16A34A"; // green
            if (grade.score < 50) scoreColor = "#EF4444"; // red
            else if (grade.score < 80) scoreColor = "#F59E0B"; // amber
            
            resultsContainer.innerHTML = `
                <div style="display:flex; align-items:center; gap:16px; margin-bottom:10px;">
                    <div style="width:55px; height:55px; border-radius:50%; background:#F3F4F6; display:flex; align-items:center; justify-content:center; font-size:18px; font-weight:800; color:${scoreColor}; border:3px solid ${scoreColor};">
                        ${grade.score}
                    </div>
                    <div>
                        <h4 style="margin:0; font-size:12.5px;">Readiness Score</h4>
                        <p style="margin:2px 0 0; font-size:11px; color:#4B5563;">Based on required industry keywords.</p>
                    </div>
                </div>
                
                <div style="background:#FAFAFF; border:1px solid #ECEDF3; padding:12px; border-radius:8px; font-size:11.5px; line-height:1.45; color:#1F2937;">
                    <strong>Mentor Feedback:</strong><br>
                    ${grade.feedback}
                </div>
                
                <div style="font-size:11.5px;">
                    <strong>Matching Keywords:</strong>
                    <div class="keyword-list" style="margin-top:6px; margin-bottom:12px;">
                        ${matchedTags ? matchedTags : '<span style="font-size:10px; color:#9CA3AF;">None matched</span>'}
                    </div>
                    
                    <strong>Missing Concept Keywords:</strong>
                    <div class="keyword-list" style="margin-top:6px; margin-bottom:12px;">
                        ${missingTags ? missingTags : '<span style="font-size:10px; color:#16A34A;">None missing!</span>'}
                    </div>
                </div>
                
                <div style="border-top:1px solid #ECEDF3; padding-top:10px; margin-top:4px;">
                    <button class="btn-recommended" onclick="toggleRecommendedAnswerBox()">View Model Answer <i class="ti ti-chevron-down"></i></button>
                    <div id="recommendedAnswerBox" style="display:none; background:#F9FAFB; border:1px solid #ECEDF3; padding:12px; border-radius:8px; font-size:11px; line-height:1.45; color:#4B5563; margin-top:8px; font-style:italic;">
                        ${grade.expected_answer}
                    </div>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = `<div style="text-align:center; padding:30px; color:#EF4444;">Evaluation failed.</div>`;
        }
    } catch (err) {
        console.error("Grading submit error:", err);
        resultsContainer.innerHTML = `<div style="text-align:center; padding:30px; color:#EF4444;">Failed to connect to grading API.</div>`;
    }
}

window.toggleRecommendedAnswerBox = function() {
    const box = document.getElementById("recommendedAnswerBox");
    const btn = document.querySelector(".btn-recommended");
    
    if (box.style.display === "none") {
        box.style.display = "block";
        btn.innerHTML = `Hide Model Answer <i class="ti ti-chevron-up"></i>`;
    } else {
        box.style.display = "none";
        btn.innerHTML = `View Model Answer <i class="ti ti-chevron-down"></i>`;
    }
};
