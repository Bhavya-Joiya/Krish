# Smart Crop Bot — Application Workflow

**Complete End-to-End Flow**  
Hackathon MVP · August 2026

---

## 1. High-Level Architecture Flow

```
Farmer (WhatsApp) → Twilio Webhook → FastAPI Backend → AI Processing → Reply → Farmer
```

Every message follows the same high-level path. The system then branches based on message type.

---

## 2. Detailed Step-by-Step Workflow

### Step 1 — Farmer Sends a Message

The farmer opens WhatsApp and sends one of the following to the bot number:

- A crop photo (image)
- A voice note (audio)
- A text message
- A location pin (optional, for weather)

No app download or login is required.

### Step 2 — Message Reaches the Backend

- Twilio (or Meta test number) sends an HTTP POST to the webhook endpoint.
- FastAPI receives the request at `/webhooks/twilio/whatsapp` (or equivalent).
- The payload contains message type, media URL (if any), sender phone number, and text body.

### Step 3 — Message Type Detection

The backend inspects the incoming payload and routes it:

| Message Type | Action Taken |
| --- | --- |
| Image | Crop Diagnosis Flow |
| Audio / Voice Note | Speech-to-Text → then treat as Text Flow |
| Text | Normal Chat / Intent Detection Flow |
| Location | Save lat/long against farmer phone number |

### Step 4A — Crop Photo Diagnosis Flow

1. Download the image from the Twilio/WhatsApp media URL.
2. Validate and resize the image using Pillow (reject non-images, limit size).
3. Send the image to Google Gemini 2.0 Flash (Vision mode).
4. Gemini returns: disease/pest name, short explanation, confidence, and recommended actions.
5. Format a clear, short, farmer-friendly Hindi/Hinglish reply.
6. Optionally convert the reply to voice using edge-tts.
7. Send the reply (text + optional voice) back to the farmer on WhatsApp.

### Step 4B — Voice Note Flow

1. Download the audio file from the media URL.
2. Convert format if necessary (WhatsApp OGG → WAV) using ffmpeg.
3. Send audio to Groq Whisper-large-v3 for transcription.
4. If Groq fails or is rate-limited → fall back to local faster-whisper.
5. Obtain Hindi/English text transcript.
6. Treat the transcript exactly like a normal text message and continue to Step 4C.

### Step 4C — Text / Intent Flow

1. Send the text (original or transcribed) to Gemini 2.0 Flash.
2. The model understands the farmer’s intent (weather, mandi price, general advice, follow-up on diagnosis, etc.).
3. If extra data is needed, the system calls the appropriate tool:
   - **Weather** → OpenWeather using farmer’s saved location
   - **Mandi price** → return simple hardcoded or cached sample data
   - **General knowledge** → use a short hardcoded agriculture context string
4. Gemini generates a final helpful reply in simple Hindi/Hinglish.

### Step 5 — Generate and Send Reply

- The final text reply is ready.
- If the original message was a voice note (or farmer preference is voice), convert text → speech with edge-tts.
- Send text message and/or voice note back via Twilio WhatsApp API.
- Farmer receives the reply in the same WhatsApp chat.

### Step 6 — Logging and Admin Visibility

- Save: farmer phone number, incoming message type, content summary, AI diagnosis/reply, timestamp.
- Store in Supabase Postgres or local SQLite.
- Admin can open the Streamlit dashboard and see recent conversations and diagnoses.

---

## 3. Component Responsibility Map

| Component | Exact Role in the Flow |
| --- | --- |
| Twilio WhatsApp Sandbox | Entry and exit point for all farmer messages |
| FastAPI | Receives webhook, detects type, orchestrates entire pipeline |
| Pillow | Validates and resizes crop photos |
| Gemini 2.0 Flash | Vision diagnosis + text understanding + reply generation |
| Groq Whisper | Converts voice notes into text |
| faster-whisper | Local STT fallback if Groq is unavailable |
| edge-tts | Converts bot text replies into Hindi voice messages |
| OpenWeather | Provides location-based weather data |
| Supabase / SQLite | Stores farmers, conversations, and diagnoses |
| Streamlit | Simple admin view of recent activity |
| ngrok | Exposes local FastAPI to Twilio during development |
| Render / Railway | Hosts the live demo backend |

---

## 4. Example Happy-Path Demo Flow

### Scenario: Farmer sends a diseased leaf photo

1. Farmer opens WhatsApp and sends a clear photo of a yellow-spotted leaf.
2. Twilio delivers the image to FastAPI webhook.
3. FastAPI downloads the image, validates it with Pillow.
4. Image is sent to Gemini 2.0 Flash Vision.
5. Gemini responds: “यह Alternaria Leaf Spot (अर्ली ब्लाइट) है। पत्तियों पर भूरे धब्बे दिखाई दे रहे हैं। …”
6. Bot formats a short Hindi reply with treatment advice.
7. Reply is sent back as text (and optionally as voice via edge-tts).
8. Conversation is saved. Admin can see it on Streamlit.

**Total expected time from photo to reply: 8–15 seconds** under normal free-tier conditions.

---

## 5. Error and Fallback Handling

- Gemini fails or rate-limited → switch to Groq Llama Vision
- Groq Whisper fails → switch to local faster-whisper
- TTS fails → send text-only reply
- OpenWeather fails → reply with a polite “मौसम की जानकारी अभी उपलब्ध नहीं है”
- Any unhandled error → log it and send a friendly fallback message to the farmer
