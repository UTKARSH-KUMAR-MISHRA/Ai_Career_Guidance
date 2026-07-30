/* =======================================================
   AI Career Guidance - Recommendations Page Controller
   ======================================================= */

(() => {
const API_URL = "http://localhost:5000/api";

function initRecommendationsPage() {
    setTimeout(loadRecommendations, 300);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRecommendationsPage);
} else {
    initRecommendationsPage();
}

async function loadRecommendations() {
    const grid = document.getElementById("recsGrid");
    if (!grid) return;
    
    try {
        const res = await fetch(`${API_URL}/recommendations`);
        if (!res.ok) {
            grid.innerHTML = `<div style="grid-column:span 2; text-align:center; padding:40px; color:#EF4444;">Failed to calculate recommendations. Verify server status.</div>`;
            return;
        }
        
        const recommendations = await res.json();
        if (recommendations.length === 0) {
            grid.innerHTML = `<div style="grid-column:span 2; text-align:center; padding:40px; color:#6B7280;">No recommendations matched. Update your profile branch and skills.</div>`;
            return;
        }
        
        let gridHtml = "";
        recommendations.forEach(rec => {
            // Check if there are warning flags for advanced role
            const badgeClass = rec.is_advanced ? "score-badge advanced-warning" : "score-badge";
            
            // Map skill markup
            const matchingSkillsMarkup = rec.matching_skills.slice(0, 4).map(s => 
                `<span class="skill-match">✓ ${s.skill_name}</span>`
            ).join("");
            
            const missingSkillsMarkup = rec.missing_skills.slice(0, 4).map(s => 
                `<span class="skill-gap">✗ ${s.skill_name}</span>`
            ).join("");
            
            let bridgeSuggestionMarkup = "";
            if (rec.is_advanced && rec.bridge_role_suggestion) {
                // Fetch recommended bridge name or use placeholder
                // We'll translate the suggestion ID to a user friendly name
                // To keep it simple, we can display a general warning banner
                bridgeSuggestionMarkup = `
                    <div class="bridge-alert">
                        <i class="ti ti-alert-triangle"></i>
                        <span><strong>Prerequisite Alert:</strong> This role is advanced for your current level. Consider completing entry-level bridge courses first.</span>
                    </div>
                `;
            }
            
            gridHtml += `
                <div class="rec-card">
                    <div>
                        <div class="rec-header">
                            <div class="rec-title-wrap">
                                <h3>${rec.role_name}</h3>
                                <span class="rec-family">${rec.role_family}</span>
                            </div>
                            <div class="${badgeClass}">${rec.match_score}%</div>
                        </div>
                        
                        <p class="rec-details">${rec.explanation}</p>
                        
                        ${bridgeSuggestionMarkup}
                        
                        <div class="rec-meta-row">
                            <div class="meta-item">Difficulty<strong>${rec.difficulty}</strong></div>
                            <div class="meta-item">Avg Salary India<strong>${rec.salary_range}</strong></div>
                            <div class="meta-item">Future Scope<strong>${rec.future_scope}</strong></div>
                        </div>
                        
                        <div class="skills-matchup">
                            <strong>Skills Matchup:</strong><br>
                            ${matchingSkillsMarkup}
                            ${missingSkillsMarkup}
                            ${rec.missing_skills.length > 4 ? `<span style="font-size:9.5px; color:#9CA3AF; display:block; margin-top:4px;">+${rec.missing_skills.length - 4} more gaps</span>` : ''}
                        </div>
                    </div>
                    
                    <div class="action-row">
                        <button class="btn-primary" onclick="window.selectedTargetRoleId='${rec.role_id}'; window.navigateTo('skill-gap')">Analyze Gap <i class="ti ti-chart-radar"></i></button>
                        <button class="btn-primary" style="background:#fff; color:#4F46E5; border:1px solid #ECEDF3;" onclick="window.selectedTargetRoleId='${rec.role_id}'; window.navigateTo('roadmap')">View Roadmap <i class="ti ti-map"></i></button>
                    </div>
                </div>
            `;
        });
        
        grid.innerHTML = gridHtml;
        
    } catch (err) {
        console.error("Error loading recommendations page:", err);
        grid.innerHTML = `<div style="grid-column:span 2; text-align:center; padding:40px; color:#EF4444;">Could not connect to API server. verify Flask is running on port 5000.</div>`;
    }
}

})();
