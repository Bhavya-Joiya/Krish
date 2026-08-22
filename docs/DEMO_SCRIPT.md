# Smart Crop Bot — Live Demo Script (~60–90 seconds)

## One-line pitch (say first)

> Smart Crop Bot is an AI farming advisor inside WhatsApp — farmers send a photo or voice note in Hindi and get instant crop advice, with no app download.

## Pre-demo (T-minus 2 minutes)

1. Confirm http://YOUR_URL/health → `"phase": 5`, keys true  
2. Run: `.venv\Scripts\python.exe scripts\prewarm.py --base http://YOUR_URL`  
3. Open Streamlit admin and Web Chat backup tab  
4. Phone unlocked, sandbox joined, 3 leaf photos ready  

## Live path (in order)

### 1) Wow — photo diagnosis (core)

- Send a clear diseased leaf photo on WhatsApp  
- Narrate: “Farmer sends a photo — no app, no form.”  
- When reply arrives (~8–15s): point to disease name + क्या करें steps  
- Optional: Hindi voice note arrives after text  

### 2) Voice note

- Send: “टमाटर में पत्ते पीले हो रहे हैं, क्या करूँ?”  
- Show “आपने कहा: …” transcript + advice  

### 3) Weather

- Share location once (if not already)  
- Ask: “आज मौसम कैसा है?”  
- Show temperature / tip  

### 4) Mandi

- Ask: “टमाटर का मंडी भाव?”  
- Note honestly: “Demo sample prices for the hackathon.”  

### 5) Admin

- Refresh Streamlit → conversations + diagnoses visible  

## Backup if WhatsApp fails

1. Open `/chat`  
2. **Text** — crop question in Hindi or English  
3. **Image** — public direct leaf/crop photo URL  
4. **Location** — demo pin (Delhi) then ask weather  

Voice notes are **WhatsApp only** — not available in the browser backup.

## If something errors live

| Symptom | Line to say | Action |
| --- | --- | --- |
| Slow reply | “Free-tier models warming — usually under 15 seconds.” | Wait; avoid spam |
| Voice missing | “Text always arrives; voice is optional TTS.” | Continue |
| Weather fail | “We degrade gracefully — still advisory-first.” | Show mandi/photo |
| Sandbox limit | “Backup web channel uses the same AI pipeline.” | Switch to `/chat` |

## Closing line

> Meet farmers where they already are — WhatsApp — with vision, voice, and practical Hindi advice.
