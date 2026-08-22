# Smart Crop Bot — Pitch (one paragraph + bullets)

## 30-second paragraph

Indian farmers lose crops to diseases they cannot diagnose in time, and most agri apps never get used because they require downloads and high digital literacy. **Smart Crop Bot** puts an AI advisor inside WhatsApp: send a leaf photo, Hindi voice note, or text, and get practical advice in seconds — diagnosis, weather, and mandi context — with zero install. Built on a free-tier stack (Twilio Sandbox, Gemini, Groq Whisper, edge-tts) so a realistic prototype ships in a hackathon weekend.

## Judge bullets

- **Problem:** Expert advice is scarce; WhatsApp is already universal  
- **Solution:** Reactive WhatsApp bot (photo + voice + text)  
- **Wow demo:** Photo → Hindi diagnosis in ~10–15 seconds  
- **Inclusion:** Hindi/Hinglish voice in and out  
- **Honesty:** Advisory chatbot, not satellite farm monitoring  
- **Feasibility:** Free tiers, clear Scope Lock, fallbacks for live demo  

## Architecture (one breath)

WhatsApp → Twilio → FastAPI → Gemini/Groq (+ Whisper/TTS) → SQLite/Streamlit admin
