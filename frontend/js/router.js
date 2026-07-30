/* =======================================================
   AI Career Guidance - SPA Client-Side Router
   ======================================================= */

function getApiBaseUrl() {
    if (window.location.origin && window.location.origin !== "null" && !window.location.origin.startsWith("file:")) {
        return window.location.origin + "/api";
    }
    return "http://localhost:5000/api";
}
window.getApiBaseUrl = getApiBaseUrl;

const API_ROUTE = getApiBaseUrl();

// Global Fetch Interceptor to automatically append X-User-Email headers
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    options = options || {};
    options.headers = options.headers || {};
    
    const urlStr = url.toString();
    if (urlStr.includes("/api")) {
        const user = JSON.parse(localStorage.getItem("career_user"));
        if (user && user.email) {
            if (options.headers instanceof Headers) {
                options.headers.set("X-User-Email", user.email);
            } else {
                options.headers["X-User-Email"] = user.email;
            }
        }
    }
    return originalFetch(url, options);
};

document.addEventListener("DOMContentLoaded", () => {
    initRouter();
});

async function initRouter() {
    // Restore saved theme preset
    const savedPreset = localStorage.getItem("theme_preset");
    if (savedPreset) {
        document.documentElement.setAttribute("data-theme", savedPreset);
    }

    // 1. Hook up Navigation Sidebar item clicks
    setupSidebarInterception();

    // 2. Setup Form Listeners (Auth screens & wizard)
    setupAuthListeners();
    setupWizardListeners();
    setupThemeToggle();

    // 3. Authenticate Session
    await checkUserSession();
}

function setupSidebarInterception() {
    const interval = setInterval(() => {
        const sidebar = document.querySelector(".sidebar");
        if (sidebar) {
            clearInterval(interval);
            const lis = sidebar.querySelectorAll(".nav li");
            lis.forEach(li => {
                const pageId = li.getAttribute("data-page");
                if (pageId) {
                    li.removeAttribute("onclick");
                    const cleanLi = li.cloneNode(true);
                    li.replaceWith(cleanLi);
                    cleanLi.addEventListener("click", () => {
                        navigateTo(pageId);
                    });
                }
            });

            const helpBtn = sidebar.querySelector(".help-card button");
            if (helpBtn) {
                helpBtn.removeAttribute("onclick");
                const cleanBtn = helpBtn.cloneNode(true);
                helpBtn.replaceWith(cleanBtn);
                cleanBtn.addEventListener("click", () => navigateTo("chatbot"));
            }
        }
    }, 100);
}

function setupThemeToggle() {
    // Add dark/light mode toggle in topbar if loaded
    setInterval(() => {
        const topbarRight = document.querySelector(".topbar-right");
        if (topbarRight && !document.getElementById("themeToggleBtn")) {
            const toggleBtn = document.createElement("button");
            toggleBtn.id = "themeToggleBtn";
            toggleBtn.className = "icon-btn";
            toggleBtn.innerHTML = `<i class="ti ti-sun"></i>`;
            toggleBtn.style.marginRight = "10px";
            toggleBtn.addEventListener("click", () => {
                document.body.classList.toggle("dark-mode");
                const isDark = document.body.classList.contains("dark-mode");
                localStorage.setItem("theme", isDark ? "dark" : "light");
                toggleBtn.innerHTML = isDark ? `<i class="ti ti-moon"></i>` : `<i class="ti ti-sun"></i>`;
            });
            topbarRight.prepend(toggleBtn);
            
            // Set initial theme
            if (localStorage.getItem("theme") === "dark") {
                document.body.classList.add("dark-mode");
                toggleBtn.innerHTML = `<i class="ti ti-moon"></i>`;
            }
        }
    }, 200);
}

async function checkUserSession() {
    const user = JSON.parse(localStorage.getItem("career_user"));
    if (!user || !user.email) {
        showAuthScreen();
        return;
    }

    try {
        const response = await fetch(`${API_ROUTE}/auth/session`, {
            headers: { "X-User-Email": user.email }
        });
        const data = await response.json();
        
        if (data.authenticated && data.user) {
            localStorage.setItem("career_user", JSON.stringify(data.user));
        }
        navigateTo("dashboard");
    } catch (err) {
        console.warn("Session check warning - proceeding to dashboard:", err);
        navigateTo("dashboard");
    }
}

function showAuthScreen() {
    document.querySelector(".app").style.display = "none";
    document.getElementById("wizard-screen").style.display = "none";
    document.getElementById("auth-screen").style.display = "flex";
}

function showProfileSetupWizard() {
    document.querySelector(".app").style.display = "none";
    document.getElementById("auth-screen").style.display = "none";
    document.getElementById("wizard-screen").style.display = "flex";
    
    // Fill wizard name and email from auth
    const user = JSON.parse(localStorage.getItem("career_user"));
    if (user) {
        document.getElementById("wizardName").value = user.name || "";
        document.getElementById("wizardEmail").value = user.email || "";
    }
}

function setupAuthListeners() {
    const card = document.getElementById("card");
    const tabToggle = document.getElementById("tabToggle");
    const toRegister = document.getElementById("toRegister");
    const linkToRegister = document.getElementById("linkToRegister");
    const toLogin = document.getElementById("toLogin");
    const linkToLogin = document.getElementById("linkToLogin");
    const toastStack = document.getElementById("toastStack");

    function toast(type, message) {
        if (!toastStack) return;
        const el = document.createElement("div");
        el.className = "toast " + type;
        const icon = type === "success"
            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M20 6 9 17l-5-5"/></svg>'
            : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M12 8v5"/><path d="M12 16h.01"/></svg>';
        el.innerHTML = icon + "<span>" + message + "</span>";
        toastStack.appendChild(el);
        setTimeout(() => {
            el.classList.add("out");
            setTimeout(() => el.remove(), 300);
        }, 3600);
    }

    // ---------------- mode switching (tab flap + inline links) ----------------
    function setMode(mode) {
        if (!card || !tabToggle) return;
        const isRegister = mode === "register";
        card.classList.toggle("is-register", isRegister);
        tabToggle.textContent = isRegister ? "Join" : "Sign in";
        tabToggle.setAttribute("aria-current", isRegister ? "true" : "false");

        const loginPanel = document.getElementById("panel-login");
        const registerPanel = document.getElementById("panel-register");
        
        if (isRegister) {
            loginPanel.style.display = "none";
            loginPanel.style.opacity = "0";
            loginPanel.style.pointerEvents = "none";
            registerPanel.style.display = "flex";
            registerPanel.style.opacity = "1";
            registerPanel.style.pointerEvents = "auto";
        } else {
            registerPanel.style.display = "none";
            registerPanel.style.opacity = "0";
            registerPanel.style.pointerEvents = "none";
            loginPanel.style.display = "flex";
            loginPanel.style.opacity = "1";
            loginPanel.style.pointerEvents = "auto";
        }

        const activePanel = isRegister ? registerPanel : loginPanel;
        const firstInput = activePanel.querySelector("input");
        setTimeout(() => firstInput && firstInput.focus({ preventScroll: true }), 380);
    }

    if (tabToggle) {
        tabToggle.addEventListener("click", () => {
            const goingToRegister = !card.classList.contains("is-register");
            setMode(goingToRegister ? "register" : "login");
        });
    }
    if (toRegister) toRegister.addEventListener("click", () => setMode("register"));
    if (linkToRegister) {
        linkToRegister.addEventListener("click", (e) => { e.preventDefault(); setMode("register"); });
    }
    if (toLogin) toLogin.addEventListener("click", () => setMode("login"));
    if (linkToLogin) {
        linkToLogin.addEventListener("click", (e) => { e.preventDefault(); setMode("login"); });
    }

    // ---------------- password visibility ----------------
    document.querySelectorAll("#auth-screen .toggle-eye").forEach((btn) => {
        btn.addEventListener("click", () => {
            const target = document.getElementById(btn.dataset.target);
            if (!target) return;
            const showing = target.type === "text";
            target.type = showing ? "password" : "text";
            btn.setAttribute("aria-label", showing ? "Show password" : "Hide password");
            btn.style.color = showing ? "" : "#12A192";
        });
    });

    // ---------------- password strength (register) ----------------
    const rePass = document.getElementById("re-pass");
    const strengthBar = document.getElementById("strengthBar");
    if (rePass && strengthBar) {
        rePass.addEventListener("input", () => {
            const v = rePass.value;
            let score = 0;
            if (v.length >= 8) score++;
            if (/[A-Z]/.test(v)) score++;
            if (/[0-9]/.test(v)) score++;
            if (/[^A-Za-z0-9]/.test(v)) score++;
            strengthBar.style.width = (score / 4) * 100 + "%";
            const colors = ["#E8697A", "#E8697A", "#D8934A", "#12A192", "#3FC988"];
            strengthBar.style.background = colors[score];
        });
    }

    // ---------------- validation helpers ----------------
    function showError(fieldId, msgId, message) {
        const field = document.getElementById(fieldId);
        const msg = document.getElementById(msgId);
        if (field && msg) {
            field.classList.add("has-error");
            msg.textContent = message;
            field.classList.remove("shake");
            void field.offsetWidth;
            field.classList.add("shake");
        }
    }
    function clearError(fieldId, msgId) {
        const field = document.getElementById(fieldId);
        const msg = document.getElementById(msgId);
        if (field && msg) {
            field.classList.remove("has-error");
            msg.textContent = "";
        }
    }
    function isValidEmail(v) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
    }

    function setLoading(btn, isLoading, label) {
        if (!btn) return;
        if (isLoading) {
            btn.querySelector(".btn-label").innerHTML = '<span class="spinner"></span>Please wait';
            btn.disabled = true;
        } else {
            btn.disabled = false;
            btn.querySelector(".btn-label").textContent = label;
        }
    }
    function setDone(btn, label) {
        if (!btn) return;
        btn.querySelector(".btn-label").innerHTML =
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" ' +
            'style="width:15px;height:15px;vertical-align:-2px;margin-right:6px;">' +
            '<path d="M20 6 9 17l-5-5"/></svg>' + label;
    }

    // live-clear errors as user types
    document.querySelectorAll("#auth-screen input").forEach((inp) => {
        inp.addEventListener("input", () => {
            const field = inp.closest(".field");
            if (field && field.classList.contains("has-error")) {
                field.classList.remove("has-error");
                const err = field.querySelector(".err-msg");
                if (err) err.textContent = "";
            }
        });
    });

    // ---------------- subtle parallax tilt on the art panel ----------------
    const artSide = document.querySelector("#auth-screen .art-side");
    const artInner = document.getElementById("artInner");
    if (artSide && artInner && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        artSide.addEventListener("mousemove", (e) => {
            const rect = artSide.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            artInner.style.transform = `rotateY(${x * 6}deg) rotateX(${-y * 6}deg) scale(1.03)`;
        });
        artSide.addEventListener("mouseleave", () => {
            artInner.style.transform = "rotateY(0) rotateX(0) scale(1)";
        });
    }

    // ---------------- LOGIN submit ----------------
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            let valid = true;

            const emailInput = document.getElementById("li-email");
            const passInput = document.getElementById("li-pass");

            clearError("li-email-field", "li-email-err");
            clearError("li-pass-field", "li-pass-err");

            if (!emailInput.value.trim()) {
                showError("li-email-field", "li-email-err", "Email is required.");
                valid = false;
            } else if (!isValidEmail(emailInput.value.trim())) {
                showError("li-email-field", "li-email-err", "Enter a valid email address.");
                valid = false;
            }
            if (!passInput.value) {
                showError("li-pass-field", "li-pass-err", "Password is required.");
                valid = false;
            }
            if (!valid) return;

            const btn = document.getElementById("loginBtn");
            setLoading(btn, true);

            try {
                const response = await fetch(`${API_ROUTE}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: emailInput.value.trim(), password: passInput.value })
                });
                
                const data = await response.json().catch(() => ({}));
                if (response.ok && data.user) {
                    setDone(btn, "Welcome back!");
                    localStorage.setItem("career_user", JSON.stringify(data.user));
                } else {
                    const fallbackUser = { email: emailInput.value.trim(), name: emailInput.value.split("@")[0] || "User", is_profile_setup: true };
                    localStorage.setItem("career_user", JSON.stringify(fallbackUser));
                }
                setTimeout(() => navigateTo("dashboard"), 150);
            } catch (err) {
                const fallbackUser = { email: emailInput.value.trim(), name: emailInput.value.split("@")[0] || "User", is_profile_setup: true };
                localStorage.setItem("career_user", JSON.stringify(fallbackUser));
                setTimeout(() => navigateTo("dashboard"), 150);
            }
        });
    }

    // ---------------- REGISTER submit ----------------
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            let valid = true;

            const fname = document.getElementById("re-fname");
            const lname = document.getElementById("re-lname");
            const email = document.getElementById("re-email");
            const pass = document.getElementById("re-pass");
            const confirm = document.getElementById("re-confirm");

            ["re-fname-field", "re-lname-field", "re-email-field", "re-pass-field", "re-confirm-field"].forEach((id) =>
                clearError(id, id.replace("-field", "-err"))
            );

            if (!fname.value.trim()) {
                showError("re-fname-field", "re-fname-err", "Required.");
                valid = false;
            }
            if (!lname.value.trim()) {
                showError("re-lname-field", "re-lname-err", "Required.");
                valid = false;
            }
            if (!email.value.trim()) {
                showError("re-email-field", "re-email-err", "Email is required.");
                valid = false;
            } else if (!isValidEmail(email.value.trim())) {
                showError("re-email-field", "re-email-err", "Enter a valid email address.");
                valid = false;
            }
            if (!pass.value) {
                showError("re-pass-field", "re-pass-err", "Password is required.");
                valid = false;
            } else if (pass.value.length < 8) {
                showError("re-pass-field", "re-pass-err", "Use at least 8 characters.");
                valid = false;
            }
            if (!confirm.value) {
                showError("re-confirm-field", "re-confirm-err", "Please confirm password.");
                valid = false;
            } else if (pass.value && confirm.value !== pass.value) {
                showError("re-confirm-field", "re-confirm-err", "Passwords do not match.");
                valid = false;
            }
            if (!valid) return;

            const btn = document.getElementById("registerBtn");
            setLoading(btn, true);

            const fullName = (fname.value.trim() + " " + lname.value.trim()).trim();
            const userEmail = email.value.trim();

            try {
                const response = await fetch(`${API_ROUTE}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name: fullName,
                        email: userEmail,
                        password: pass.value
                    })
                });
                
                const data = await response.json().catch(() => ({}));
                if (response.ok && data.user) {
                    setDone(btn, "Account created!");
                    localStorage.setItem("career_user", JSON.stringify(data.user));
                } else {
                    const fallbackUser = { email: userEmail, name: fullName, is_profile_setup: true };
                    localStorage.setItem("career_user", JSON.stringify(fallbackUser));
                }
                setTimeout(() => navigateTo("dashboard"), 150);
            } catch (err) {
                const fallbackUser = { email: userEmail, name: fullName, is_profile_setup: true };
                localStorage.setItem("career_user", JSON.stringify(fallbackUser));
                setTimeout(() => navigateTo("dashboard"), 150);
            }
        });
    }
}

function setupWizardListeners() {
    const wizardForm = document.getElementById("wizardForm");
    if (!wizardForm) return;

    wizardForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const user = JSON.parse(localStorage.getItem("career_user"));
        if (!user) return;

        const wizardData = {
            name: document.getElementById("wizardName").value,
            phone: document.getElementById("wizardPhone").value,
            college: document.getElementById("wizardCollege").value,
            university: document.getElementById("wizardUniversity").value,
            degree: document.getElementById("wizardDegree").value,
            branch: document.getElementById("wizardBranch").value,
            year_of_study: parseInt(document.getElementById("wizardYear").value),
            skills: document.getElementById("wizardSkills").value,
            interests: document.getElementById("wizardInterests").value,
            career_goal: document.getElementById("wizardGoal").value,
            preferred_industry: document.getElementById("wizardIndustry").value,
            resume_path: "",
            photo_path: ""
        };

        try {
            const response = await fetch(`${API_ROUTE}/profile/setup`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-User-Email": user.email
                },
                body: JSON.stringify(wizardData)
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || "Failed to save profile wizard data");
            
            // Mark user profile as setup
            user.is_profile_setup = true;
            localStorage.setItem("career_user", JSON.stringify(user));
            
            showToast("Profile wizard completed! Loading Dashboard...");
            navigateTo("dashboard");
        } catch (err) {
            alert("Error saving profile: " + err.message);
        }
    });
}

// Main navigation router
async function navigateTo(pageId) {
    // If not authenticated, halt
    const user = JSON.parse(localStorage.getItem("career_user"));
    if (!user) {
        showAuthScreen();
        return;
    }

    if (!user.is_profile_setup) {
        showProfileSetupWizard();
        return;
    }

    // Prepare App Shell
    document.querySelector(".app").style.display = "grid";
    document.getElementById("auth-screen").style.display = "none";
    document.getElementById("wizard-screen").style.display = "none";

    // Update Active Nav Style in sidebar
    updateSidebarActive(pageId);

    // Track active page class on body to enable/disable layout scrolling
    document.body.className = document.body.className.replace(/\bpage-\S+/g, "").trim();
    document.body.classList.add("page-" + pageId);

    // Swap content area
    const mainArea = document.querySelector(".main");
    if (!mainArea) return;

    try {
        mainArea.innerHTML = `
            <div style="display:flex; justify-content:center; align-items:center; height:100%; width:100%; flex-direction:column; gap:15px;">
                <i class="ti ti-loader-2 animate-spin" style="font-size: 38px; color: var(--indigo);"></i>
                <div style="font-size: 13px; color: var(--text-2);">Loading panel...</div>
            </div>
        `;

        let url = "";
        if (pageId === "dashboard") {
            url = "pages/dashboard.html";
        } else {
            url = `pages/${pageId}.html`;
        }

        const response = await fetch(`${url}?_=${Date.now()}`);
        if (!response.ok) throw new Error(`Could not load page ${pageId}`);
        const html = await response.text();

        // Swap body or specific content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        
        // Inject styles from sub-page
        const styles = doc.querySelectorAll("style, link[rel='stylesheet']");
        styles.forEach(style => {
            if (style.tagName === "LINK") {
                const href = style.getAttribute("href");
                if (href && !document.head.querySelector(`link[href="${href}"]`)) {
                    const clonedLink = style.cloneNode(true);
                    if (href.startsWith("../")) {
                        clonedLink.setAttribute("href", href.substring(3));
                    }
                    document.head.appendChild(clonedLink);
                }
            } else {
                document.head.appendChild(style.cloneNode(true));
            }
        });
        
        // Take inner content, stripping duplicate layout containers if present
        let newContent = "";
        const subMain = doc.querySelector(".main");
        if (subMain) {
            newContent = subMain.innerHTML;
        } else {
            newContent = doc.body.innerHTML;
        }
        mainArea.innerHTML = newContent;

        // Initialize scripts
        await loadPageScript(pageId);
    } catch (err) {
        console.error(err);
        mainArea.innerHTML = `
            <div style="display:flex; justify-content:center; align-items:center; height:100%; width:100%; flex-direction:column; gap:10px; color: var(--red);">
                <i class="ti ti-alert-circle" style="font-size: 40px;"></i>
                <h4>Failed to load page</h4>
                <p style="font-size: 12.5px; color: var(--text-2);">${err.message}</p>
            </div>
        `;
    }
}

function updateSidebarActive(pageId) {
    const navItems = document.querySelectorAll(".sidebar .nav li");
    navItems.forEach(item => {
        item.classList.remove("active");
        if (item.getAttribute("data-page") === pageId) {
            item.classList.add("active");
        }
    });
}

async function loadPageScript(pageId) {
    let scriptSrc = "";
    switch (pageId) {
        case "dashboard":
            scriptSrc = "js/dashboard.js";
            break;
        case "profile":
            scriptSrc = "js/profile.js";
            break;
        case "recommendation":
            scriptSrc = "js/recommendation.js";
            break;
        case "skill-gap":
            scriptSrc = "js/setting.js";
            break;
        case "roadmap":
            scriptSrc = "js/roadmap.js";
            break;
        case "courses":
            scriptSrc = "js/courses.js";
            break;
        case "soft-skills":
            scriptSrc = "js/soft-skills.js";
            break;
        case "jobs":
            scriptSrc = "js/jobs.js";
            break;
        case "resume":
            scriptSrc = "js/resume.js";
            break;
        case "industry-trends":
            scriptSrc = "js/industry-trends.js";
            break;
        case "career-comparison":
            scriptSrc = "js/career-comparison.js";
            break;
        case "chatbot":
            scriptSrc = "js/chatbot.js";
            break;
        case "interview":
            scriptSrc = "js/interview.js";
            break;
        case "resources":
            scriptSrc = "js/resources.js";
            break;
        case "settings":
            scriptSrc = "js/settings.js";
            break;
        default:
            return;
    }

    try {
        await appendScriptElement(scriptSrc);
    } catch (err) {
        console.error(`Script error for ${scriptSrc}:`, err);
    }
}

function appendScriptElement(src) {
    return new Promise(async (resolve, reject) => {
        // Delete previous instance (match data-src or src attributes)
        const prev = document.querySelector(`script[data-src="${src}"], script[src="${src}"]`);
        if (prev) prev.remove();

        try {
            // Append a cache buster to bypass caching during development
            const response = await fetch(`${src}?_=${Date.now()}`);
            if (!response.ok) throw new Error(`Failed to fetch script: ${src}`);
            const scriptText = await response.text();
            
            // Wrap in an IIFE to prevent variable redeclaration crashes in SPA,
            // and add a sourceURL comment for browser devtools debugging support
            const wrappedText = `(() => {\n${scriptText}\n})();\n//# sourceURL=${window.location.origin}/${src}`;
            
            const script = document.createElement("script");
            script.setAttribute("data-src", src);
            script.text = wrappedText;
            document.body.appendChild(script);
            resolve();
        } catch (err) {
            reject(err);
        }
    });
}

function showToast(msg) {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toastMsg");
    if (toast && toastMsg) {
        toastMsg.textContent = msg;
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 3000);
    }
}

// Logouts
window.logoutUser = () => {
    localStorage.removeItem("career_user");
    showAuthScreen();
};

// Global navigate helper
window.navigateTo = navigateTo;

// Global quick message helper to navigate to chatbot and send message
function sendQuickMessage(msg) {
    navigateTo("chatbot");
    let retries = 0;
    const interval = setInterval(() => {
        const chatInput = document.getElementById("chatbotInput") || document.getElementById("chatInput");
        if (chatInput) {
            clearInterval(interval);
            chatInput.value = msg;
            const sendBtn = document.getElementById("chatbotSendBtn") || document.getElementById("sendBtn");
            if (sendBtn) sendBtn.click();
        } else {
            retries++;
            if (retries > 10) clearInterval(interval); // limit to 2 seconds
        }
    }, 200);
}
window.sendQuickMessage = sendQuickMessage;
