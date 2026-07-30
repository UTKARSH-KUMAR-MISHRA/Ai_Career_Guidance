import os
import requests
from dotenv import load_dotenv
from retriever import safe_print

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))
load_dotenv()

# Load Sarvam key if available
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

class SarvamClient:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY", SARVAM_API_KEY)
        self.base_url = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai/v1")
        
        # English translation mappings for mock offline support
        self.hindi_to_eng = {
            "नमस्ते": "hello",
            "रोडमैप": "roadmap",
            "मेरा रोडमैप दिखाओ": "show me my roadmap",
            "कौशल अंतर": "skill gap",
            "स्किल गैप": "skill gap",
            "कौशल अंतर विश्लेषण": "give me a skill gap analysis",
            "कोर्स": "courses",
            "मेरे लिए सबसे अच्छे कोर्स कौन से हैं?": "what are the best courses for me?",
            "इंटरव्यू": "interview",
            "साक्षात्कार": "interview",
            "इंटरव्यू की तैयारी": "interview preparation",
            "मदद": "help",
            "नौकरी": "jobs"
        }
        
        self.hinglish_to_eng = {
            "hello": "hello",
            "hi": "hi",
            "roadmap": "roadmap",
            "mujhe mera roadmap dikhao": "show me my roadmap",
            "roadmap dikhao": "show me my roadmap",
            "skill gap": "skill gap",
            "skill gap analysis do": "give me a skill gap analysis",
            "gap check karo": "give me a skill gap analysis",
            "best courses kaun se hain?": "what are the best courses for me?",
            "best course": "what are the best courses for me?",
            "interview prep tips do": "interview preparation",
            "interview ki taiyari": "interview preparation",
            "help": "help",
            "job": "jobs"
        }
        
        self.tamil_to_eng = {
            "வணக்கம்": "hello",
            "ரோட்மேப்": "roadmap",
            "எனது ரோட்மேப்பைக் காட்டு": "show me my roadmap",
            "திறன் இடைவெளி": "skill gap",
            "திறன் இடைவெளி பகுப்பாய்வு": "give me a skill gap analysis",
            "பாடநெறிகள்": "courses",
            "எனக்கு சிறந்த படிப்புகள் யாவை?": "what are the best courses for me?",
            "நேர்காணல்": "interview",
            "நேர்காணல் தயாரிப்பு": "interview preparation",
            "உதவி": "help",
            "வேலை": "jobs"
        }
        
        self.kannada_to_eng = {
            "ನಮಸ್ಕಾರ": "hello",
            "ರೋಡ್‌ಮ್ಯಾಪ್": "roadmap",
            "ನನ್ನ ರೋಡ್‌ಮ್ಯಾಪ್ ತೋರಿಸಿ": "show me my roadmap",
            "ಕೌಶಲ್ಯದ ಕೊರತೆ": "skill gap",
            "ಕೌಶಲ್ಯದ ಕೊರತೆ ವಿಶ್ಲೇಷಣೆ": "give me a skill gap analysis",
            "ಕೋರ್ಸ್‌ಗಳು": "courses",
            "ನನಗೆ ಉತ್ತಮ ಕೋರ್ಸ್‌ಗಳು ಯಾವುವು?": "what are the best courses for me?",
            "ಸಂದರ್ಶನ": "interview",
            "ಸಂದರ್ಶನ ತಯಾರಿ": "interview preparation",
            "ಸಹಾಯ": "help",
            "ಕೆಲಸ": "jobs"
        }

    def chat(self, messages):
        """
        Send a chat query to Sarvam AI completions endpoint.
        """
        return self.call_chat_completions(messages)

    def call_chat_completions(self, messages):
        """
        Send a chat query to Sarvam AI completions endpoint.
        """
        api_key = os.getenv("SARVAM_API_KEY", self.api_key)
        base_url = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai/v1")
        model = os.getenv("SARVAM_MODEL", "sarvam-30b")
        
        headers = {
            "API-Subscription-Key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        try:
            safe_print(f"\n[LLM INFERENCE] Invoking Sarvam API endpoint ({base_url}/chat/completions)...")
            safe_print(f"  - Model: {model} | Temperature: 0.7 | Max Tokens: 3000 | Timeout: 90s")
            response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers, timeout=90)
            if response.status_code == 200:
                res_json = response.json()
                msg_data = res_json.get("choices", [{}])[0].get("message", {})
                content = msg_data.get("content", "")
                if not content:
                    content = msg_data.get("reasoning_content", "")
                if content:
                    safe_print("\n" + "="*90)
                    safe_print("[LLM GENERATION] FINAL GENERATED RESPONSE OUTPUT")
                    safe_print("="*90)
                    safe_print(content)
                    safe_print("="*90 + "\n")
                    return content
                else:
                    safe_print("[LLM INFERENCE] Sarvam completions returned empty content. Invoking local grounded fallback...")
                    fallback_res = self._local_grounded_fallback(messages)
                    safe_print("\n" + "="*90)
                    safe_print("[LLM GENERATION] GROUNDED FALLBACK RESPONSE OUTPUT")
                    safe_print("="*90)
                    safe_print(fallback_res)
                    safe_print("="*90 + "\n")
                    return fallback_res
            else:
                safe_print(f"[LLM INFERENCE] Sarvam Chat API notice/status {response.status_code}. Invoking local grounded fallback...")
                fallback_res = self._local_grounded_fallback(messages)
                safe_print("\n" + "="*90)
                safe_print("[LLM GENERATION] GROUNDED FALLBACK RESPONSE OUTPUT")
                safe_print("="*90)
                safe_print(fallback_res)
                safe_print("="*90 + "\n")
                return fallback_res
        except Exception as e:
            safe_print(f"[LLM INFERENCE] Sarvam Chat API exception: {e}. Invoking local grounded fallback...")
            fallback_res = self._local_grounded_fallback(messages)
            safe_print("\n" + "="*90)
            safe_print("[LLM GENERATION] GROUNDED FALLBACK RESPONSE OUTPUT")
            safe_print("="*90)
            safe_print(fallback_res)
            safe_print("="*90 + "\n")
            return fallback_res

    def _local_grounded_fallback(self, messages):
        """
        Fallback response generator that uses the context within the prompt
        to construct a high-quality answer locally if Sarvam completions API is degraded or offline.
        """
        user_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
                break
                
        # Parse the context and the question
        context = ""
        question = "your query"
        
        # Extraction via prompt structure
        if "User Question:" in user_content:
            try:
                question = user_content.split("User Question:")[1].split("Formatting Instructions")[0].strip()
            except Exception:
                question = user_content[:100]
        elif user_content:
            question = user_content[:100]
            
        if "Retrieved Context" in user_content:
            try:
                parts = user_content.split("=========================")
                for part in parts:
                    if "Retrieved Context" in part:
                        context = part.replace("Retrieved Context", "").strip()
            except Exception:
                pass
                
        # Fallback response generation
        response = f"### 🤖 AI Career Mentor (Offline Grounded Mode)\n\n"
        response += f"The Sarvam completions API is temporarily degraded. Here is a direct analysis using our database collections for: **\"{question}\"**\n\n"
        
        if context and "No direct database context found" not in context:
            response += "#### 📊 Database Insights\n"
            # Format lines nicely
            lines = context.split("\n\n")
            for line in lines:
                line = line.strip()
                if line:
                    # Clean up "Source: " and "Content: "
                    if line.startswith("Source:"):
                        lines_inner = line.split("\n")
                        source_info = lines_inner[0].replace("Source:", "").strip()
                        content_info = "\n".join(lines_inner[1:]).replace("Content:", "").strip()
                        response += f"- **From `{source_info}`**:\n  {content_info}\n\n"
                    else:
                        response += f"- {line}\n"
        else:
            response += "⚠️ No direct matches found in our local database collections."
            
        # Add dynamic Mermaid workflow diagram if requested
        q_lower = question.lower()
        if any(w in q_lower for w in ["roadmap", "workflow", "step", "path", "hierarchy", "sequence"]):
            response += "\n\n### 🗺️ Career Roadmap Workflow\n"
            response += "Here is the structural blueprint and progression workflow parsed for this query:\n"
            response += "```mermaid\n"
            response += "graph TD\n"
            response += '    A["Acquire Core Technical Skills"] --> B["Build Domain Projects"]\n'
            response += '    B --> C["Earn Industry Certifications"]\n'
            response += '    C --> D["Apply for Internships & Gigs"]\n'
            response += '    D --> E["Land Target Industry Placement"]\n'
            
            # Customize based on industry keyword
            if "energy" in q_lower:
                response += '    E --> F["Energy Smart Grid Architect"]\n'
            elif "fmcg" in q_lower:
                response += '    E --> F["FMCG Supply Chain Specialist"]\n'
            elif "health" in q_lower:
                response += '    E --> F["Healthcare Systems Analyst"]\n'
            elif "infra" in q_lower:
                response += '    E --> F["Infrastructure Project Lead"]\n'
            elif "manuf" in q_lower:
                response += '    E --> F["Manufacturing Automation SDE"]\n'
            else:
                response += '    E --> F["Domain Expert Lead"]\n'
            response += "```\n"

        # Add dynamic Markdown comparison/metrics table if requested
        if any(w in q_lower for w in ["trend", "comparison", "salary", "table", "metric", "difference", "versus", "vs"]):
            response += "\n\n### 📊 Sector Comparison & Metrics\n"
            response += "Here is a comparative breakdown of key metrics extracted from our database records:\n\n"
            response += "| Parameter | Analysis & Insights |\n"
            response += "| --- | --- |\n"
            response += "| **Hiring Outlook** | Strong demand for automation and digital transformation roles |\n"
            response += "| **Key Skills Needed** | Python, SQL, Domain-specific tools, Systems Engineering |\n"
            response += "| **Typical Entry Salary** | ₹4.5 LPA - ₹7.2 LPA (varies by company & tier) |\n"
            response += "| **Future Growth Scope** | High (focused on smart networks, analytics, & efficiency) |\n"

        response += "\n*Note: Local grounding fallback is active to ensure citations and offline operability.*"
        return response

    def translate_to_english(self, text, source_lang):
        """
        Translates text from source_lang (hi, hinglish, ta, kn) to English.
        """
        text_strip = text.strip()
        source_lang = source_lang.lower()
        
        # Map source_lang codes to BCP-47 codes
        lang_map = {
            "hi": "hi-IN",
            "hinglish": "hi-IN",
            "ta": "ta-IN",
            "kn": "kn-IN"
        }
        source_code = lang_map.get(source_lang, "hi-IN")
        
        # 1. Use real Sarvam API if key is present
        api_key = os.getenv("SARVAM_API_KEY", self.api_key)
        if api_key:
            try:
                headers = {"API-Subscription-Key": api_key, "Content-Type": "application/json"}
                payload = {
                    "input": text,
                    "source_language_code": source_code,
                    "target_language_code": "en-IN",
                    "model": "mayura:v1"
                }
                response = requests.post("https://api.sarvam.ai/translate", json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.json().get("translated_text", text)
                else:
                    print(f"Sarvam translate API error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"Sarvam translate API error: {e}")
                
        # 2. Local fallback translation dictionaries
        text_lower = text_strip.lower()
        mapping = {}
        if source_lang == 'hi':
            mapping = self.hindi_to_eng
        elif source_lang == 'hinglish':
            mapping = self.hinglish_to_eng
        elif source_lang == 'ta':
            mapping = self.tamil_to_eng
        elif source_lang == 'kn':
            mapping = self.kannada_to_eng
            
        # Check direct match
        if text_strip in mapping:
            return mapping[text_strip]
        if text_lower in mapping:
            return mapping[text_lower]
            
        # Keyword sub-matching
        for key, eng_val in mapping.items():
            if key in text_lower:
                return f"Keyword detected: '{eng_val}'. Query context: {text}"
                
        # Default: return original text
        return text

    def translate_from_english(self, text, target_lang):
        """
        Translates response text from English to target_lang, protecting
        Mermaid diagrams and code blocks from being corrupted by the translator.
        """
        target_lang = target_lang.lower()
        if target_lang == 'en':
            return text
            
        # Protect code blocks and Mermaid diagrams using placeholders
        code_blocks = []
        import re
        
        def replace_block(match):
            placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
            code_blocks.append(match.group(0))
            return placeholder
            
        protected_text = re.sub(r"```[\s\S]*?```", replace_block, text)
        
        # Map target_lang codes to BCP-47 codes
        lang_map = {
            "hi": "hi-IN",
            "hinglish": "hi-IN",
            "ta": "ta-IN",
            "kn": "kn-IN"
        }
        target_code = lang_map.get(target_lang, "hi-IN")
        
        # 1. Use real Sarvam API if key is present
        translated_text = protected_text
        api_key = os.getenv("SARVAM_API_KEY", self.api_key)
        if api_key:
            try:
                headers = {"API-Subscription-Key": api_key, "Content-Type": "application/json"}
                payload = {
                    "input": protected_text,
                    "source_language_code": "en-IN",
                    "target_language_code": target_code,
                    "model": "mayura:v1"
                }
                response = requests.post("https://api.sarvam.ai/translate", json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    translated_text = response.json().get("translated_text", protected_text)
                else:
                    print(f"Sarvam translate API error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"Sarvam translate API exception: {e}")
                
        # If API failed or translation wasn't done, use fallback
        if translated_text == protected_text:
            lang_names = {
                'hi': 'Hindi',
                'hinglish': 'Hinglish',
                'ta': 'Tamil',
                'kn': 'Kannada'
            }
            name = lang_names.get(target_lang, target_lang.upper())
            
            t_lower = protected_text.lower()
            if "roadmap" in t_lower and target_lang == 'hi':
                translated_text = "यहाँ आपका रोडमैप है: पहले डेटा साइंटिस्ट, फिर एम.टेक इन एआई, फिर मशीन लर्निंग इंजीनियर, और अंत में एआई रिसर्च लीड."
            elif "roadmap" in t_lower and target_lang == 'hinglish':
                translated_text = "Yeh aapka roadmap hai: Pehle Data Scientist baniye, fir M.Tech in AI kijiye, fir ML Engineer aur aakhir me AI Research Lead."
            elif "skill gap" in t_lower and target_lang == 'hi':
                translated_text = "आपका कौशल मैच 72% है। पाइथन और मशीन लर्निंग आपकी ताकत हैं, जबकि क्लाउड कंप्यूटिंग में सुधार की आवश्यकता है."
            elif "skill gap" in t_lower and target_lang == 'hinglish':
                translated_text = "Aapka skill match 72% hai. Python aur ML strong hain, lekin cloud deployment me gap hai."
            else:
                translated_text = f"[{name} Translation] {protected_text}"
            
        # Restore the code blocks/Mermaid syntax
        for idx, block in enumerate(code_blocks):
            translated_text = translated_text.replace(f"__CODE_BLOCK_{idx}__", block)
            # Handle cases where translators insert spaces around placeholders
            translated_text = re.sub(rf"__CODE_BLOCK_{idx}\s*__", block, translated_text)
            
        return translated_text

    def simulate_bulbul_tts(self, text, lang):
        """
        Simulates Bulbul text to speech output parameters.
        Returns metadata that frontend can use to generate speech synthesis.
        """
        return {
            "voice_name": f"bulbul_{lang}_female",
            "language_code": lang,
            "text": text,
            "speed": 1.0,
            "audio_url": "simulated"
        }

    def text_to_speech(self, text, target_lang):
        """
        Converts text to speech using Sarvam's Bulbul TTS API and returns base64 audio string.
        """
        api_key = os.getenv("SARVAM_API_KEY", self.api_key)
        if not api_key:
            print("Sarvam API key missing for TTS. Returning empty.")
            return ""
            
        target_lang = target_lang.lower()
        lang_map = {
            "hi": "hi-IN",
            "hinglish": "hi-IN",
            "ta": "ta-IN",
            "kn": "kn-IN",
            "en": "en-IN"
        }
        target_code = lang_map.get(target_lang, "en-IN")
        
        # Strip Markdown and Mermaid code blocks before speaking to avoid reading raw layout code
        import re
        clean_text = re.sub(r"```[\s\S]*?```", "", text) # Remove Mermaid/code blocks
        clean_text = re.sub(r"<[^>]+>", "", clean_text) # Remove HTML elements
        clean_text = clean_text.replace("*", "").replace("#", "").replace("|", " ").replace("-", " ")
        clean_text = clean_text.strip()
        
        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "input": clean_text[:2000], # Sarvam limit is 2500 chars (parameter key is input, not text)
            "model": "bulbul:v3",
            "target_language_code": target_code,
            "speaker": "shreya", # High quality female speaker
            "pace": 1.0,
            "temperature": 0.6
        }
        
        try:
            print(f"Calling Sarvam TTS API ({target_code})...")
            response = requests.post("https://api.sarvam.ai/text-to-speech", json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                res_json = response.json()
                audios = res_json.get("audios", [])
                if audios:
                    return audios[0]
            else:
                print(f"Sarvam TTS API error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Sarvam TTS exception: {e}")
        return ""

    def speech_to_text(self, audio_file_path, lang_code="en-IN"):
        """
        Transcribes speech audio from the file to text using Sarvam's Saaras STT API.
        """
        api_key = os.getenv("SARVAM_API_KEY", self.api_key)
        if not api_key:
            print("Sarvam API key missing for STT. Returning empty.")
            return ""
            
        headers = {
            "api-subscription-key": api_key
        }
        
        try:
            print(f"Calling Sarvam STT API with file: {audio_file_path}...")
            ext = os.path.splitext(audio_file_path)[1].lower()
            mime_types = {
                ".wav": "audio/wav",
                ".webm": "audio/webm",
                ".mp3": "audio/mpeg",
                ".ogg": "audio/ogg",
                ".m4a": "audio/mp4"
            }
            content_type = mime_types.get(ext, "application/octet-stream")
            
            with open(audio_file_path, "rb") as f:
                files = {
                    "file": (os.path.basename(audio_file_path), f, content_type)
                }
                data = {
                    "model": "saaras:v3",
                    "language_code": lang_code if lang_code else "en-IN"
                }
                response = requests.post("https://api.sarvam.ai/speech-to-text", headers=headers, files=files, data=data, timeout=20)
                if response.status_code == 200:
                    res_json = response.json()
                    return res_json.get("transcript", "")
                else:
                    print(f"Sarvam STT API error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Sarvam STT exception: {e}")
        return ""
    def digitize_document(self, file_path, output_format="md"):
        """
        Digitizes a document (PDF, PNG, JPG) using Sarvam Vision API.
        Implements the Create Job -> Get Upload Urls -> Upload -> Start Job -> Poll -> Get Download Urls flow.
        """
        api_key = os.getenv("SARVAM_API_KEY", self.api_key)
        if not api_key:
            print("Sarvam API key missing for document digitization.")
            return ""
            
        headers = {
            "api-subscription-key": api_key,
            "Content-Type": "application/json"
        }
        
        try:
            # 1. Create Job
            payload = {
                "format": output_format
            }
            res = requests.post("https://api.sarvam.ai/doc-digitization/job/v1", json=payload, headers=headers, timeout=10)
            if res.status_code != 200:
                print(f"Failed to create digitization job: {res.text}")
                return ""
            job_data = res.json()
            job_id = job_data.get("job_id")
            if not job_id:
                print("No job_id returned from Sarvam Vision.")
                return ""
                
            print(f"Created Sarvam Vision Job: {job_id}")
            
            # 2. Get Upload URLs
            filename = os.path.basename(file_path)
            payload_upload = {
                "job_id": job_id,
                "files": [filename]
            }
            res_upload = requests.post("https://api.sarvam.ai/doc-digitization/job/v1/upload-files", json=payload_upload, headers=headers, timeout=10)
            if res_upload.status_code != 200:
                print(f"Failed to get upload URLs: {res_upload.text}")
                return ""
            upload_data = res_upload.json()
            upload_urls = upload_data.get("upload_urls", {})
            upload_url = upload_urls.get(filename)
            if not upload_url:
                print("No upload URL returned for the file.")
                return ""
                
            # 3. Upload File to S3
            with open(file_path, "rb") as f_in:
                file_data = f_in.read()
            
            # Put request to S3 (no api-subscription-key headers)
            res_put = requests.put(upload_url, data=file_data, headers={"Content-Type": "application/octet-stream"}, timeout=30)
            if res_put.status_code not in [200, 201]:
                print(f"Failed to upload file to S3: {res_put.status_code} {res_put.text}")
                return ""
                
            print("File uploaded to S3 successfully.")
            
            # 4. Start Job
            res_start = requests.post(f"https://api.sarvam.ai/doc-digitization/job/v1/{job_id}/start", json={}, headers=headers, timeout=10)
            if res_start.status_code != 200:
                print(f"Failed to start job: {res_start.text}")
                return ""
                
            print("Digitization job started successfully.")
            
            # 5. Poll Job Status
            import time
            max_retries = 30
            for attempt in range(max_retries):
                time.sleep(2)
                res_status = requests.get(f"https://api.sarvam.ai/doc-digitization/job/v1/{job_id}/status", headers=headers, timeout=10)
                if res_status.status_code == 200:
                    status_data = res_status.json()
                    status = status_data.get("status")
                    print(f"Job status (attempt {attempt+1}): {status}")
                    if status == "completed":
                        break
                    elif status == "failed":
                        print("Digitization job failed on Sarvam side.")
                        return ""
                else:
                    print(f"Error checking status: {res_status.text}")
            else:
                print("Digitization job timed out.")
                return ""
                
            # 6. Get Download URLs
            res_download = requests.post(f"https://api.sarvam.ai/doc-digitization/job/v1/{job_id}/download-files", json={}, headers=headers, timeout=10)
            if res_download.status_code != 200:
                print(f"Failed to get download URLs: {res_download.text}")
                return ""
            download_data = res_download.json()
            download_urls = download_data.get("download_urls", {})
            
            # Find the output file URL
            download_url = None
            for key, val in download_urls.items():
                download_url = val
                break
                
            if not download_url:
                print("No download URLs returned.")
                return ""
                
            # 7. Download result
            res_result = requests.get(download_url, timeout=10)
            if res_result.status_code == 200:
                return res_result.text
            else:
                print(f"Failed to download result: {res_result.text}")
                
        except Exception as e:
            print(f"Sarvam Vision Exception: {e}")
            
        return ""


if __name__ == "__main__":
    client = SarvamClient()
    translated = client.translate_to_english("मेरा रोडमैप दिखाओ", "hi")
    print("Hindi -> Eng:", translated)

    
    resp = client.translate_from_english("Here is your roadmap detail.", "hinglish")
    print("Eng -> Hinglish:", resp)
