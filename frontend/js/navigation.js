/* =======================================================
   AI Career Guidance - Shared Navigation & Profile Swifter
   ======================================================= */

const API_BASE = "http://localhost:5000/api";

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
});

async function initNavigation() {
    // Determine path prefixes based on folder depth
    const isPagesDir = window.location.pathname.includes("/pages/");
    const prefix = isPagesDir ? "" : "pages/";
    const rootPrefix = isPagesDir ? "../" : "";
    
    // 1. Render Sidebar
    const sidebar = document.querySelector(".sidebar");
    if (sidebar) {
        // Get active index based on title or URL
        const title = document.title.toLowerCase();
        let activeIdx = 0; // Dashboard
        if (title.includes("profile")) activeIdx = 1;
        else if (title.includes("recommendation")) activeIdx = 2;
        else if (title.includes("skill gap") || title.includes("gap")) activeIdx = 3;
        else if (title.includes("roadmap")) activeIdx = 4;
        else if (title.includes("chatbot") || title.includes("chat")) activeIdx = 5;
        else if (title.includes("interview")) activeIdx = 6;
        else if (title.includes("resource") || title.includes("insight")) activeIdx = 7;
        
        sidebar.innerHTML = `
            <div class="brand" onclick="window.location.href='${rootPrefix}index.html'">
                <div class="logo"><i class="ti ti-school"></i></div>
                <div>ENGINEERING CAREER<br><small>DEVELOPMENT PORTAL</small></div>
            </div>
            <ul class="nav">
                <li class="${activeIdx === 0 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}index.html'">
                    <i class="ti ti-layout-dashboard"></i>Dashboard
                </li>
                <li class="${activeIdx === 1 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}${prefix}profile.html'">
                    <i class="ti ti-user"></i>Profile
                </li>
                <li class="${activeIdx === 2 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}${prefix}recommendation.html'">
                    <i class="ti ti-target-arrow"></i>Recommendations
                </li>
                <li class="${activeIdx === 3 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}${prefix}skill-gap.html'">
                    <i class="ti ti-chart-radar"></i>Skill Gap Analysis
                </li>
                <li class="${activeIdx === 4 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}${prefix}roadmap.html'">
                    <i class="ti ti-map"></i>Roadmap
                </li>
                <li class="${activeIdx === 5 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}${prefix}chatbot.html'">
                    <i class="ti ti-message-chatbot"></i>AI Career Chatbot
                </li>
                <li class="${activeIdx === 6 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}${prefix}interview.html'">
                    <i class="ti ti-users"></i>Interview Prep
                </li>
                <li class="${activeIdx === 7 ? 'active' : ''}" onclick="window.location.href='${rootPrefix}${prefix}resources.html'">
                    <i class="ti ti-chart-line"></i>Placement Insights
                </li>
            </ul>
            <div class="help-card">
                <div class="bot"><i class="ti ti-robot"></i></div>
                <h4>Need help?</h4>
                <p>Chat with our RAG career chatbot anytime!</p>
                <button onclick="window.location.href='${rootPrefix}${prefix}chatbot.html'">Ask chatbot <i class="ti ti-arrow-right"></i></button>
            </div>
        `;
    }

    // 2. Fetch Active Student Profile
    let activeProfile = {};
    try {
        const res = await fetch(`${API_BASE}/profile`);
        if (res.ok) {
            const data = await res.json();
            activeProfile = data.normalized;
        }
    } catch (err) {
        console.error("Failed to load active profile from API, loading fallback from localStorage:", err);
        // Fallback to local storage
        activeProfile = JSON.parse(localStorage.getItem("careerProfileNormalized")) || {
            name: "Ananya Singh",
            branch: "CSE",
            year: 3,
            cgpa: 8.12
        };
    }

    // 3. Render Topbar contents
    const topbar = document.querySelector(".topbar");
    if (topbar) {
        const topbarTitle = topbar.querySelector("h1")?.textContent || "Dashboard";
        const subtitle = topbar.querySelector("p, .sub")?.textContent || `Welcome back, ${activeProfile.name}! 👋`;
        
        topbar.innerHTML = `
            <div>
                <h1>${topbarTitle}</h1>
                <div class="sub">${subtitle}</div>
            </div>
            <div class="topbar-right" style="display:flex; align-items:center; gap:12px;">
                <!-- Student Swifter Switcher -->
                <div class="student-select-wrap" style="display:flex; align-items:center; gap:6px; background:#fff; padding:6px 12px; border-radius:18px; border:1px solid #ECEDF3;">
                    <i class="ti ti-users" style="color:#4F46E5; font-size:15px;"></i>
                    <select id="studentSelect" style="border:none; outline:none; font-size:12px; font-weight:600; cursor:pointer; background:transparent; color:#111827;">
                        <option value="">Switch Student...</option>
                    </select>
                </div>
                <button class="voice-btn" id="navVoiceBtn" style="display:flex; align-items:center; gap:6px; background:#EEF0FF; color:#4F46E5; border:none; padding:8px 14px; border-radius:18px; font-size:12.5px; font-weight:600; cursor:pointer;">
                    <i class="ti ti-microphone"></i> <span id="navVoiceLabel">Voice</span>
                </button>
                <div class="profile" onclick="window.location.href='${rootPrefix}${prefix}profile.html'" style="display:flex; align-items:center; gap:8px; cursor:pointer;">
                    <div class="avatar" style="width:33px; height:33px; border-radius:50%; background:linear-gradient(135deg,#6C63FF,#4F46E5); display:flex; align-items:center; justify-content:center; color:#fff; font-weight:600; font-size:12px;">
                        ${activeProfile.name.split(' ').map(x=>x[0]).join('').substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                        <div class="profile-name" style="font-size:12.5px; font-weight:700;">${activeProfile.name}</div>
                        <div class="profile-sub" style="font-size:11px; color:#9CA3AF;">${activeProfile.branch} · Year ${activeProfile.year}</div>
                    </div>
                </div>
            </div>
        `;
        
        // Populate Student switcher options
        loadStudentOptions();
        
        // Voice Assistant listener trigger
        const voiceBtn = document.getElementById("navVoiceBtn");
        if (voiceBtn) {
            voiceBtn.addEventListener("click", () => {
                window.location.href = `${rootPrefix}${prefix}chatbot.html?voice=true`;
            });
        }
    }
}

async function loadStudentOptions() {
    const selector = document.getElementById("studentSelect");
    if (!selector) return;
    
    try {
        const res = await fetch(`${API_BASE}/students`);
        if (res.ok) {
            const list = await res.json();
            list.forEach(student => {
                const opt = document.createElement("option");
                opt.value = student.id;
                opt.textContent = `${student.name} (${student.branch} - Yr ${student.year})`;
                opt.dataset.isExcel = student.is_excel;
                selector.appendChild(opt);
            });
            
            // Set currently selected
            const activeRes = await fetch(`${API_BASE}/profile`);
            if (activeRes.ok) {
                const activeData = await activeRes.json();
                const activeId = activeData.raw.student_id || activeData.raw.email_id;
                if (activeId) {
                    selector.value = activeId;
                }
            }
        }
    } catch (err) {
        console.error("Failed to load student profiles switcher options:", err);
    }
    
    selector.addEventListener("change", async (e) => {
        const id = e.target.value;
        if (!id) return;
        
        const opt = e.target.selectedOptions[0];
        const isExcel = opt.dataset.isExcel === 'true';
        
        // Fetch all students and locate the target student
        try {
            const sRes = await fetch(`${API_BASE}/students`);
            if (sRes.ok) {
                const list = await sRes.json();
                // We fetch the detailed structure from backend tables or reload active
                let fullProfile = {};
                
                // Read from backend directly using SQL or matching
                // Send a request to change active student
                // The app backend handles matching
                const responseList = await fetch(`${API_BASE}/students`);
                
                // Make a call to POST /api/profile
                // For simplicity, we can query details from backend or let backend set active directly
                // Let's query backend for standard profile or build it
                let targetData = {};
                if (isExcel) {
                    targetData = { email_id: id, is_excel: true };
                } else {
                    targetData = { student_id: id, is_excel: false };
                }
                
                // Wait, let's write a backend handler to fetch the exact student row on POST
                // Yes, we will let the backend fetch it by loading the full profile row
                // To keep it simple, we POST a JSON with {'student_id': id, 'is_excel': isExcel}
                // and our /api/profile POST endpoint in app.py will resolve the full record and save it!
                // Let's modify app.py's profile POST to handle loading from database when id is provided!
                // Yes! That's incredibly elegant!
                const postRes = await fetch(`${API_BASE}/profile`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        resolve_id: id,
                        is_excel: isExcel
                    })
                });
                
                if (postRes.ok) {
                    // Save local state copy too for safety
                    const activeData = await postRes.json();
                    showToast("Switched student profile!");
                    setTimeout(() => window.location.reload(), 800);
                }
            }
        } catch (err) {
            console.error("Failed to switch student:", err);
        }
    });
}

function showToast(msg) {
    let toast = document.getElementById("toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "toast";
        toast.className = "toast";
        toast.innerHTML = `<i class="ti ti-circle-check"></i><span id="toastMsg"></span>`;
        document.body.appendChild(toast);
    }
    document.getElementById("toastMsg").textContent = msg;
    toast.classList.add("show");
    
    // Set styling if missing
    toast.style.position = "fixed";
    toast.style.bottom = "22px";
    toast.style.right = "22px";
    toast.style.background = "#181B33";
    toast.style.color = "#fff";
    toast.style.padding = "10px 16px";
    toast.style.borderRadius = "10px";
    toast.style.fontSize = "12.5px";
    toast.style.display = "flex";
    toast.style.alignItems = "center";
    toast.style.gap = "8px";
    toast.style.boxShadow = "0 12px 28px rgba(0,0,0,.25)";
    toast.style.zIndex = "1000";
    toast.style.transition = "transform .3s ease, opacity .3s ease";
    
    clearTimeout(window._t);
    window._t = setTimeout(() => toast.classList.remove("show"), 2200);
}
