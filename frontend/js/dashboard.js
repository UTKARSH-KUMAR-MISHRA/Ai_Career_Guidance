/* =======================================================
   AI Career Guidance - Dashboard Page Controller
   ======================================================= */

(() => {
const API_ROOT = "http://localhost:5000/api";

function initDashboard() {
    setTimeout(loadDashboardData, 300);
    initDashboardChat();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDashboard);
} else {
    initDashboard();
}

async function loadDashboardData() {
    try {
        // 1. Fetch recommendations for match stats
        const recRes = await fetch(`${API_ROOT}/recommendations`);
        if (!recRes.ok) return;
        const recommendations = await recRes.json();
        
        if (recommendations.length === 0) return;
        
        // Find top recommended role
        const topRole = recommendations[0];
        const targetRoleId = topRole.role_id;
        
        // Update stats
        const recommendedCountEl = document.querySelector(".stat-card:nth-child(1) .stat-value");
        if (recommendedCountEl) {
            // Count roles with score > 30%
            const positiveMatches = recommendations.filter(r => r.match_score > 30).length;
            recommendedCountEl.textContent = positiveMatches;
        }
        
        const matchScoreEl = document.querySelector(".stat-card:nth-child(2) .stat-value");
        const matchFillEl = document.querySelector(".stat-card:nth-child(2) .progress-fill");
        if (matchScoreEl && matchFillEl) {
            matchScoreEl.textContent = `${topRole.match_score}%`;
            matchFillEl.style.width = `${topRole.match_score}%`;
        }
        
        // 2. Fetch skill gap details for courses & projects
        const gapRes = await fetch(`${API_ROOT}/skill-gap?role_id=${targetRoleId}`);
        if (gapRes.ok) {
            const gapData = await gapRes.json();
            
            // Update resource count
            const resourceCountEl = document.querySelector(".stat-card:nth-child(3) .stat-value");
            if (resourceCountEl) {
                const totalRes = gapData.recommended_courses.length + gapData.recommended_projects.length;
                resourceCountEl.textContent = totalRes;
            }
            
            // Render Recommended Courses panel (limit 2)
            const coursesContainer = document.querySelector(".panel:has(.course-row)");
            if (coursesContainer) {
                const titleHead = coursesContainer.querySelector(".panel-head");
                let coursesHtml = `<div class="panel-head">${titleHead.innerHTML}</div>`;
                
                const courses = gapData.recommended_courses.slice(0, 2);
                if (courses.length > 0) {
                    courses.forEach(c => {
                        coursesHtml += `
                            <div class="course-row" onclick="window.navigateTo('courses')">
                                <div class="course-thumb"><i class="ti ti-brain"></i></div>
                                <div class="course-info">
                                    <div class="t">${c.course_name}</div>
                                    <div class="s">${c.platform} · ${c.difficulty}</div>
                                </div>
                                <span class="badge progress">Popular</span>
                            </div>
                        `;
                    });
                } else {
                    coursesHtml += `<p style="font-size:11px; color:#9CA3AF; margin:10px 0;">All course prerequisites completed!</p>`;
                }
                coursesContainer.innerHTML = coursesHtml;
            }
        }
        
        // 3. Fetch interview questions count
        const intRes = await fetch(`${API_ROOT}/interview?role_id=${targetRoleId}`);
        if (intRes.ok) {
            const questions = await intRes.json();
            const questionCountEl = document.querySelector(".stat-card:nth-child(4) .stat-value");
            if (questionCountEl) {
                questionCountEl.textContent = questions.length;
            }
            
            // Update interview widget circular progress SVG
            // Assume difficulty breakdown: e.g. 3 technical, 2 HR, 1 Aptitude
            const technicalCount = questions.filter(q => q.question_type.toLowerCase() === 'coding' || q.question_type.toLowerCase() === 'technical').length;
            const hrCount = questions.filter(q => q.question_type.toLowerCase() === 'hr' || q.question_type.toLowerCase() === 'behavioral').length;
            const aptitudeCount = questions.length - technicalCount - hrCount;
            
            const interviewLegend = document.querySelector(".panel:has(.ip-legend-row)");
            if (interviewLegend) {
                const legends = interviewLegend.querySelectorAll(".ip-legend-row");
                if (legends.length >= 3) {
                    legends[0].innerHTML = `<div class="lb"><span class="ldot" style="background:#6C63FF"></span>Technical</div><b>${technicalCount}</b>`;
                    legends[1].innerHTML = `<div class="lb"><span class="ldot" style="background:#16A34A"></span>HR / Scenario</div><b>${hrCount}</b>`;
                    legends[2].innerHTML = `<div class="lb"><span class="ldot" style="background:#F59E0B"></span>Core Concepts</div><b>${aptitudeCount}</b>`;
                }
                const ipNum = interviewLegend.querySelector(".ip-num");
                if (ipNum) ipNum.textContent = questions.length;
            }
        }
        
        // 4. Fetch active roadmap for timeline steps
        const roadRes = await fetch(`${API_ROOT}/roadmap?role_id=${targetRoleId}&type=90-Day`);
        if (roadRes.ok) {
            const roadmapSteps = await roadRes.json();
            
            // Render roadmap next step panel
            const nextStepPanel = document.querySelector(".nextstep-panel");
            if (nextStepPanel) {
                const titleHead = nextStepPanel.querySelector(".panel-head");
                let stepsHtml = `<div class="panel-head">${titleHead.innerHTML}</div>`;
                
                // Fetch first 4 learning modules
                const weeks = roadmapSteps.slice(0, 4);
                window.currentRoadmapSteps = weeks;
                
                stepsHtml += `<div class="ns-track" style="display:flex; justify-content:space-between; width:100%;">`;
                
                weeks.forEach((wk, i) => {
                    let medal = "🥇";
                    if (wk.status === 'Completed') medal = "🏆";
                    else if (i === 1) medal = "🥈";
                    else if (i === 2) medal = "🥉";
                    else if (i === 3) medal = "🏆";
                    
                    stepsHtml += `
                        <div class="ns-step" onclick="window.toggleModuleAccordion(${i})">
                            <div class="ns-medal">${medal}</div>
                            <div class="lbl" style="font-size:11px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:100px;">${wk.topic}</div>
                            <div class="sub-lbl" style="font-size:9px; color:${wk.status === 'Completed' ? '#16A34A' : '#4F46E5'}">${wk.status === 'Completed' ? 'Completed' : 'Week ' + wk.week_number} • Click to expand</div>
                        </div>
                    `;
                });
                stepsHtml += `</div>`;
                
                // Add slider filler
                const completedCount = roadmapSteps.filter(w => w.status === 'Completed').length;
                const progressPct = roadmapSteps.length > 0 ? Math.round((completedCount / roadmapSteps.length) * 100) : 0;
                
                stepsHtml += `
                    <div class="ns-sliderwrap" style="position:relative; height:7px; margin-top:14px;">
                        <div class="ns-slidertrack" style="position:absolute; width:100%; height:7px; background:#E7E8F2; border-radius:4px;"></div>
                        <div class="ns-sliderfill" style="position:absolute; width:${progressPct}%; height:7px; background:#4F46E5; border-radius:4px; transition:width 1s ease;"></div>
                        <div class="ns-dots" style="display:flex; justify-content:space-between; position:absolute; width:100%; top:-1px;">
                            ${weeks.map((w, idx) => `<span class="${idx === 0 ? 'on' : ''}" style="width:9px; height:9px; border-radius:50%; background:${w.status === 'Completed' ? '#4F46E5' : '#C9CBE0'};"></span>`).join('')}
                        </div>
                    </div>
                    <div id="moduleAccordionPanel" class="module-accordion" style="display:none;"></div>
                `;
                nextStepPanel.innerHTML = stepsHtml;

                if (window.activeModuleAccordionIdx !== null && window.activeModuleAccordionIdx !== undefined) {
                    const activeIdx = window.activeModuleAccordionIdx;
                    window.activeModuleAccordionIdx = null;
                    window.toggleModuleAccordion(activeIdx);
                }
            }
            
            // Render upcoming tasks panel based on incomplete roadmap items
            const tasksContainer = document.getElementById("dashboardTasksList");
            if (tasksContainer) {
                let tasksHtml = "";
                const incomplete = roadmapSteps.filter(w => w.status === 'Todo').slice(0, 3);
                if (incomplete.length > 0) {
                    incomplete.forEach((task, idx) => {
                        const priority = idx === 0 ? "High" : (idx === 1 ? "Medium" : "Low");
                        const badgeClass = idx === 0 ? "high" : (idx === 1 ? "medium" : "low");
                        tasksHtml += `
                            <div class="task-row">
                                <button class="task-check unchecked" onclick="toggleTaskDone(this)"><i class="ti ti-check"></i></button>
                                <div class="task-info">
                                    <div class="t">${task.topic}</div>
                                    <div class="s">${task.day_range}</div>
                                </div>
                                <span class="badge ${badgeClass}">${priority}</span>
                            </div>
                        `;
                    });
                } else {
                    tasksHtml += `<p style="font-size:11px; color:var(--text-3); margin:10px 0;">No upcoming tasks. You are all caught up!</p>`;
                }
                tasksContainer.innerHTML = tasksHtml;
            }
        }
        
    } catch (err) {
        console.error("Error populating dashboard details:", err);
    }
}

function toggleTaskDone(btn) {
    btn.classList.toggle('unchecked');
    const taskRow = btn.closest('.task-row');
    taskRow.classList.toggle('done', !btn.classList.contains('unchecked'));
}

/* =======================================================
   AI RAG Chatbot Widget Integration
   ======================================================= */

function parseMarkdown(text) {
    if (!text) return "";
    
    // Protect Mermaid code blocks first by replacing them with placeholders
    const mermaidBlocks = [];
    let textCleaned = text.replace(/```mermaid\n([\s\S]*?)```/gi, (match, code) => {
        const placeholder = `<!--MERMAID_PLACEHOLDER_${mermaidBlocks.length}-->`;
        mermaidBlocks.push(code.trim());
        return placeholder;
    });
    
    // Protect safe white-listed layout HTML tags from escaping
    const htmlBlocks = [];
    const htmlTagRegex = /<(\/?)(div|span|strong|p|br|table|thead|tbody|tr|th|td|ol|ul|li|b|i|u|h1|h2|h3|h4|h5|h6|hr)\b[^>]*>/gi;
    textCleaned = textCleaned.replace(htmlTagRegex, (match) => {
        const placeholder = `<!--HTML_TAG_PLACEHOLDER_${htmlBlocks.length}-->`;
        htmlBlocks.push(match);
        return placeholder;
    });
    
    let html = textCleaned;
    
    // Escape HTML tag elements (escapes custom tags or bracket inputs)
    html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // Code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre style="background:rgba(0,0,0,0.05); padding:10px; border-radius:6px; overflow-x:auto;"><code class="language-$1">$2</code></pre>');
    
    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(0,0,0,0.05); padding:2px 5px; border-radius:4px;">$1</code>');
    
    // Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 style="margin-top:12px; margin-bottom:6px; font-weight:700;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 style="margin-top:15px; margin-bottom:8px; font-weight:700;">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 style="margin-top:18px; margin-bottom:10px; font-weight:700;">$1</h1>');
    
    // Bullet list items
    html = html.replace(/^\s*-\s+(.*)$/gim, '<ul><li style="margin-bottom:4px;">$1</li></ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, ''); // combine lists
    
    // Numbered list items
    html = html.replace(/^\s*\d+\.\s+(.*)$/gim, '<ol><li style="margin-bottom:4px;">$1</li></ol>');
    html = html.replace(/<\/ol>\s*<ol>/g, ''); // combine lists
 
    // Markdown Table Parser
    const lines = html.split('\n');
    let insideTable = false;
    let tableHtml = '';
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('|') && line.endsWith('|')) {
            if (!insideTable) {
                insideTable = true;
                tableHtml = '<table style="width:100%; border-collapse:collapse; margin:15px 0; font-size:12.5px;">';
            }
            
            if (line.match(/^\|[\s:-|]+$/)) continue; // skip dividers
            
            const cols = line.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);
            const isHeader = !tableHtml.includes('<tbody>');
            const tag = isHeader ? 'th' : 'td';
            
            let rowHtml = '<tr style="border-bottom:1px solid #ECEDF3;">';
            cols.forEach(c => {
                rowHtml += `<${tag} style="padding:8px 10px; text-align:left; font-weight:${isHeader ? '700' : '400'};">${c}</${tag}>`;
            });
            rowHtml += '</tr>';
            
            if (isHeader) {
                tableHtml += `<thead style="background:rgba(0,0,0,0.02);">${rowHtml}</thead><tbody>`;
            } else {
                tableHtml += rowHtml;
            }
            lines[i] = ""; // clear processed line
        } else {
            if (insideTable) {
                insideTable = false;
                tableHtml += '</tbody></table>';
                lines[i - 1] = tableHtml;
            }
        }
    }
    if (insideTable) {
        tableHtml += '</tbody></table>';
        lines[lines.length - 1] = tableHtml;
    }
    html = lines.filter(l => l !== "").join('\n');
    
    // Convert newlines to breaks
    html = html.replace(/\n/g, '<br>');
    
    // Restore Mermaid placeholders as clean divs
    for (let i = 0; i < mermaidBlocks.length; i++) {
        let cleanMermaid = mermaidBlocks[i]
            .replace(/&amp;/g, "&")
            .replace(/&lt;/g, "<")
            .replace(/&gt;/g, ">");
        let escapedMermaid = cleanMermaid
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        html = html.replace(`&lt;!--MERMAID_PLACEHOLDER_${i}--&gt;`, `<div class="mermaid">${escapedMermaid}</div>`);
        html = html.replace(`<!--MERMAID_PLACEHOLDER_${i}-->`, `<div class="mermaid">${escapedMermaid}</div>`);
    }

    // Restore protected HTML tags
    for (let i = 0; i < htmlBlocks.length; i++) {
        html = html.replace(`&lt;!--HTML_TAG_PLACEHOLDER_${i}--&gt;`, htmlBlocks[i]);
        html = html.replace(`<!--HTML_TAG_PLACEHOLDER_${i}-->`, htmlBlocks[i]);
    }
    
    return html;
}

function initDashboardChat() {
    const chatInput = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendBtn");
    const chatBody = document.getElementById("chatBody");
    const chips = document.querySelectorAll(".chip");
    
    if (!chatInput || !sendBtn || !chatBody) return;
    
    function scrollDashboardChatToBottom(smooth = true) {
        if (!chatBody) return;
        requestAnimationFrame(() => {
            chatBody.scrollTo({
                top: chatBody.scrollHeight,
                behavior: smooth ? 'smooth' : 'auto'
            });
            chatBody.scrollTop = chatBody.scrollHeight;
        });
    }

    if (chatBody && !chatBody._hasScrollObserver) {
        chatBody._hasScrollObserver = true;
        const scrollObserver = new MutationObserver(() => {
            scrollDashboardChatToBottom(false);
        });
        scrollObserver.observe(chatBody, { childList: true, subtree: true, characterData: true });
    }

    sendBtn.addEventListener("click", handleChatSend);
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleChatSend();
    });
    
    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            const msg = chip.getAttribute("data-msg") || chip.textContent;
            appendMsg(msg, "user");
            getBotReply(msg);
        });
    });
    
    async function handleChatSend() {
        const query = chatInput.value.trim();
        if (!query) return;
        
        appendMsg(query, "user");
        chatInput.value = "";
        
        getBotReply(query);
    }
    
    function appendMsg(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `msg ${sender}`;
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        msgDiv.innerHTML = `${text}<time>${timeStr}</time>`;
        chatBody.appendChild(msgDiv);
        scrollDashboardChatToBottom(true);
    }
    
    async function getBotReply(query) {
        // Create an empty bot message container for typing effect
        const msgDiv = document.createElement("div");
        msgDiv.className = "msg bot";
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        const textSpan = document.createElement("span");
        textSpan.innerHTML = `<i class="ti ti-loader-2 animate-spin"></i> Typing response...`;
        msgDiv.appendChild(textSpan);
        
        const timeTag = document.createElement("time");
        timeTag.textContent = timeStr;
        msgDiv.appendChild(timeTag);
        
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
        
        let accumulatedAnswer = "";
        
        try {
            const user = JSON.parse(localStorage.getItem("career_user"));
            const res = await fetch("http://localhost:5000/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-User-Email": user?.email || "STU0001"
                },
                body: JSON.stringify({
                    message: query,
                    lang: "en",
                    stream: true
                })
            });
            
            if (!res.ok) {
                textSpan.innerHTML = `<span style="color:var(--red);"><i class="ti ti-alert-circle"></i> API error ${res.status}.</span>`;
                return;
            }
            
            const reader = res.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";
            textSpan.innerHTML = ""; // Clear loader
            
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop(); // Keep last incomplete line in buffer
                
                for (const line of lines) {
                    const cleanLine = line.trim();
                    if (!cleanLine.startsWith("data:")) continue;
                    
                    const dataStr = cleanLine.substring(5).trim();
                    if (dataStr === "[DONE]") break;
                    
                    try {
                        const parsed = JSON.parse(dataStr);
                        if (parsed.chunk) {
                            accumulatedAnswer += parsed.chunk;
                            textSpan.innerHTML = parseMarkdown(accumulatedAnswer);
                            chatBody.scrollTop = chatBody.scrollHeight;
                        } else if (parsed.sources && parsed.sources.length > 0) {
                            // Add sources badge at the end of the text
                            const sourceBadges = parsed.sources.map(s => 
                                `<span style="display:inline-block; font-size:9.5px; background:#EEF0FF; color:#4F46E5; padding:2px 6px; border-radius:4px; margin-right:4px; margin-top:4px;">📚 ${s.source}</span>`
                            ).join("");
                            const sourcesDiv = document.createElement("div");
                            sourcesDiv.style.marginTop = "6px";
                            sourcesDiv.style.fontSize = "10px";
                            sourcesDiv.style.borderTop = "1px solid #ECEDF3";
                            sourcesDiv.style.paddingTop = "4px";
                            sourcesDiv.style.color = "#6B7280";
                            sourcesDiv.innerHTML = `Sources:<br>${sourceBadges}`;
                            msgDiv.appendChild(sourcesDiv);
                            chatBody.scrollTop = chatBody.scrollHeight;
                        }
                    } catch (e) {
                        // Ignore chunk JSON parse errors
                    }
                }
            }
            
            // Post-stream cleanup and Mermaid init
            if (window.mermaid) {
                setTimeout(() => {
                    const mermaidDivs = document.querySelectorAll("#chatBody .mermaid");
                    if (mermaidDivs.length > 0) {
                        try {
                            if (typeof window.mermaid.run === 'function') {
                                window.mermaid.run({ nodes: mermaidDivs });
                            } else {
                                window.mermaid.init(undefined, mermaidDivs);
                            }
                        } catch (e) {
                            console.error("Dashboard Mermaid rendering error:", e);
                        }
                    }
                    chatBody.scrollTop = chatBody.scrollHeight;
                }, 200);
            }
            
        } catch (err) {
            console.error("Chat error:", err);
            textSpan.innerHTML = `<span style="color:var(--red);"><i class="ti ti-alert-circle"></i> Connection offline.</span>`;
        }
    }
    
    // Wire up askNowBtn and startPracticeBtn
    const askNowBtn = document.getElementById("askNowBtn");
    if (askNowBtn) {
        askNowBtn.addEventListener("click", () => {
            chatInput.focus();
        });
    }
    const startPracticeBtn = document.getElementById("startPracticeBtn");
    if (startPracticeBtn) {
        startPracticeBtn.addEventListener("click", () => {
            window.navigateTo("interview");
        });
    }
}

// Inline Module Accordion Toggle
window.toggleModuleAccordion = function(idx) {
    const panel = document.getElementById("moduleAccordionPanel");
    if (!panel) return;
    
    let step = (window.currentRoadmapSteps && window.currentRoadmapSteps[idx]) ? window.currentRoadmapSteps[idx] : {
        topic: `Learning Module ${idx + 1}`,
        week_number: idx + 1,
        day_range: `Day ${idx * 7 + 1}-${(idx + 1) * 7}`,
        estimated_hours: 10,
        skill_name: idx === 0 ? "Core Programming & Data Structures" : (idx === 1 ? "System Architecture & APIs" : (idx === 2 ? "Database Design & Optimization" : "Cloud Deployment & Microservices")),
        course_name: idx === 0 ? "Python & CS Fundamentals" : (idx === 1 ? "Web & API Architecture" : (idx === 2 ? "PostgreSQL & Database Design" : "Docker & AWS Deployment")),
        course_platform: "NPTEL / Coursera",
        project_name: idx === 0 ? "Data Structure Engine" : (idx === 1 ? "REST API Microservice" : (idx === 2 ? "High-Throughput DB System" : "CI/CD Cloud Pipeline")),
        milestone: `Complete Module ${idx + 1} core benchmarks and peer code reviews`,
        status: "In Progress"
    };

    const steps = document.querySelectorAll(".ns-step");
    const clickedStep = steps[idx];

    // If module is currently open and clicked again -> collapse it
    if (window.activeModuleAccordionIdx === idx && panel.style.display !== "none") {
        if (clickedStep) clickedStep.classList.remove("active");
        panel.style.display = "none";
        window.activeModuleAccordionIdx = null;
        return;
    }

    window.activeModuleAccordionIdx = idx;
    steps.forEach((s, i) => {
        if (i === idx) s.classList.add("active");
        else s.classList.remove("active");
    });

    panel.innerHTML = `
        <div class="module-accordion-title">
            <div style="display:flex; align-items:center; gap:8px;">
                <span>📚 <strong>${step.topic}: ${step.skill_name || 'Core Fundamentals & Architecture'}</strong></span>
                <span style="font-size:11px; background:#EEF2FF; color:#4F46E5; padding:3px 8px; border-radius:6px; font-weight:600;">${step.day_range || 'Week ' + step.week_number} • ${step.estimated_hours || 10} Hours</span>
            </div>
            <button onclick="window.toggleModuleAccordion(${idx})" title="Close Drawer" style="background:none; border:none; font-size:20px; line-height:1; font-weight:700; color:#64748B; cursor:pointer; padding:0 4px;">&times;</button>
        </div>
        <div class="module-accordion-body">
            <div class="module-accordion-scrollable">
                <div style="margin-bottom:8px;"><strong>🎯 Key Technical Syllabus & Study Objectives:</strong></div>
                <ul style="margin-bottom:12px;">
                    <li><strong>Primary Skill Target:</strong> ${step.skill_name || 'Engineering Principles'} — Master core syntax, data models, and memory optimization techniques.</li>
                    <li><strong>System Architecture:</strong> Modular component design, software design patterns, and asynchronous execution workflows.</li>
                    <li><strong>Algorithmic Mastery:</strong> Time and space complexity benchmarking, data structure implementation, and edge-case handling.</li>
                    <li><strong>Quality Assurance:</strong> Unit testing standards, automated test runner integration, and code review compliance.</li>
                </ul>

                <div style="margin-bottom:8px;"><strong>📖 Recommended Course Resource:</strong></div>
                <div style="background:#F1F5F9; border-left:3px solid #4F46E5; padding:8px 12px; border-radius:4px; font-size:12px; margin-bottom:12px;">
                    <strong>${step.course_name || 'Technical Specialization Course'}</strong> (${step.course_platform || 'Udemy / NPTEL'})<br>
                    <span style="color:#64748B;">Includes guided video tutorials, interactive coding quizzes, and peer-reviewed assignments.</span>
                </div>

                <div style="margin-bottom:8px;"><strong>🛠️ Industry Capstone Project:</strong></div>
                <div style="background:#F8FAFC; border:1px dashed #CBD5E1; padding:8px 12px; border-radius:6px; font-size:12px; margin-bottom:12px;">
                    <strong>${step.project_name || 'Enterprise System Benchmark'}</strong><br>
                    <span style="color:#64748B;">Develop and test a production-ready software module demonstrating ${step.skill_name || 'core technical'} proficiency.</span>
                </div>

                <div style="background:#EEF2FF; border-radius:6px; padding:8px 12px; font-size:12px; color:#4338CA; font-weight:600;">
                    🏁 Milestone Target: ${step.milestone || 'Complete all Week ' + step.week_number + ' assessments and code submissions.'}
                </div>
            </div>
            <div style="margin-top:12px; display:flex; justify-content:space-between; align-items:center; border-top:1px solid #E2E8F0; padding-top:8px;">
                <span style="font-size:11.5px; color:#64748B;">Module Status: <strong style="color:${step.status === 'Completed' ? '#16A34A' : '#4F46E5'}">${step.status || 'In Progress'}</strong></span>
                <button onclick="window.navigateTo('roadmap')" style="background:#4F46E5; color:#fff; border:none; padding:6px 12px; border-radius:6px; font-size:11.5px; font-weight:600; cursor:pointer;">Explore Full Roadmap <i class="ti ti-arrow-right"></i></button>
            </div>
        </div>
    `;
    panel.style.display = "block";
};

function parseMarkdown(text) {
    if (!text) return "";
    
    // Protect Mermaid code blocks
    const mermaidBlocks = [];
    let textCleaned = text.replace(/```mermaid\n([\s\S]*?)```/gi, (match, code) => {
        const placeholder = `<!--MERMAID_PLACEHOLDER_${mermaidBlocks.length}-->`;
        mermaidBlocks.push(code.trim());
        return placeholder;
    });
    
    let html = textCleaned.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    
    // Citation badges transformer for [1], [2], [roles.csv], [courses.csv], [projects.csv], [interview_questions.csv], etc.
    html = html.replace(/\[(\d+|[\w\.-]+\.csv|web_search_[\w\.-]+)\]/gi, (match, citeId) => {
        return `<span class="rag-citation-badge" title="Retrieved Database Citation: ${citeId}" style="display:inline-flex; align-items:center; gap:3px; background:#EEF2FF; color:#4F46E5; border:1px solid #C7D2FE; font-size:11px; font-weight:700; padding:1px 7px; border-radius:12px; margin:0 3px; cursor:pointer; vertical-align:middle; box-shadow:0 1px 2px rgba(79,70,229,0.12);">📚 [${citeId}]</span>`;
    });
    
    // Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Italic
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 style="margin-top:12px; margin-bottom:6px; font-weight:700;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 style="margin-top:15px; margin-bottom:8px; font-weight:700;">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 style="margin-top:18px; margin-bottom:10px; font-weight:700;">$1</h1>');
    
    // Lists
    html = html.replace(/^\s*-\s+(.*)$/gim, '<ul><li style="margin-bottom:4px;">$1</li></ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, '');
    
    html = html.replace(/\n/g, '<br>');
    
    // Restore Mermaid placeholders
    for (let i = 0; i < mermaidBlocks.length; i++) {
        let cleanMermaid = mermaidBlocks[i].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
        let escapedMermaid = cleanMermaid.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        html = html.replace(`&lt;!--MERMAID_PLACEHOLDER_${i}--&gt;`, `<div class="mermaid">${escapedMermaid}</div>`);
        html = html.replace(`<!--MERMAID_PLACEHOLDER_${i}-->`, `<div class="mermaid">${escapedMermaid}</div>`);
    }
    
    return html;
}

})();
