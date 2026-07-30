/* =======================================================
   AI Career Guidance - Industry Trends Page Controller
   ======================================================= */

(() => {
const API_TRENDS = (window.getApiBaseUrl ? window.getApiBaseUrl() : (window.location.origin + "/api"));

function initTrendsPage() {
    loadTrends();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTrendsPage);
} else {
    initTrendsPage();
}

async function loadTrends(roleId = "") {
    const container = document.getElementById("trendsContainer");
    const summaryText = document.getElementById("trendsSummaryText");
    if (!container) return;

    container.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <i class="ti ti-loader-2 animate-spin" style="font-size: 32px; color: var(--indigo);"></i>
            <div style="margin-top: 10px; font-size: 13px; color: var(--text-2);">Loading market insights...</div>
        </div>
    `;

    try {
        let url = `${API_TRENDS}/industry-trends`;
        if (roleId) {
            url += `?role_id=${roleId}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error("Failed to fetch industry trends");
        
        const data = await response.json();
        
        if (summaryText) {
            summaryText.textContent = `Found ${data.length} trend records`;
        }

        if (data.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-3);">
                    <i class="ti ti-database-off" style="font-size: 40px;"></i>
                    <p style="margin-top: 10px;">No trend records match this filter.</p>
                </div>
            `;
            return;
        }

        let html = "";
        data.forEach(trend => {
            // Badges color parsing
            let demandClass = "progress";
            if (trend.hiring_demand.toLowerCase() === "high" || trend.hiring_demand.toLowerCase() === "critical") {
                demandClass = "high";
            } else if (trend.hiring_demand.toLowerCase() === "medium") {
                demandClass = "medium";
            } else {
                demandClass = "low";
            }

            let growthClass = trend.future_growth.includes("High") ? "var(--green)" : "var(--indigo)";
            
            html += `
                <div class="panel reveal" style="padding: 24px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                            <span class="badge ${demandClass}">${trend.hiring_demand} Demand</span>
                            <span class="badge" style="background: rgba(59, 130, 246, 0.1); color: var(--blue);">${trend.industry}</span>
                        </div>
                        
                        <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 8px; color: var(--text);">${trend.trend_title}</h3>
                        <div style="font-size: 11.5px; font-weight: 600; color: var(--indigo); text-transform: uppercase; margin-bottom: 10px;">${trend.role_name}</div>
                        
                        <p style="font-size: 13px; color: var(--text-2); line-height: 1.5; margin-bottom: 15px;">${trend.trend_description}</p>
                        
                        <div style="background: var(--bg-page); border-radius: var(--radius); padding: 12px; margin-bottom: 15px; border: 1px solid var(--border);">
                            <div style="display: flex; justify-content: space-between; font-size: 12.5px; margin-bottom: 6px;">
                                <span style="color: var(--text-2);"><i class="ti ti-cash"></i> Avg India Salary:</span>
                                <strong style="color: var(--text);">${trend.average_salary_india_lpa} LPA</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 12.5px; margin-bottom: 6px;">
                                <span style="color: var(--text-2);"><i class="ti ti-world"></i> Global Salary:</span>
                                <strong style="color: var(--text);">$${trend.average_salary_global_usd.toLocaleString()}</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; font-size: 12.5px;">
                                <span style="color: var(--text-2);"><i class="ti ti-shield-alert"></i> Automation Risk:</span>
                                <strong style="color: ${trend.automation_risk.includes('Low') ? 'var(--green)' : 'var(--red)'}">${trend.automation_risk}</strong>
                            </div>
                        </div>

                        <div style="margin-bottom: 12px;">
                            <span style="font-size: 12px; font-weight: 700; color: var(--text-2); display: block; margin-bottom: 6px;">Required Skills:</span>
                            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                ${trend.required_skills.split(',').map(s => `<span class="badge progress" style="font-size: 10px; background: rgba(0, 0, 0, 0.05); color: var(--text);">${s.trim()}</span>`).join('')}
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 15px; border-top: 1px solid var(--border); padding-top: 12px;">
                        <span style="font-size: 11px; font-weight: 700; color: var(--text-3); text-transform: uppercase; display: block; margin-bottom: 6px;">Top Companies Hiring:</span>
                        <div style="font-size: 12.5px; font-weight: 600; color: var(--text-2);"><i class="ti ti-building"></i> ${trend.top_companies}</div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;

    } catch (err) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--red);">
                <i class="ti ti-alert-circle" style="font-size: 40px;"></i>
                <p style="margin-top: 10px;">Error loading trends: ${err.message}</p>
            </div>
        `;
    }
}

window.filterTrends = (roleId) => {
    loadTrends(roleId);
};

})();
