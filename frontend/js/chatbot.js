/* =======================================================
   AI Career Guidance - Enhanced RAG Chatbot Controller
   ======================================================= */

(() => {
const API_ENDPOINT = (window.getApiBaseUrl ? window.getApiBaseUrl() : (window.location.origin + "/api"));

function initChatbotPage() {
    initChatbot();
    
    // Check if voice auto-trigger is requested
    const params = new URLSearchParams(window.location.search);
    if (params.get("voice") === "true") {
        setTimeout(() => {
            const micBtn = document.getElementById("micBtn");
            if (micBtn) micBtn.click();
        }, 800);
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initChatbotPage);
} else {
    initChatbotPage();
}

function initChatbot() {
    const chatInput = document.getElementById("chatbotInput") || document.getElementById("chatInput");
    const sendBtn = document.getElementById("chatbotSendBtn") || document.getElementById("sendBtn");
    const chatBody = document.getElementById("chatbotBody") || document.getElementById("chatBody");
    const langSelect = document.getElementById("langSelect") || { value: "en" };
    const micBtn = document.getElementById("micBtn") || document.getElementById("voiceBtn");
    const chips = document.querySelectorAll(".chip");
    
    if (!chatInput || !sendBtn || !chatBody) return;
    
    // Add "Download Report" button to Chat Header if missing
    const chatHeader = document.querySelector(".chat-head");
    if (chatHeader && !document.getElementById("downloadReportBtn")) {
        const downloadBtn = document.createElement("button");
        downloadBtn.id = "downloadReportBtn";
        downloadBtn.className = "voice-btn";
        downloadBtn.style.padding = "6px 12px";
        downloadBtn.style.fontSize = "11.5px";
        downloadBtn.style.background = "var(--indigo-light)";
        downloadBtn.style.color = "var(--indigo)";
        downloadBtn.style.border = "none";
        downloadBtn.style.borderRadius = "8px";
        downloadBtn.style.cursor = "pointer";
        downloadBtn.innerHTML = `<i class="ti ti-download"></i> Report`;
        downloadBtn.addEventListener("click", downloadChatReport);
        chatHeader.appendChild(downloadBtn);
    }
    
    // Setup listeners
    sendBtn.replaceWith(sendBtn.cloneNode(true));
    const newSendBtn = document.getElementById("chatbotSendBtn") || document.getElementById("sendBtn");
    
    newSendBtn.addEventListener("click", (e) => handleChatSubmission(e));
    
    chatInput.removeEventListener("keydown", handleEnterKey);
    chatInput.addEventListener("keydown", handleEnterKey);
    
    function handleEnterKey(e) {
        if (e.key === "Enter") {
            handleChatSubmission(e);
        }
    }
    
    chips.forEach(chip => {
        chip.replaceWith(chip.cloneNode(true));
    });
    
    const newChips = document.querySelectorAll(".chip");
    newChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const msg = chip.getAttribute("data-msg") || chip.textContent;
            appendUserMessage(msg);
            queryChatbotAPI(msg);
        });
    });
    
    // 30-Second Inactivity Timers State
    let micTimer = null;
    let micCountdownInterval = null;
    let cameraTimer = null;
    let cameraCountdownInterval = null;
    let cameraSecondsLeft = 30;

    // Speech Recognition Setup with MediaRecorder and Sarvam STT
    let mediaRecorder;
    let audioChunks = [];
    let isListening = false;
    
    if (micBtn) {
        micBtn.addEventListener("click", async () => {
            if (isListening) {
                stopMicRecording();
            } else {
                startMicRecording();
            }
        });
        
        async function startMicRecording() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                fallbackWebkitSTT();
                return;
            }
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                audioChunks = [];
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = async () => {
                    clearMicTimers();
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    
                    const formData = new FormData();
                    formData.append("file", audioBlob, "speech.webm");
                    formData.append("lang", langSelect.value || "en");
                    
                    try {
                        const res = await fetch(`${API_ENDPOINT}/stt`, {
                            method: "POST",
                            body: formData
                        });
                        
                        if (res.ok) {
                            const data = await res.json();
                            if (data.transcript) {
                                chatInput.value = data.transcript;
                                handleChatSubmission({ preventDefault: () => {} });
                            } else {
                                if (typeof showToast === 'function') showToast("Could not recognize speech.");
                            }
                        } else {
                            if (typeof showToast === 'function') showToast("STT API failed. Falling back to browser speech.");
                            fallbackWebkitSTT();
                        }
                    } catch (err) {
                        console.error("STT upload error:", err);
                        fallbackWebkitSTT();
                    }
                };
                
                mediaRecorder.start();
                isListening = true;
                micBtn.classList.add("active");
                chatInput.placeholder = "Listening... Auto-disabling in 30s of inactivity";
                
                // 30-Second Inactivity Auto-Disable Trigger
                clearMicTimers();
                micTimer = setTimeout(() => {
                    if (isListening) {
                        if (typeof showToast === 'function') {
                            showToast("Microphone access disabled after 30 seconds of inactivity. Re-enable to record audio.");
                        } else {
                            alert("Microphone access disabled after 30 seconds of inactivity. Re-enable to record audio.");
                        }
                        stopMicRecording();
                    }
                }, 30000);

            } catch (err) {
                console.error("Microphone access denied, falling back:", err);
                fallbackWebkitSTT();
            }
        }

        function stopMicRecording() {
            if (mediaRecorder && mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
            }
            isListening = false;
            micBtn.classList.remove("active");
            chatInput.placeholder = "Processing speech...";
            clearMicTimers();
        }

        function clearMicTimers() {
            if (micTimer) clearTimeout(micTimer);
            micTimer = null;
        }

        function fallbackWebkitSTT() {
            if ('webkitSpeechRecognition' in window) {
                const rec = new webkitSpeechRecognition();
                rec.continuous = false;
                rec.interimResults = false;
                const lang = langSelect.value || "en";
                rec.lang = lang === 'hi' || lang === 'hinglish' ? 'hi-IN' : (lang === 'ta' ? 'ta-IN' : (lang === 'kn' ? 'kn-IN' : 'en-US'));
                
                rec.onstart = () => {
                    micBtn.classList.add("active");
                    chatInput.placeholder = "Browser Listening (Auto-stops in 30s)...";
                };
                rec.onend = () => {
                    micBtn.classList.remove("active");
                    chatInput.placeholder = "Type your message here...";
                };
                rec.onresult = (e) => {
                    chatInput.value = e.results[0][0].transcript;
                    handleChatSubmission({ preventDefault: () => {} });
                };
                rec.start();
            } else {
                if (typeof showToast === 'function') showToast("Speech recognition not supported in this browser.");
            }
        }
    }
    
    // Camera Setup, Snapshot & OCR Scanner
    const cameraBtn = document.getElementById("cameraBtn");
    const cameraModal = document.getElementById("cameraModal");
    const closeCameraBtn = document.getElementById("closeCameraBtn");
    const stopCameraBtn = document.getElementById("stopCameraBtn");
    const capturePhotoBtn = document.getElementById("capturePhotoBtn");
    const scanOcrModeBtn = document.getElementById("scanOcrModeBtn");
    const cameraVideo = document.getElementById("cameraVideo");
    const cameraCanvas = document.getElementById("cameraCanvas");
    const camCountdown = document.getElementById("camCountdown");
    const uploadImgBtn = document.getElementById("uploadImgBtn");
    const imageFileInput = document.getElementById("imageFileInput");
    let cameraStream = null;

    if (cameraBtn && cameraModal) {
        cameraBtn.addEventListener("click", async () => {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert("Camera is not supported on this browser.");
                return;
            }
            try {
                cameraStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
                cameraVideo.srcObject = cameraStream;
                cameraModal.style.display = "flex";
                startCameraInactivityTimer();
            } catch (err) {
                console.error("Camera access denied:", err);
                alert("Unable to access camera. Please check your browser camera permissions.");
            }
        });

        function startCameraInactivityTimer() {
            clearCameraTimers();
            cameraSecondsLeft = 30;
            if (camCountdown) camCountdown.textContent = cameraSecondsLeft;
            
            cameraCountdownInterval = setInterval(() => {
                cameraSecondsLeft--;
                if (camCountdown) camCountdown.textContent = cameraSecondsLeft;
                if (cameraSecondsLeft <= 0) {
                    clearCameraTimers();
                    stopCamera();
                    if (typeof showToast === 'function') {
                        showToast("Camera access disabled after 30 seconds of inactivity. Re-enable to capture a photo.");
                    } else {
                        alert("Camera access disabled after 30 seconds of inactivity. Re-enable to capture a photo.");
                    }
                }
            }, 1000);
        }

        function clearCameraTimers() {
            if (cameraTimer) clearTimeout(cameraTimer);
            if (cameraCountdownInterval) clearInterval(cameraCountdownInterval);
            cameraTimer = null;
            cameraCountdownInterval = null;
        }

        const stopCamera = () => {
            clearCameraTimers();
            if (cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
                cameraStream = null;
            }
            cameraModal.style.display = "none";
            cameraVideo.srcObject = null;
        };

        closeCameraBtn.addEventListener("click", stopCamera);
        stopCameraBtn.addEventListener("click", stopCamera);

        capturePhotoBtn.addEventListener("click", async () => {
            if (!cameraStream) return;
            
            const context = cameraCanvas.getContext("2d");
            cameraCanvas.width = cameraVideo.videoWidth || 640;
            cameraCanvas.height = cameraVideo.videoHeight || 480;
            
            context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
            const dataUrl = cameraCanvas.toDataURL("image/jpeg");
            
            stopCamera();
            
            appendUserMessage("📷 Captured snapshot for interview posture check & document OCR scanning.");
            
            // Try OCR text extraction on captured photo
            try {
                const ocrRes = await fetch(`${API_ENDPOINT}/ocr`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ image_base64: dataUrl })
                });
                
                if (ocrRes.ok) {
                    const ocrData = await ocrRes.json();
                    if (ocrData.text && ocrData.text.length > 15) {
                        queryChatbotAPI(`I captured an image containing the following scanned text:\n\n---\n${ocrData.text}\n---\n\nPlease analyze this document / code snippet, provide technical career guidance, skill gap analysis, or code review as an expert AI Career Mentor.`);
                        return;
                    }
                }
            } catch (err) {
                console.error("Camera OCR scan error:", err);
            }
            
            // Default mock interview posture check if no document text found
            queryChatbotAPI("Perform a mock interview camera verification and check my posture/background setup. Tell me if it is optimal for technical and Machine Learning role interviews.");
        });

        if (scanOcrModeBtn) {
            scanOcrModeBtn.addEventListener("click", () => {
                capturePhotoBtn.click();
            });
        }
    }

    // Document / Code / Image File Upload OCR Handler
    if (uploadImgBtn && imageFileInput) {
        uploadImgBtn.addEventListener("click", () => {
            imageFileInput.click();
        });

        imageFileInput.addEventListener("change", async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            appendUserMessage(`📄 Uploaded document / code image: <strong>${file.name}</strong>`);
            if (typeof showToast === 'function') showToast("Scanning image text with OCR pipeline...");

            const formData = new FormData();
            formData.append("file", file);

            try {
                const res = await fetch(`${API_ENDPOINT}/ocr`, {
                    method: "POST",
                    body: formData
                });

                if (res.ok) {
                    const data = await res.json();
                    if (data.text && data.text.length > 5) {
                        queryChatbotAPI(`I uploaded a document/resume/code image (${file.name}) containing the following text:\n\n---\n${data.text}\n---\n\nPlease analyze this content thoroughly, evaluate skill gaps, or provide career mentorship & code recommendations.`);
                    } else {
                        queryChatbotAPI(`I uploaded an image document (${file.name}). Please guide me on optimizing my resume and technical portfolio for engineering and AI roles.`);
                    }
                } else {
                    queryChatbotAPI(`I uploaded a technical document (${file.name}). Please provide guidance on engineering career paths and required technical skills.`);
                }
            } catch (err) {
                console.error("Image OCR upload failed:", err);
                queryChatbotAPI(`I uploaded a document (${file.name}). Please provide AI career guidance based on my active profile.`);
            }
            
            imageFileInput.value = "";
        });
    }
    
    function handleChatSubmission(e) {
        if (e && typeof e.preventDefault === 'function') {
            e.preventDefault(); // <-- Prevents default form submit / page refresh
        }
        
        const query = chatInput.value.trim();
        if (!query) return;
        
        appendUserMessage(query);
        chatInput.value = "";
        
        queryChatbotAPI(query);
    }
    
    function scrollToBottom(smooth = true) {
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
            scrollToBottom(false);
        });
        scrollObserver.observe(chatBody, { childList: true, subtree: true, characterData: true });
    }

    function appendUserMessage(text) {
        const msgContainer = document.createElement("div");
        msgContainer.className = "msg-container user";
        
        const msgDiv = document.createElement("div");
        msgDiv.className = "msg user";
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        msgDiv.innerHTML = `${text}<time>${timeStr}</time>`;
        msgContainer.appendChild(msgDiv);
        
        chatBody.appendChild(msgContainer);
        scrollToBottom(true);
    }
    
    async function queryChatbotAPI(query) {
        // Create an empty bot message container for typing effect
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const msgContainer = document.createElement("div");
        msgContainer.className = "msg-container bot";
        
        const msgDiv = document.createElement("div");
        msgDiv.className = "msg bot";
        
        const textSpan = document.createElement("span");
        textSpan.innerHTML = `<i class="ti ti-loader-2 animate-spin"></i> Typing response...`;
        msgDiv.appendChild(textSpan);
        
        const timeTag = document.createElement("time");
        timeTag.textContent = timeStr;
        msgDiv.appendChild(timeTag);
        
        msgContainer.appendChild(msgDiv);
        chatBody.appendChild(msgContainer);
        chatBody.scrollTop = chatBody.scrollHeight;
        
        const selectedLang = langSelect.value || "en";
        let fullText = "";
        let retrievedSources = [];
        
        try {
            const userObj = JSON.parse(localStorage.getItem("career_user"));
            const headers = { 
                "Content-Type": "application/json"
            };
            if (userObj) headers["X-User-Email"] = userObj.email;

            const res = await fetch(`${API_ENDPOINT}/chat`, {
                method: "POST",
                headers: headers,
                body: JSON.stringify({
                    message: query,
                    lang: selectedLang,
                    stream: true
                })
            });
            
            if (!res.ok) throw new Error("API call failed");
            
            textSpan.innerHTML = ""; // Clear loader
            
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            
            let streamBuffer = "";
            let isDone = false;

            while (!isDone) {
                const { value, done } = await reader.read();
                if (done) break;
                
                streamBuffer += decoder.decode(value, { stream: true });
                const lines = streamBuffer.split('\n');
                streamBuffer = lines.pop() || "";
                
                for (const line of lines) {
                    const trimmed = line.trim();
                    if (trimmed.startsWith("data: ")) {
                        const dataContent = trimmed.substring(6).trim();
                        if (dataContent === "[DONE]") {
                            isDone = true;
                            break;
                        }
                        
                        try {
                            const parsed = JSON.parse(dataContent);
                            if (parsed.chunk) {
                                fullText += parsed.chunk;
                                // Hide chart metadata from raw display
                                let cleanText = fullText.replace(/\[CHART:\s*(\w+),\s*(.*?)\]/g, "");
                                textSpan.innerHTML = parseMarkdown(cleanText);
                                chatBody.scrollTop = chatBody.scrollHeight;
                            }
                            if (parsed.sources) {
                                retrievedSources = parsed.sources;
                            }
                        } catch (e) {
                            // Ignored parse error for non-JSON lines
                        }
                    }
                }
            }
            
            // Stream finished! Load charts and utility buttons
            if (fullText && fullText.trim().length > 0) {
                let cleanText = fullText.replace(/\[CHART:\s*(\w+),\s*(.*?)\]/g, "");
                textSpan.innerHTML = parseMarkdown(cleanText);
            }
            
            // Trigger Mermaid diagram rendering safely
            if (window.mermaid) {
                const mermaidDivs = msgDiv.querySelectorAll(".mermaid");
                if (mermaidDivs.length > 0) {
                    try {
                        if (typeof window.mermaid.run === 'function') {
                            window.mermaid.run({ nodes: mermaidDivs });
                        } else {
                            window.mermaid.init(undefined, mermaidDivs);
                        }
                    } catch (e) {
                        console.error("Mermaid rendering error:", e);
                    }
                }
            }
            
            // Render sources safely if any
            if (retrievedSources && Array.isArray(retrievedSources) && retrievedSources.length > 0) {
                try {
                    const sourceBadges = retrievedSources.map(s => {
                        const srcStr = typeof s === 'string' ? s : (s && s.source ? s.source : (s && s.title ? s.title : "Document"));
                        return `<span style="display:inline-block; font-size:9.5px; background:#EEF0FF; color:#4F46E5; padding:2px 6px; border-radius:4px; margin-right:4px; margin-top:4px;">📚 ${srcStr}</span>`;
                    }).join("");
                    const sourcesContainer = document.createElement("div");
                    sourcesContainer.style.cssText = "margin-top:6px; font-size:10px; border-top:1px solid #ECEDF3; padding-top:4px; color:#6B7280;";
                    sourcesContainer.innerHTML = `Sources:<br>${sourceBadges}`;
                    msgDiv.appendChild(sourcesContainer);
                } catch (srcErr) {
                    console.error("Error rendering sources:", srcErr);
                }
            }
            
            // Render any charts safely
            try {
                if (typeof renderChartsInMessage === 'function') {
                    renderChartsInMessage(fullText, msgDiv);
                }
            } catch (cErr) {
                console.error("Error rendering charts:", cErr);
            }
            
            // Add TTS speak button
            let speakerBtnElement = null;
            try {
                const speakerHtml = `<button class="speech-btn" title="Speak reply" onclick="speakBotResponse(this)" style="background:none; border:none; color:var(--text-3); cursor:pointer; margin-left:8px;"><i class="ti ti-volume"></i></button>`;
                msgDiv.insertAdjacentHTML('beforeend', speakerHtml);
                speakerBtnElement = msgDiv.querySelector(".speech-btn");
            } catch (spkErr) {
                console.error("Error adding speech button:", spkErr);
            }
            
            // Auto-Read response TTS trigger if enabled
            const autoReadToggle = document.getElementById("autoReadToggle");
            if (autoReadToggle && autoReadToggle.checked && speakerBtnElement) {
                setTimeout(() => {
                    window.speakBotResponse(speakerBtnElement);
                }, 300);
            }
            
            // Add Feedback Buttons
            try {
                const feedbackWrap = document.createElement("div");
                feedbackWrap.className = "feedback-buttons";
                feedbackWrap.style.marginTop = "8px";
                feedbackWrap.innerHTML = `
                    <button class="feedback-btn" onclick="submitFeedback('up', this)" style="background:none; border:none; color:var(--text-3); cursor:pointer; margin-right:8px;"><i class="ti ti-thumb-up"></i></button>
                    <button class="feedback-btn" onclick="submitFeedback('down', this)" style="background:none; border:none; color:var(--text-3); cursor:pointer;"><i class="ti ti-thumb-down"></i></button>
                `;
                msgContainer.appendChild(feedbackWrap);
            } catch (fbErr) {
                console.error("Error adding feedback buttons:", fbErr);
            }
            
        } catch (err) {
            console.error("Chatbot query error:", err);
            if (!fullText || fullText.trim().length === 0) {
                textSpan.innerHTML = `<span style="color:var(--red);"><i class="ti ti-alert-circle"></i> Failed to retrieve guidance response. Server offline or timeout.</span>`;
            } else {
                // Keep the content already rendered and append small notification
                let cleanText = fullText.replace(/\[CHART:\s*(\w+),\s*(.*?)\]/g, "");
                textSpan.innerHTML = parseMarkdown(cleanText);
            }
        }
    }
}

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

// Chart.js renderer
function renderChartsInMessage(text, container) {
    const chartRegex = /\[CHART:\s*(\w+),\s*(.*?)\]/g;
    let match;
    let index = 0;
    
    while ((match = chartRegex.exec(text)) !== null) {
        const chartType = match[1];
        const dataStr = match[2];
        
        const labels = [];
        const values = [];
        dataStr.split(',').forEach(item => {
            const parts = item.split(':');
            if (parts.length === 2) {
                labels.push(parts[0].trim());
                values.push(parseFloat(parts[1].trim()) || 0);
            }
        });
        
        const canvasId = `chart_${Date.now()}_${index++}`;
        const canvas = document.createElement('canvas');
        canvas.id = canvasId;
        canvas.style.maxWidth = '100%';
        canvas.style.marginTop = '15px';
        canvas.style.background = '#fff';
        canvas.style.padding = '10px';
        canvas.style.borderRadius = '8px';
        canvas.style.border = '1px solid var(--border)';
        canvas.height = 160;
        
        container.appendChild(canvas);
        
        if (typeof Chart === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = () => {
                createChartInstance(canvasId, chartType, labels, values);
            };
            document.head.appendChild(script);
        } else {
            createChartInstance(canvasId, chartType, labels, values);
        }
    }
}

function createChartInstance(id, type, labels, values) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: type === 'pie' ? 'pie' : 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Metric Value',
                data: values,
                backgroundColor: [
                    'rgba(99, 102, 241, 0.7)',
                    'rgba(22, 163, 74, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(239, 68, 68, 0.7)',
                    'rgba(59, 130, 246, 0.7)'
                ],
                borderColor: [
                    '#6366F1',
                    '#16A34A',
                    '#F59E0B',
                    '#EF4444',
                    '#3B82F6'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: type === 'pie' ? {} : {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Download Chat Reports Action
function downloadChatReport() {
    const chatBody = document.getElementById("chatbotBody") || document.getElementById("chatBody");
    if (!chatBody) return;
    
    let text = "# AI Career Guidance Assistant - Consultation Report\n\n";
    text += `Generated on: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}\n\n`;
    text += `Target Student: ${JSON.parse(localStorage.getItem("career_user"))?.name || "Active Session Student"}\n\n`;
    text += "=========================================\n\n";
    
    const messages = chatBody.querySelectorAll(".msg-container");
    if (messages.length === 0) {
        alert("Chat console is empty. Send a query first!");
        return;
    }
    
    messages.forEach(msg => {
        const sender = msg.classList.contains("user") ? "User Student" : "AI Career Mentor";
        const content = msg.querySelector(".msg").cloneNode(true);
        // Strip nested tags like time and button
        const timeTag = content.querySelector("time");
        if (timeTag) timeTag.remove();
        const speechBtn = content.querySelector(".speech-btn");
        if (speechBtn) speechBtn.remove();
        
        text += `### [${sender}]\n${content.textContent.trim()}\n\n`;
    });
    
    const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `career_guidance_report_${Date.now()}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Text to Speech using Sarvam AI with Web Speech Fallback
window.speakBotResponse = async function(btn) {
    const parentMsg = btn.closest(".msg");
    const utteranceText = parentMsg.querySelector("span")?.textContent || parentMsg.firstChild.textContent;
    const lang = document.getElementById("langSelect")?.value || "en";
    
    // Change button icon/style to show loading
    const originalIcon = btn.innerHTML;
    btn.innerHTML = `<i class="ti ti-loader-quarter animate-spin"></i>`;
    btn.style.color = "var(--text-2)";
    
    try {
        const res = await fetch(`${API_ENDPOINT}/tts`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: utteranceText,
                lang: lang
            })
        });
        
        if (res.ok) {
            const data = await res.json();
            if (data.audio) {
                const audio = new Audio("data:audio/mp3;base64," + data.audio);
                btn.style.color = "var(--green)";
                btn.innerHTML = `<i class="ti ti-volume"></i>`;
                audio.play();
                audio.onended = () => {
                    btn.style.color = "var(--text-3)";
                    btn.innerHTML = originalIcon;
                };
                return;
            }
        }
    } catch (err) {
        console.error("Sarvam TTS failed, falling back to WebSpeech:", err);
    }
    
    // Fallback Speech Synthesis
    btn.innerHTML = originalIcon;
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(utteranceText.replace(/\[CHART:\s*(\w+),\s*(.*?)\]/g, ""));
        const voices = window.speechSynthesis.getVoices();
        
        let voice = voices.find(v => {
            if (lang === 'hi' || lang === 'hinglish') return v.lang.includes("hi-IN");
            if (lang === 'ta') return v.lang.includes("ta-IN");
            if (lang === 'kn') return v.lang.includes("kn-IN");
            return v.lang.includes("en-US");
        });
        
        if (voice) utterance.voice = voice;
        else utterance.lang = lang === 'hinglish' ? 'hi-IN' : lang;
        
        window.speechSynthesis.speak(utterance);
        
        btn.style.color = "var(--green)";
        utterance.onend = () => {
            btn.style.color = "var(--text-3)";
        };
    } else {
        alert("Speech synthesis is not supported on this browser.");
    }
};

window.submitFeedback = function(rating, btn) {
    btn.style.color = rating === 'up' ? 'var(--green)' : 'var(--red)';
    showToast("Thank you for your feedback! It helps improve recommendations.");
};

window.sendQuickMessage = function(msg) {
    const chatInput = document.getElementById("chatbotInput") || document.getElementById("chatInput");
    if (chatInput) {
        chatInput.value = msg;
        const sendBtn = document.getElementById("chatbotSendBtn") || document.getElementById("sendBtn");
        if (sendBtn) sendBtn.click();
    }
};

})();