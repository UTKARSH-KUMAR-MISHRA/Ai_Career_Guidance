/* =======================================================
   AI Career Guidance - Resources / Insights Page Controller
   ======================================================= */

const API_INSIGHTS = "http://localhost:5000/api";

function initResourcesPage() {
    loadInsights();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initResourcesPage);
} else {
    initResourcesPage();
}

async function loadInsights() {
    const branchContainer = document.getElementById("branchDistContainer");
    const aspContainer = document.getElementById("topAspirationsContainer");
    const gapContainer = document.getElementById("commonGapsContainer");
    const feedbackContainer = document.getElementById("feedbackLogsContainer");
    
    if (!branchContainer || !aspContainer || !gapContainer || !feedbackContainer) return;
    
    try {
        const res = await fetch(`${API_INSIGHTS}/mentor/insights`);
        if (res.ok) {
            const data = await res.json();
            
            // 1. Render Branch distribution
            let branchHtml = "";
            const branches = data.branch_distribution || {};
            const maxBranchCount = Math.max(...Object.values(branches), 1);
            
            for (const [branch, count] of Object.entries(branches)) {
                const pct = Math.round((count / maxBranchCount) * 100);
                branchHtml += `
                    <div style="margin-bottom: 12px;">
                        <div class="metric-row" style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px;"><strong>${branch}</strong> <span style="color:var(--indigo); font-weight:700;">${count} Students</span></div>
                        <div class="metric-bar-wrap" style="height:6px; background:rgba(0,0,0,0.05); border-radius:3px; overflow:hidden;"><div class="metric-bar-fill" style="height:100%; background:var(--indigo); width:${pct}%; transition:width 1s ease;"></div></div>
                    </div>
                `;
            }
            branchContainer.innerHTML = branchHtml || "<p>No student branch distribution logged.</p>";
            
            // 2. Render Top aspirations
            let aspHtml = "";
            const aspirations = data.top_aspirations || {};
            const maxAspCount = Math.max(...Object.values(aspirations), 1);
            
            for (const [role, count] of Object.entries(aspirations)) {
                const pct = Math.round((count / maxAspCount) * 100);
                aspHtml += `
                    <div style="margin-bottom: 12px;">
                        <div class="metric-row" style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px;"><strong>${role}</strong> <span style="color:var(--green); font-weight:700;">${count} Students</span></div>
                        <div class="metric-bar-wrap" style="height:6px; background:rgba(0,0,0,0.05); border-radius:3px; overflow:hidden;"><div class="metric-bar-fill" style="height:100%; background:var(--green); width:${pct}%; transition:width 1s ease;"></div></div>
                    </div>
                `;
            }
            aspContainer.innerHTML = aspHtml || "<p>No aspirations logged.</p>";
            
            // 3. Render common gaps
            let gapHtml = "";
            if (data.common_skill_gaps && data.common_skill_gaps.length > 0) {
                data.common_skill_gaps.forEach(g => {
                    gapHtml += `
                        <div class="metric-row" style="border-left:3px solid var(--red); padding-left:10px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                            <strong style="font-size:12px;">${g.skill_name}</strong>
                            <span style="font-size:10px; color:var(--red); font-weight:700; text-transform:uppercase;">${g.importance}</span>
                        </div>
                    `;
                });
            }
            gapContainer.innerHTML = gapHtml || "<p>No skill gaps logged.</p>";
            
            // 4. Render recent feedback entries
            let fbHtml = "";
            if (data.recent_feedback && data.recent_feedback.length > 0) {
                data.recent_feedback.forEach(f => {
                    const icon = f.rating === 'up' ? 'ti-thumb-up' : 'ti-thumb-down';
                    const color = f.rating === 'up' ? 'var(--green)' : 'var(--red)';
                    const bg = f.rating === 'up' ? 'var(--green-bg)' : 'var(--red-bg)';
                    fbHtml += `
                        <div class="metric-row" style="display:block; padding:10px; margin-bottom:8px; border-radius:8px; border:1px solid var(--border); background:rgba(0,0,0,0.01);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px; width:100%;">
                                <strong style="color:var(--text); font-size:11.5px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:85%;">Query: "${f.query}"</strong>
                                <span style="display:inline-flex; align-items:center; justify-content:center; width:20px; height:20px; border-radius:50%; background:${bg}; color:${color}; font-size:11px;"><i class="ti ${icon}"></i></span>
                            </div>
                            <p style="margin:0; font-size:11px; color:var(--text-2); font-style:italic;">Response: "${f.response.substring(0, 80)}..."</p>
                        </div>
                    `;
                });
            } else {
                fbHtml = `<p style="font-size:11.5px; color:var(--text-3); text-align:center; margin:30px 0;">No student feedback has been logged yet.</p>`;
            }
            feedbackContainer.innerHTML = fbHtml;
        }
    } catch (err) {
        console.error("Failed to load mentor insights:", err);
    }
}
