/* =======================================================
   AI Career Guidance - Courses Page Controller
   ======================================================= */

(() => {
const API_COURSES = (window.getApiBaseUrl ? window.getApiBaseUrl() : (window.location.origin + "/api"));
let allCourses = [];

function initCoursesPage() {
    loadCoursesCatalog();
    
    const search = document.getElementById("courseSearch");
    if (search) {
        // Remove existing listener if any
        search.replaceWith(search.cloneNode(true));
        const newSearch = document.getElementById("courseSearch");
        newSearch.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            filterCourses(query);
        });
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCoursesPage);
} else {
    initCoursesPage();
}

async function loadCoursesCatalog() {
    const grid = document.getElementById("coursesCatalogGrid");
    if (!grid) return;
    
    grid.innerHTML = `
        <div style="grid-column: span 3; text-align: center; padding: 40px; color: var(--text-3);">
            <i class="ti ti-loader animate-spin" style="font-size: 32px; color: var(--indigo);"></i>
            <p style="margin-top: 10px;">Querying catalog database...</p>
        </div>
    `;
    
    try {
        const res = await fetch(`${API_COURSES}/courses`);
        if (res.ok) {
            allCourses = await res.json();
            renderCourses(allCourses);
        } else {
            grid.innerHTML = `<div style="grid-column:span 3; text-align:center; padding:40px; color:var(--red);">Failed to query course records.</div>`;
        }
    } catch (err) {
        console.error("Failed to query catalog:", err);
        grid.innerHTML = `<div style="grid-column:span 3; text-align:center; padding:40px; color:var(--red);">Database catalog connection error.</div>`;
    }
}

function renderCourses(list) {
    const grid = document.getElementById("coursesCatalogGrid");
    if (!grid) return;
    
    if (list.length === 0) {
        grid.innerHTML = `<div style="grid-column:span 3; text-align:center; padding:40px; color:var(--text-3);">No courses found matching filter criteria.</div>`;
        return;
    }
    
    let html = "";
    list.forEach(c => {
        html += `
            <div class="course-catalog-card panel" style="display: flex; flex-direction: column; justify-content: space-between; padding: 18px;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="platform-lbl">${c.platform}</span>
                        <span style="font-size:11px; color:var(--green); font-weight:700;">★ ${c.rating || '4.5'}</span>
                    </div>
                    <h4 style="margin:0 0 6px; font-size:13.5px; font-weight:700; color:var(--text); line-height:1.45;">${c.course_name}</h4>
                    <p style="margin:0 0 8px; font-size:11px; color:var(--text-2);">Skill Focus: <strong>${c.skill_name || 'General'}</strong></p>
                    
                    <div style="font-size:11px; color:var(--text-2); display:flex; gap:12px; margin-bottom:12px;">
                        <span>⏱ ${c.duration_hours} hrs</span>
                        <span>📶 ${c.difficulty}</span>
                        <span>💰 ${c.price || 'Free'}</span>
                    </div>
                </div>
                
                <button class="start-btn" style="width:100%; padding:8px;" onclick="window.open('${c.course_url || 'https://coursera.org'}', '_blank')">Enroll Course <i class="ti ti-external-link"></i></button>
            </div>
        `;
    });
    grid.innerHTML = html;
}

function filterCourses(query) {
    if (!query) {
        renderCourses(allCourses);
        return;
    }
    
    const filtered = allCourses.filter(c => {
        const nameMatch = c.course_name.toLowerCase().includes(query);
        const skillMatch = (c.skill_name || "").toLowerCase().includes(query);
        const platformMatch = c.platform.toLowerCase().includes(query);
        return nameMatch || skillMatch || platformMatch;
    });
    
    renderCourses(filtered);
}

})();
