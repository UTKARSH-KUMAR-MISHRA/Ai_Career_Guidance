/* =======================================================
   AI Career Guidance - Settings Page Controller
   ======================================================= */

(() => {
const API_SETTINGS = (window.getApiBaseUrl ? window.getApiBaseUrl() : (window.location.origin + "/api"));

function initSettingsPage() {
    setupThemeCards();
    setupPasswordForm();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSettingsPage);
} else {
    initSettingsPage();
}

function setupThemeCards() {
    const savedPreset = localStorage.getItem("theme_preset") || "default";
    
    // Highlight the active theme card
    const cards = document.querySelectorAll(".theme-card");
    cards.forEach(card => {
        card.classList.remove("active");
        if (card.dataset.theme === savedPreset) {
            card.classList.add("active");
        }
        
        card.addEventListener("click", () => {
            const theme = card.dataset.theme;
            
            // Set attributes on root document HTML element
            document.documentElement.setAttribute("data-theme", theme);
            localStorage.setItem("theme_preset", theme);
            
            // Remove active style from others and apply to clicked
            cards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            
            if (window.showToast) {
                window.showToast(`Applied ${theme.charAt(0).toUpperCase() + theme.slice(1)} theme style.`);
            }
        });
    });
}

function setupPasswordForm() {
    const form = document.getElementById("settingsPasswordForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const oldPass = document.getElementById("setOldPass").value;
        const newPass = document.getElementById("setNewPass").value;
        const confirmPass = document.getElementById("setConfirmPass").value;

        if (newPass.length < 8) {
            alert("New password must be at least 8 characters.");
            return;
        }

        if (newPass !== confirmPass) {
            alert("Passwords do not match.");
            return;
        }

        const btn = form.querySelector("button[type='submit']");
        btn.disabled = true;
        btn.innerHTML = `<i class="ti ti-loader-2 animate-spin"></i> Updating...`;

        try {
            const response = await fetch(`${API_SETTINGS}/auth/change-password`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    old_password: oldPass,
                    new_password: newPass
                })
            });

            const data = await response.json();
            btn.disabled = false;
            btn.innerHTML = `Update Password <i class="ti ti-lock"></i>`;

            if (!response.ok) {
                alert(data.error || "Failed to update password.");
                return;
            }

            if (window.showToast) {
                window.showToast("Password updated successfully!");
            }
            form.reset();

        } catch (err) {
            console.error(err);
            btn.disabled = false;
            btn.innerHTML = `Update Password <i class="ti ti-lock"></i>`;
            alert("Connection error. Ensure Flask backend is running.");
        }
    });
}

})();
