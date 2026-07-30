/* =======================================================
   AI Career Guidance - Profile Page Controller
   ======================================================= */

(() => {
const API_BASE_ENDPOINT = "http://localhost:5000/api";

function initProfilePage() {
    loadProfileDetails();
    
    // Wire up save buttons
    const saveBtns = document.querySelectorAll(".save-btn");
    saveBtns.forEach(btn => {
        btn.addEventListener("click", handleProfileSave);
    });
    
    // Checkboxes change listeners to auto-update progress
    const inputs = document.querySelectorAll("input, select, textarea");
    inputs.forEach(el => {
        el.addEventListener("change", updateProgressPercentage);
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProfilePage);
} else {
    initProfilePage();
}

async function loadProfileDetails() {
    try {
        const res = await fetch(`${API_BASE_ENDPOINT}/profile`);
        if (!res.ok) return;
        
        const data = await res.json();
        const raw = data.raw;
        
        // Populate inputs based on active profile details
        // 1. College
        const collegeInput = document.querySelector('input[placeholder="Your College"]');
        if (collegeInput && raw.college) collegeInput.value = raw.college;
        
        // 2. Degree
        const degreeSelect = document.querySelectorAll(".form-grid select")[0];
        if (degreeSelect && raw.current_course) degreeSelect.value = raw.current_course;
        
        // 3. Branch
        const branchSelect = document.querySelectorAll(".form-grid select")[1];
        if (branchSelect) {
            // Map CS, CSE, Computer Science
            if (raw.branch === 'CSE' || raw.branch === 'Computer Science') branchSelect.value = "Computer Science";
            else if (raw.branch === 'ECE') branchSelect.value = "Electronics & Communication";
            else if (raw.branch === 'ME') branchSelect.value = "Mechanical Engineering";
            else if (raw.branch === 'CE') branchSelect.value = "Civil Engineering";
        }
        
        // 4. Year
        const yearSelect = document.querySelectorAll(".form-grid select")[2];
        if (yearSelect && raw.year) {
            yearSelect.value = `${raw.year}rd Year`; // e.g. 3rd Year
        }
        
        // 5. CGPA
        const cgpaInput = document.querySelector('input[placeholder="8.5"]');
        if (cgpaInput && raw.cgpa) cgpaInput.value = raw.cgpa;
        
        // 6. Skills
        // Get all checked skills from backend string
        const knownStr = raw.known_skills || raw.technical_skills || "";
        const skillsArray = knownStr.split(',').map(s => s.trim().toLowerCase());
        
        const skillCheckboxes = document.querySelectorAll(".chips label input");
        skillCheckboxes.forEach(cb => {
            const labelText = cb.parentElement.textContent.trim().toLowerCase();
            // Match skill name or skill ID
            const isMatch = skillsArray.some(s => s === labelText || s === cb.value.toLowerCase());
            if (isMatch) {
                cb.checked = true;
            }
        });
        
        // 7. Goals
        const goalStr = raw.career_goal || raw.job_role_aspiration || "";
        const goalCheckboxes = document.querySelectorAll(".chips label input");
        goalCheckboxes.forEach(cb => {
            const labelText = cb.parentElement.textContent.trim().toLowerCase();
            if (goalStr.toLowerCase().includes(labelText)) {
                cb.checked = true;
            }
        });
        
        // Update completion percentage
        updateProgressPercentage();
        
    } catch (err) {
        console.error("Failed to load profile details:", err);
    }
}

async function handleProfileSave() {
    // 1. Gather all inputs
    const college = document.querySelector('input[placeholder="Your College"]')?.value || "";
    const degree = document.querySelectorAll(".form-grid select")[0]?.value || "B.Tech";
    const branchText = document.querySelectorAll(".form-grid select")[1]?.value || "Computer Science";
    const yearText = document.querySelectorAll(".form-grid select")[2]?.value || "3rd Year";
    const cgpa = parseFloat(document.querySelector('input[placeholder="8.5"]')?.value || "8.0");
    
    // Map branch display text to clean DB code
    let branch = "CSE";
    if (branchText.includes("Electronics")) branch = "ECE";
    else if (branchText.includes("Mechanical")) branch = "ME";
    else if (branchText.includes("Civil")) branch = "CE";
    
    // Extract year number
    const yearMatch = yearText.match(/\d+/);
    const year = yearMatch ? parseInt(yearMatch[0]) : 3;
    
    // Gather checked skills
    const checkedSkills = [];
    document.querySelectorAll(".card:has(h2:contains('Skills')) label input:checked").forEach(cb => {
        checkedSkills.push(cb.parentElement.textContent.trim());
    });
    
    // Gather goal
    let careerGoal = "Data Scientist";
    const checkedGoal = document.querySelector(".card:has(h3:contains('Career Goal')) label input:checked");
    if (checkedGoal) {
        careerGoal = checkedGoal.parentElement.textContent.trim();
    }
    
    // Fetch currently active student profile to preserve email or ID info
    let existingProfile = {};
    try {
        const res = await fetch(`${API_BASE_ENDPOINT}/profile`);
        if (res.ok) {
            const data = await res.json();
            existingProfile = data.raw;
        }
    } catch (err) {}
    
    // Build updated profile JSON
    const updatedProfile = {
        ...existingProfile,
        name: existingProfile.name || "Ananya Singh",
        college: college,
        current_course: degree,
        branch: branch,
        year: year,
        cgpa: cgpa,
        known_skills: checkedSkills.join(", "),
        technical_skills: checkedSkills.join(", "),
        career_goal: careerGoal,
        job_role_aspiration: careerGoal,
        daily_learning_hours: existingProfile.daily_learning_hours || 3
    };
    
    // Save to local storage for safety
    localStorage.setItem("careerProfileNormalized", JSON.stringify(updatedProfile));
    
    // Send to backend
    try {
        const res = await fetch(`${API_BASE_ENDPOINT}/profile`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updatedProfile)
        });
        
        if (res.ok) {
            showToast("Profile Saved Successfully!");
            // Reload page to reflect styling/metrics
            setTimeout(() => {
                window.location.reload();
            }, 800);
        } else {
            showToast("Failed to save profile on backend.");
        }
    } catch (err) {
        console.error("Failed to save profile on API:", err);
        showToast("Error connecting to server.");
    }
}

function updateProgressPercentage() {
    const fields = document.querySelectorAll("input[type='text'], select, textarea");
    let completed = 0;
    
    fields.forEach(f => {
        if (f.value.trim() !== "") completed++;
    });
    
    // Count checked checkboxes
    const totalCheckboxes = document.querySelectorAll("input[type='checkbox']").length;
    const checkedCheckboxes = document.querySelectorAll("input[type='checkbox']:checked").length;
    
    // Standard percentage calculation
    const totalFields = fields.length + (totalCheckboxes > 0 ? 1 : 0);
    const completedScore = completed + (checkedCheckboxes > 0 ? 1 : 0);
    
    const percentage = Math.round((completedScore / totalFields) * 100);
    
    const fill = document.querySelector(".progress-fill");
    const text = document.querySelector(".percentage");
    
    if (fill && text) {
        fill.style.width = `${percentage}%`;
        text.textContent = `${percentage}% Complete`;
    }
}

// Add jQuery style :contains selector helper to vanilla JS QuerySelector
// to let selectors like h2:contains('Skills') function correctly
(function() {
    const originalQuerySelectorAll = Document.prototype.querySelectorAll;
    const originalQuerySelector = Document.prototype.querySelector;
    
    function parseSelector(selector) {
        const containsRegex = /:contains\(['"]?([^'"]+)['"]?\)/;
        const match = selector.match(containsRegex);
        if (match) {
            const textToFind = match[1];
            const baseSelector = selector.replace(containsRegex, '');
            return { baseSelector, textToFind };
        }
        return null;
    }
    
    Document.prototype.querySelectorAll = function(selector) {
        const parsed = parseSelector(selector);
        if (parsed) {
            const elements = originalQuerySelectorAll.call(this, parsed.baseSelector);
            return Array.from(elements).filter(el => el.textContent.includes(parsed.textToFind));
        }
        return originalQuerySelectorAll.call(this, selector);
    };
    
    Document.prototype.querySelector = function(selector) {
        const parsed = parseSelector(selector);
        if (parsed) {
            const elements = originalQuerySelectorAll.call(this, parsed.baseSelector);
            const found = Array.from(elements).find(el => el.textContent.includes(parsed.textToFind));
            return found || null;
        }
        return originalQuerySelector.call(this, selector);
    };
    
    Element.prototype.querySelectorAll = function(selector) {
        const parsed = parseSelector(selector);
        if (parsed) {
            const elements = originalQuerySelectorAll.call(this, parsed.baseSelector);
            return Array.from(elements).filter(el => el.textContent.includes(parsed.textToFind));
        }
        return originalQuerySelectorAll.call(this, selector);
    };
    
    Element.prototype.querySelector = function(selector) {
        const parsed = parseSelector(selector);
        if (parsed) {
            const elements = originalQuerySelectorAll.call(this, parsed.baseSelector);
            const found = Array.from(elements).find(el => el.textContent.includes(parsed.textToFind));
            return found || null;
        }
        return originalQuerySelector.call(this, selector);
    };
})();

})();