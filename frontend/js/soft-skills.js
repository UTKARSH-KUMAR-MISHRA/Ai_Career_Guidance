/* =======================================================
   AI Career Guidance - Soft Skills Page Controller
   ======================================================= */

(() => {
const API_SOFTSKILLS = "http://localhost:5000/api";

function initSoftSkillsPage() {
    loadSoftSkills();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSoftSkillsPage);
} else {
    initSoftSkillsPage();
}

async function loadSoftSkills() {
    const grid = document.getElementById("softSkillsGrid");
    if (!grid) return;

    grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <i class="ti ti-loader-2 animate-spin" style="font-size: 32px; color: var(--indigo);"></i>
            <div style="margin-top: 10px; font-size: 13px; color: var(--text-2);">Loading soft skills catalogue...</div>
        </div>
    `;

    try {
        const response = await fetch(`${API_SOFTSKILLS}/soft-skills`);
        if (!response.ok) throw new Error("Failed to fetch soft skills");

        const data = await response.json();

        if (data.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-3);">
                    <i class="ti ti-heart" style="font-size: 40px;"></i>
                    <p style="margin-top: 10px;">No soft skills registered in database.</p>
                </div>
            `;
            return;
        }

        // Refine soft skills to a concise, highly relevant subset of core skills
        const refinedSkills = data.filter(s => 
            (s.importance && s.importance.toLowerCase().includes("high")) || 
            ["communication", "leadership", "adaptability", "problem solving", "teamwork"].some(k => s.skill_name.toLowerCase().includes(k))
        ).slice(0, 4);

        const skillsToDisplay = refinedSkills.length > 0 ? refinedSkills : data.slice(0, 4);

        let html = "";
        skillsToDisplay.forEach(skill => {
            let importanceClass = "medium";
            if (skill.importance.toLowerCase() === "high" || skill.importance.toLowerCase() === "very high") {
                importanceClass = "high";
            } else if (skill.importance.toLowerCase() === "low") {
                importanceClass = "low";
            }

            // Recommended roles list to badges
            const rolesList = skill.recommended_roles ? skill.recommended_roles.split(';') : [];
            const rolesMarkup = rolesList.map(role => 
                `<span class="badge progress" style="font-size:9.5px; background:rgba(0,0,0,0.04); color:var(--text-2); padding:3px 8px;">${role.trim()}</span>`
            ).join('');

            html += `
                <div class="panel reveal" style="padding: 24px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                            <span class="badge ${importanceClass}">${skill.importance} Priority</span>
                            <span class="badge" style="background: rgba(168, 85, 247, 0.1); color: var(--secondary);">${skill.category}</span>
                        </div>

                        <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 8px; color: var(--text);">${skill.skill_name}</h3>
                        <p style="font-size: 13px; color: var(--text-2); line-height: 1.5; margin-bottom: 15px;">${skill.description}</p>

                        <div style="background: var(--bg-page); border-radius: var(--radius); padding: 12px; margin-bottom: 15px; border: 1px solid var(--border); font-size: 12.5px;">
                            <div style="margin-bottom: 6px;">
                                <strong style="color: var(--indigo);"><i class="ti ti-bulb"></i> Practice Activity:</strong>
                                <div style="color: var(--text); margin-top: 2px;">${skill.practice_activity}</div>
                            </div>
                            <div>
                                <strong style="color: var(--green);"><i class="ti ti-book"></i> Recommended Resource:</strong>
                                <div style="color: var(--text); margin-top: 2px;">${skill.improvement_resources}</div>
                            </div>
                        </div>

                        <div style="margin-bottom: 10px;">
                            <span style="font-size: 11.5px; font-weight: 700; color: var(--text-2); display: block; margin-bottom: 5px;">Highly Recommended for:</span>
                            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
                                ${rolesMarkup}
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 15px; border-top: 1px solid var(--border); padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-3);">
                        <span>Assessment: ${skill.assessment_method}</span>
                        <strong style="color: var(--indigo);">${skill.industry_relevance} Relevance</strong>
                    </div>
                </div>
            `;
        });

        grid.innerHTML = html;

    } catch (err) {
        console.error(err);
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--red);">
                <i class="ti ti-alert-circle" style="font-size: 40px;"></i>
                <p style="margin-top: 10px;">Error loading soft skills: ${err.message}</p>
            </div>
        `;
    }
}

})();
