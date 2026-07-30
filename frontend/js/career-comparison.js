/* =======================================================
   AI Career Guidance - Career Comparison Page Controller
   ======================================================= */

const API_COMPARISON = "http://localhost:5000/api";

function initComparisonPage() {
    // Initial compare run on load
    triggerComparison();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initComparisonPage);
} else {
    initComparisonPage();
}

async function triggerComparison() {
    const role1 = document.getElementById("compareRole1")?.value;
    const role2 = document.getElementById("compareRole2")?.value;
    const resultsPanel = document.getElementById("comparisonResultsPanel");
    
    if (!role1 || !role2 || !resultsPanel) return;

    // Show panel with loaders
    resultsPanel.style.display = "block";
    
    document.getElementById("role1Name").textContent = "Loading...";
    document.getElementById("role2Name").textContent = "Loading...";
    document.getElementById("salaryCompareText").innerHTML = `<i class="ti ti-loader-2 animate-spin"></i>`;
    document.getElementById("growthCompareText").textContent = "...";
    document.getElementById("difficultyCompareText").textContent = "...";
    document.getElementById("remoteCompareText").textContent = "...";
    document.getElementById("balanceCompareText").textContent = "...";
    document.getElementById("bestForText").textContent = "...";
    document.getElementById("comparisonSummaryText").textContent = "Fetching comparison metrics...";

    try {
        const response = await fetch(`${API_COMPARISON}/career-comparison?role_1_id=${role1}&role_2_id=${role2}`);
        if (!response.ok) throw new Error("Failed to load comparison data");

        const data = await response.json();

        // 1. Populate Names
        document.getElementById("role1Name").textContent = data.role_1_name;
        document.getElementById("role2Name").textContent = data.role_2_name;
        document.getElementById("comparisonTitle").textContent = `Career Face-Off: ${data.role_1_name} VS ${data.role_2_name}`;

        // 2. Populate side-by-side lists
        const r1Skills = document.getElementById("role1Skills");
        const r2Skills = document.getElementById("role2Skills");
        
        if (r1Skills) {
            r1Skills.innerHTML = "";
            data.required_skills_role_1.split(',').forEach(s => {
                r1Skills.innerHTML += `<span class="badge progress" style="background: rgba(99, 102, 241, 0.1); color: var(--indigo); font-size: 11px;">${s.trim()}</span>`;
            });
        }
        if (r2Skills) {
            r2Skills.innerHTML = "";
            data.required_skills_role_2.split(',').forEach(s => {
                r2Skills.innerHTML += `<span class="badge progress" style="background: rgba(168, 85, 247, 0.1); color: var(--secondary); font-size: 11px;">${s.trim()}</span>`;
            });
        }

        // 3. Populate rows
        document.getElementById("salaryCompareText").textContent = data.salary_comparison;
        document.getElementById("growthCompareText").textContent = data.job_growth;
        document.getElementById("difficultyCompareText").textContent = data.difficulty_to_enter;
        document.getElementById("remoteCompareText").textContent = data.remote_opportunities;
        document.getElementById("balanceCompareText").textContent = data.work_life_balance;
        document.getElementById("bestForText").textContent = data.best_for;
        document.getElementById("comparisonSummaryText").textContent = data.summary;

    } catch (err) {
        console.error("Comparison load error:", err);
        document.getElementById("comparisonSummaryText").innerHTML = `<span style="color:var(--red);"><i class="ti ti-alert-circle"></i> Error: ${err.message}</span>`;
    }
}

window.triggerComparison = triggerComparison;
