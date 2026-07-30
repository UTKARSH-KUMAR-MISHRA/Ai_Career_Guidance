/* =======================================================
   AI Career Guidance - Jobs Page Controller
   ======================================================= */

(() => {
const API_JOBS_URL = "http://localhost:5000/api";
let allJobs = [];

function initJobsPage() {
    loadJobs();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initJobsPage);
} else {
    initJobsPage();
}

async function loadJobs() {
    const grid = document.getElementById("jobsGrid");
    if (!grid) return;

    grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <i class="ti ti-loader-2 animate-spin" style="font-size: 32px; color: var(--indigo);"></i>
            <div style="margin-top: 10px; font-size: 13px; color: var(--text-2);">Loading tailored job openings...</div>
        </div>
    `;

    try {
        // Retrieve current target role ID from window target state or first recommendation
        let targetRoleId = window.selectedTargetRoleId || "";
        if (!targetRoleId) {
            const recRes = await fetch(`${API_JOBS_URL}/recommendations`);
            if (recRes.ok) {
                const recs = await recRes.json();
                if (recs.length > 0) {
                    targetRoleId = recs[0].role_id;
                }
            }
        }

        const res = await fetch(`${API_JOBS_URL}/jobs?role_id=${targetRoleId}`);
        if (!res.ok) throw new Error("Failed to fetch jobs list");

        allJobs = await res.json();
        renderJobs(allJobs);
        setupFilterListeners();

    } catch (err) {
        console.error(err);
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--red);">
                <i class="ti ti-alert-circle" style="font-size: 40px;"></i>
                <p style="margin-top: 10px;">Error loading job openings: ${err.message}</p>
            </div>
        `;
    }
}

function renderJobs(jobsList) {
    const grid = document.getElementById("jobsGrid");
    if (!grid) return;

    if (jobsList.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 45px; color: var(--text-3);">
                <i class="ti ti-briefcase" style="font-size: 44px; margin-bottom: 8px; opacity: 0.8;"></i>
                <p>No job recommendations match the current search filters.</p>
            </div>
        `;
        return;
    }

    let html = "";
    jobsList.forEach(job => {
        const skillsList = job.skills_required ? job.skills_required.split(',') : [];
        const skillsBadges = skillsList.map(s => 
            `<span class="badge progress" style="font-size:9.5px; background:rgba(79,70,229,0.06); color:var(--indigo); padding:3px 8px;">${s.trim()}</span>`
        ).join(' ');

        const typeClass = job.job_type.toLowerCase() === "internship" ? "medium" : "high";

        html += `
            <div class="panel reveal" style="padding: 24px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <span class="badge ${typeClass}">${job.job_type}</span>
                        <strong style="color: var(--green); font-size: 13.5px;">${job.salary_range}</strong>
                    </div>

                    <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 4px; color: var(--text);">${job.job_title}</h3>
                    <div style="font-size: 13px; font-weight: 600; color: var(--indigo); margin-bottom: 10px;">${job.company_name}</div>
                    
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-3); margin-bottom: 14px;">
                        <i class="ti ti-map-pin"></i> <span>${job.location}</span>
                        <span style="margin: 0 4px;">·</span>
                        <i class="ti ti-briefcase"></i> <span>${job.experience_level}</span>
                    </div>

                    <p style="font-size: 13px; color: var(--text-2); line-height: 1.55; margin-bottom: 15px;">${job.description}</p>

                    <div style="margin-bottom: 15px;">
                        <span style="font-size: 11px; font-weight: 700; color: var(--text-3); display: block; margin-bottom: 6px;">Skills Required:</span>
                        <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                            ${skillsBadges}
                        </div>
                    </div>
                </div>

                <div style="border-top: 1px solid var(--border); padding-top: 15px; margin-top: 10px;">
                    <button class="start-btn" onclick="applyToJob('${job.job_title}', '${job.company_name}')" style="width: 100%; padding: 10px;">
                        Apply Now <i class="ti ti-arrow-up-right"></i>
                    </button>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
}

function setupFilterListeners() {
    const searchInput = document.getElementById("jobSearchInput");
    const typeFilter = document.getElementById("jobTypeFilter");
    const locationFilter = document.getElementById("jobLocationFilter");

    if (!searchInput || !typeFilter || !locationFilter) return;

    const filterHandler = () => {
        const query = searchInput.value.toLowerCase().trim();
        const type = typeFilter.value;
        const location = locationFilter.value;

        const filtered = allJobs.filter(job => {
            const matchesQuery = !query || 
                job.job_title.toLowerCase().includes(query) || 
                job.company_name.toLowerCase().includes(query) ||
                (job.skills_required && job.skills_required.toLowerCase().includes(query));

            const matchesType = type === "All" || job.job_type === type;
            const matchesLocation = location === "All" || job.location === location;

            return matchesQuery && matchesType && matchesLocation;
        });

        renderJobs(filtered);
    };

    searchInput.addEventListener("input", filterHandler);
    typeFilter.addEventListener("change", filterHandler);
    locationFilter.addEventListener("change", filterHandler);
}

window.applyToJob = function(title, company) {
    if (window.showToast) {
        window.showToast(`Applied successfully to ${title} at ${company}!`);
    } else {
        alert(`Applied successfully to ${title} at ${company}!`);
    }
};

})();
