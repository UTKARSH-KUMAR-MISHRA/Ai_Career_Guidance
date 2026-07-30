/* =======================================================
   AI Career Guidance - Skill Gap Analysis Page Controller
   ======================================================= */

(() => {
const API_BASE_URL = (window.getApiBaseUrl ? window.getApiBaseUrl() : (window.location.origin + "/api"));

function initSkillGapPage() {
    setTimeout(initSkillGap, 300);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSkillGapPage);
} else {
    initSkillGapPage();
}

async function initSkillGap() {
    // 1. Get role_id from state or URL query string
    const params = new URLSearchParams(window.location.search);
    let roleId = window.selectedTargetRoleId || params.get("role_id");
    
    // If no role_id provided, fetch recommendations and pick the top match
    if (!roleId) {
        try {
            const recRes = await fetch(`${API_BASE_URL}/recommendations`);
            if (recRes.ok) {
                const recs = await recRes.json();
                if (recs.length > 0) {
                    roleId = recs[0].role_id;
                }
            }
        } catch (err) {
            console.error("Failed to load recommendations for top role:", err);
        }
    }
    
    if (!roleId) {
        // Fallback default
        roleId = "ROLE001";
    }
    
    loadSkillGapDetails(roleId);
}

async function loadSkillGapDetails(roleId) {
    const listContainer = document.getElementById("skillsChecklist");
    const coursesList = document.getElementById("gapCoursesList");
    const projectsList = document.getElementById("gapProjectsList");
    const certsList = document.getElementById("gapCertificationsList");
    const banner = document.getElementById("timelineBanner");
    const circlePath = document.getElementById("gapCirclePath");
    const matchPctEl = document.getElementById("gapMatchPct");
    const targetRoleEl = document.getElementById("gapTargetRoleName");
    
    try {
        const res = await fetch(`${API_BASE_URL}/skill-gap?role_id=${roleId}`);
        if (!res.ok) return;
        
        const data = await res.json();
        
        // 1. Render match score and circular progress SVG
        // Circumference of radius 40 is 2 * pi * 40 = 251.2
        // We fetch match score from recommendations
        const recRes = await fetch(`${API_BASE_URL}/recommendations`);
        let matchScore = 50; // default fallback
        if (recRes.ok) {
            const recs = await recRes.json();
            const matchingRole = recs.find(r => r.role_id === roleId);
            if (matchingRole) {
                matchScore = matchingRole.match_score;
            }
        }
        
        targetRoleEl.textContent = data.role_name;
        matchPctEl.textContent = `${matchScore}%`;
        const offset = 251.2 - (matchScore / 100) * 251.2;
        if (circlePath) {
            circlePath.style.strokeDasharray = "251.2";
            circlePath.style.strokeDashoffset = offset;
        }
        
        // 2. Render Study Timeline Banner
        if (banner) {
            banner.innerHTML = `
                <i class="ti ti-hourglass" style="font-size:24px; color:#4F46E5;"></i>
                <div>
                    <h4>Personalized Study Timeline</h4>
                    <p>${data.study_timeline.timeline_summary}</p>
                </div>
            `;
        }
        
        // 3. Render Skill Checklist
        let checklistHtml = "";
        
        // Render missing skills
        data.missing_skills.forEach(s => {
            checklistHtml += `
                <div class="skill-item-row gap">
                    <span style="display:flex; align-items:center; gap:6px;">
                        <i class="ti ti-x" style="color:#EF4444; font-weight:700;"></i>
                        <strong>${s.skill_name}</strong>
                    </span>
                    <span style="display:flex; align-items:center; gap:6px;">
                        <span style="font-size:10px; color:#6B7280;">Est: ${s.learning_hours} hrs</span>
                        ${s.mandatory === 'Yes' ? '<span class="badge-mandatory">Mandatory</span>' : ''}
                    </span>
                </div>
            `;
        });
        
        // Render matching skills
        data.matching_skills.forEach(s => {
            checklistHtml += `
                <div class="skill-item-row match">
                    <span style="display:flex; align-items:center; gap:6px;">
                        <i class="ti ti-check" style="color:#16A34A; font-weight:700;"></i>
                        <strong>${s.skill_name}</strong>
                    </span>
                    <span style="font-size:10px; color:#6B7280;">Possessed</span>
                </div>
            `;
        });
        
        if (data.missing_skills.length === 0 && data.matching_skills.length === 0) {
            checklistHtml = `<p style="font-size:11.5px; color:#6B7280; text-align:center;">No skills mapped in database for this role.</p>`;
        }
        
        listContainer.innerHTML = checklistHtml;
        
        // 4. Render Recommended Courses (limit 3)
        let coursesHtml = "";
        data.recommended_courses.slice(0, 3).forEach(c => {
            coursesHtml += `
                <div class="resource-card-row">
                    <div class="res-info">
                        <h5>${c.course_name}</h5>
                        <p>${c.provider} · ${c.platform} · ${c.difficulty} · ${c.duration_hours} Hours</p>
                    </div>
                    <button class="btn-primary" style="padding:6px 12px; font-size:10px;" onclick="window.open('${c.course_url || 'https://coursera.org'}', '_blank')">Enroll <i class="ti ti-external-link"></i></button>
                </div>
            `;
        });
        if (data.recommended_courses.length === 0) {
            coursesHtml = `<p style="font-size:11.5px; color:#6B7280;">No courses found matching missing skills.</p>`;
        }
        coursesList.innerHTML = coursesHtml;
        
        // 5. Render Bridging Projects (limit 3)
        let projectsHtml = "";
        data.recommended_projects.slice(0, 3).forEach(p => {
            projectsHtml += `
                <div class="resource-card-row">
                    <div class="res-info">
                        <h5>${p.project_name}</h5>
                        <p>Domain: ${p.project_domain} · Difficulty: ${p.difficulty} · Duration: ${p.estimated_duration}</p>
                        <p style="margin-top:2px; font-size:10px; color:#4B5563;">${p.description}</p>
                    </div>
                    <button class="btn-primary" style="padding:6px 12px; font-size:10px; background:#fff; color:#4F46E5; border:1px solid #ECEDF3;" onclick="showToast('Loading project codebase repository...')">Source <i class="ti ti-brand-github"></i></button>
                </div>
            `;
        });
        if (data.recommended_projects.length === 0) {
            projectsHtml = `<p style="font-size:11.5px; color:#6B7280;">No bridging projects found matching missing skills.</p>`;
        }
        projectsList.innerHTML = projectsHtml;
        
        // 6. Render Certifications
        let certsHtml = "";
        data.recommended_certifications.forEach(cert => {
            certsHtml += `
                <div class="resource-card-row">
                    <div class="res-info">
                        <h5>${cert.certification_name}</h5>
                        <p>Provider: ${cert.provider} · Difficulty: ${cert.difficulty_level || 'Intermediate'} · Cost: ${cert.cost || 'Free'}</p>
                    </div>
                    <button class="btn-primary" style="padding:6px 12px; font-size:10px;" onclick="window.open('${cert.url || 'https://google.com'}', '_blank')">Guide <i class="ti ti-external-link"></i></button>
                </div>
            `;
        });
        if (data.recommended_certifications.length === 0) {
            certsHtml = `<p style="font-size:11.5px; color:#6B7280;">No certifications mapped for this target role.</p>`;
        }
        certsList.innerHTML = certsHtml;
        
    } catch (err) {
        console.error("Error populating skill gap analysis page:", err);
    }
}

})();
