/* =======================================================
   AI Career Guidance - Resume Page Controller
   ======================================================= */

const API_RESUME = "http://localhost:5000/api";

function initResumePage() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    
    if (!dropzone || !fileInput) return;

    // Handle clicks to select file
    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.style.background = "rgba(108, 99, 255, 0.1)";
        dropzone.style.borderColor = "var(--indigo)";
    });

    ["dragleave", "dragend"].forEach(type => {
        dropzone.addEventListener(type, () => {
            dropzone.style.background = "rgba(255, 255, 255, 0.6)";
            dropzone.style.borderColor = "rgba(108, 99, 255, 0.4)";
        });
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.style.background = "rgba(255, 255, 255, 0.6)";
        dropzone.style.borderColor = "rgba(108, 99, 255, 0.4)";
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleResumeUpload(files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            handleResumeUpload(fileInput.files[0]);
        }
    });
}

async function handleResumeUpload(file) {
    const dropzone = document.getElementById("dropzone");
    const uploadStatus = document.getElementById("uploadStatus");
    
    if (!dropzone || !uploadStatus) return;

    // Show upload state
    uploadStatus.style.display = "block";
    uploadStatus.innerHTML = `<i class="ti ti-loader-2 animate-spin"></i> Uploading and analyzing resume...`;

    // Fetch active student profile to get target role_id
    let roleId = "ROLE001"; // Fallback to Data Scientist
    try {
        const user = JSON.parse(localStorage.getItem("career_user"));
        const headers = user ? { "X-User-Email": user.email } : {};
        const profileRes = await fetch(`${API_RESUME}/profile`, { headers });
        if (profileRes.ok) {
            const profileData = await profileRes.json();
            if (profileData.normalized && profileData.normalized.preferred_role) {
                roleId = profileData.normalized.preferred_role;
            }
        }
    } catch (err) {
        console.error("Failed to load active profile for resume analysis:", err);
    }

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("role_id", roleId);

    try {
        const user = JSON.parse(localStorage.getItem("career_user"));
        const headers = user ? { "X-User-Email": user.email } : {};
        
        const response = await fetch(`${API_RESUME}/resume/analyze`, {
            method: "POST",
            headers: headers,
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "Failed to analyze resume.");
        }

        const result = await response.json();
        renderAnalysisResults(result);

    } catch (err) {
        console.error(err);
        uploadStatus.innerHTML = `<span style="color: var(--red);"><i class="ti ti-alert-circle"></i> Error: ${err.message}</span>`;
    }
}

function renderAnalysisResults(data) {
    const uploadStatus = document.getElementById("uploadStatus");
    const scorePanel = document.getElementById("scorePanel");
    const skillsPanel = document.getElementById("skillsPanel");
    const suggestionsPanel = document.getElementById("suggestionsPanel");
    const coursesPanel = document.getElementById("coursesPanel");
    
    if (uploadStatus) uploadStatus.style.display = "none";
    
    // 1. Show all panels
    if (scorePanel) scorePanel.style.display = "flex";
    if (skillsPanel) skillsPanel.style.display = "block";
    if (suggestionsPanel) suggestionsPanel.style.display = "block";
    if (coursesPanel) coursesPanel.style.display = "block";

    // 2. Animate ATS Score
    const scoreNumber = document.getElementById("scoreNumber");
    const atsCircle = document.getElementById("atsCircle");
    if (scoreNumber && atsCircle) {
        let currentScore = 0;
        const targetScore = data.ats_score;
        const interval = setInterval(() => {
            if (currentScore >= targetScore) {
                clearInterval(interval);
            } else {
                currentScore++;
                scoreNumber.textContent = `${currentScore}%`;
                // SVG circle math: circumference = 2 * PI * r = 2 * 3.14159 * 50 = 314.16
                const offset = 314.16 - (314.16 * currentScore) / 100;
                atsCircle.style.strokeDashoffset = offset;
            }
        }, 15);
    }

    // 3. Set Score Labels & Details
    const scoreLabel = document.getElementById("scoreLabel");
    const scoreFeedback = document.getElementById("scoreFeedback");
    if (scoreLabel && scoreFeedback) {
        if (data.ats_score >= 80) {
            scoreLabel.textContent = "Excellent Match!";
            scoreLabel.style.color = "var(--green)";
            scoreFeedback.textContent = "Your resume structure and skills are highly compatible with hiring expectations. Only minor additions recommended.";
        } else if (data.ats_score >= 60) {
            scoreLabel.textContent = "Good Potential";
            scoreLabel.style.color = "var(--amber)";
            scoreFeedback.textContent = "Solid resume core, but you have key missing skills. Focus on adding coursework or project keywords.";
        } else {
            scoreLabel.textContent = "Needs Attention";
            scoreLabel.style.color = "var(--red)";
            scoreFeedback.textContent = "Your resume score is low. Please list more relevant skills and include contact details to pass automated filters.";
        }
    }

    const parsedEmail = document.getElementById("parsedEmail");
    const parsedPhone = document.getElementById("parsedPhone");
    if (parsedEmail) parsedEmail.textContent = data.parsed_details.email || "Not detected";
    if (parsedPhone) parsedPhone.textContent = data.parsed_details.phone || "Not detected";

    // 4. Render matched/missing skills
    const matchedSkillsList = document.getElementById("matchedSkillsList");
    if (matchedSkillsList) {
        matchedSkillsList.innerHTML = "";
        if (data.matched_skills.length > 0) {
            data.matched_skills.forEach(skill => {
                matchedSkillsList.innerHTML += `<span class="badge progress" style="background: var(--green-bg); color: var(--green); padding: 6px 12px;">${skill}</span>`;
            });
        } else {
            matchedSkillsList.innerHTML = `<span class="badge notstarted" style="padding: 6px 12px;">None detected</span>`;
        }
    }

    const missingSkillsList = document.getElementById("missingSkillsList");
    if (missingSkillsList) {
        missingSkillsList.innerHTML = "";
        const allMissing = [...data.missing_skills.mandatory, ...data.missing_skills.recommended];
        if (allMissing.length > 0) {
            allMissing.forEach(skill => {
                missingSkillsList.innerHTML += `<span class="badge progress" style="background: var(--red-bg); color: var(--red); padding: 6px 12px;">${skill}</span>`;
            });
        } else {
            missingSkillsList.innerHTML = `<span class="badge progress" style="background: var(--green-bg); color: var(--green); padding: 6px 12px;">No missing skills!</span>`;
        }
    }

    // 5. Render suggestions list
    const suggestionsList = document.getElementById("suggestionsList");
    if (suggestionsList) {
        suggestionsList.innerHTML = "";
        if (data.suggestions.length > 0) {
            data.suggestions.forEach(suggestion => {
                suggestionsList.innerHTML += `<li style="margin-bottom: 8px;"><i class="ti ti-info-circle-filled" style="color: var(--indigo); font-size: 14px; margin-right: 5px;"></i> ${suggestion}</li>`;
            });
        } else {
            suggestionsList.innerHTML = `<li><i class="ti ti-circle-check-filled" style="color: var(--green); font-size: 14px; margin-right: 5px;"></i> Your resume is fully optimized!</li>`;
        }
    }

    // 6. Render course recommendations
    const recommendedCoursesGrid = document.getElementById("recommendedCoursesGrid");
    if (recommendedCoursesGrid) {
        recommendedCoursesGrid.innerHTML = "";
        if (data.recommended_courses.length > 0) {
            data.recommended_courses.forEach(course => {
                recommendedCoursesGrid.innerHTML += `
                    <div class="panel" style="padding: 15px; margin: 0; background: rgba(255, 255, 255, 0.4); display: flex; flex-direction: column; justify-content: space-between; border: 1px solid var(--border);">
                        <div>
                            <div style="font-size: 11px; font-weight: 700; color: var(--indigo); text-transform: uppercase; margin-bottom: 5px;">${course.platform} · ${course.provider}</div>
                            <h4 style="margin: 0 0 10px; font-size: 13.5px; font-weight: 600; line-height: 1.3;">${course.course_name}</h4>
                            <div style="font-size: 12px; color: var(--text-2); display: flex; align-items: center; gap: 5px;">
                                <i class="ti ti-star" style="color: var(--amber);"></i> ${course.rating || "4.5"}
                            </div>
                        </div>
                        <a href="${course.course_url}" target="_blank" class="start-btn" style="margin-top: 15px; padding: 7px 12px; font-size: 11.5px; text-decoration: none; display: inline-flex; justify-content: center; align-items: center;">View Course <i class="ti ti-arrow-right"></i></a>
                    </div>
                `;
            });
        } else {
            recommendedCoursesGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-2); font-size: 13px;">No specific course recommendations required.</div>`;
        }
    }
}

// Auto-init on load/ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initResumePage);
} else {
    initResumePage();
}
