/* =======================================================
   AI Career Guidance - Learning Roadmap Controller
   ======================================================= */

(() => {
const API = (window.getApiBaseUrl ? window.getApiBaseUrl() : (window.location.origin + "/api"));
let currentType = "90-Day";
let currentRoleId = "";

function initRoadmapPage() {
    setTimeout(initRoadmap, 300);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRoadmapPage);
} else {
    initRoadmapPage();
}

async function initRoadmap() {
    try {
        const params = new URLSearchParams(window.location.search);
        let roleId = window.selectedTargetRoleId || params.get("role_id");
        
        if (roleId) {
            currentRoleId = roleId;
            const recRes = await fetch(`${API}/recommendations`);
            if (recRes.ok) {
                const recs = await recRes.json();
                const matchedRole = recs.find(r => r.role_id === roleId);
                if (matchedRole) {
                    document.getElementById("roadmapTargetName").textContent = matchedRole.role_name;
                } else {
                    document.getElementById("roadmapTargetName").textContent = roleId;
                }
            }
            loadRoadmap(currentRoleId, currentType);
        } else {
            const recRes = await fetch(`${API}/recommendations`);
            if (recRes.ok) {
                const recs = await recRes.json();
                if (recs.length > 0) {
                    currentRoleId = recs[0].role_id;
                    document.getElementById("roadmapTargetName").textContent = recs[0].role_name;
                    loadRoadmap(currentRoleId, currentType);
                }
            }
        }
    } catch (err) {
        console.error("Failed to load recommendations for roadmap target:", err);
    }
}

async function loadRoadmap(roleId, type) {
    const list = document.getElementById("roadmapList");
    if (!list) return;
    
    try {
        const res = await fetch(`${API}/roadmap?role_id=${roleId}&type=${type}`);
        if (!res.ok) {
            list.innerHTML = `<div style="text-align:center; padding:40px; color:#EF4444;">Failed to load roadmap data.</div>`;
            return;
        }
        
        const steps = await res.json();
        if (steps.length === 0) {
            list.innerHTML = `<div style="text-align:center; padding:40px; color:#6B7280;">No weekly roadmap items defined for this role and duration. Try selecting another tab.</div>`;
            return;
        }
        
        let listHtml = "";
        steps.forEach(step => {
            const isCompleted = step.status === 'Completed';
            const statusClass = isCompleted ? 'status-tag completed' : 'status-tag todo';
            const statusText = isCompleted ? '✓ Completed' : 'Todo';
            
            // Build resource badges
            let resBadgesHtml = "";
            if (step.skill_name) {
                resBadgesHtml += `<span class="res-badge"><i class="ti ti-code"></i> Skill: ${step.skill_name}</span>`;
            }
            if (step.course_name) {
                resBadgesHtml += `<span class="res-badge" style="background:#EBF5FF; color:#2563EB;"><i class="ti ti-school"></i> Course: ${step.course_name}</span>`;
            }
            if (step.project_name) {
                resBadgesHtml += `<span class="res-badge" style="background:#FEF6E7; color:#C58412;"><i class="ti ti-brand-github"></i> Project: ${step.project_name}</span>`;
            }
            
            listHtml += `
                <div class="week-card" style="opacity: ${isCompleted ? 0.8 : 1};">
                    <div class="week-num-badge">
                        <h3>Wk ${step.week_number}</h3>
                        <span>${step.day_range}</span>
                    </div>
                    
                    <div class="week-content">
                        <h4>${step.topic}</h4>
                        <div style="font-size:11.5px; color:#4B5563;">
                            <strong>Milestone:</strong> ${step.milestone}
                        </div>
                        <div class="week-resources">
                            ${resBadgesHtml}
                        </div>
                    </div>
                    
                    <div class="week-action-col">
                        <span class="${statusClass}">${statusText}</span>
                        <div style="font-size:10.5px; color:#6B7280; margin-top:4px;">
                            ⏱ ${step.estimated_hours} hrs total<br>
                            <span style="font-size:10px; color:#4F46E5; font-weight:600;">~${step.days_estimate} study days</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        list.innerHTML = listHtml;
        
    } catch (err) {
        console.error("Error loading roadmap steps:", err);
        list.innerHTML = `<div style="text-align:center; padding:40px; color:#EF4444;">Error connecting to backend API.</div>`;
    }
}

window.switchRoadmapType = function(type, button) {
    // Set active tab styling
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach(t => t.classList.remove("active"));
    button.classList.add("active");
    
    currentType = type;
    if (currentRoleId) {
        loadRoadmap(currentRoleId, currentType);
    }
};

})();
