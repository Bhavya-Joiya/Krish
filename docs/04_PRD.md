# Smart Crop Bot — Product Requirements Document (PRD)

Hackathon MVP · Version 1.0 · August 22, 2026

---

## 1. Document Purpose

This PRD defines the scope, requirements, user stories, success criteria, and constraints for the Smart Crop Bot hackathon MVP. It is the **single source of truth** for what must be built and what must not be built.

---

## 2. Product Overview

| Field | Value |
| --- | --- |
| Product Name | Smart Crop Bot |
| One-line description | An AI-powered WhatsApp advisor that lets Indian farmers diagnose crop problems from photos, ask questions by voice or text, and receive practical advice in Hindi — without installing any app. |
| Product type | Reactive conversational advisory system (not continuous monitoring) |

---

## 3. Goals and Non-Goals

### 3.1 Goals (Must Achieve)

- A farmer can send a crop photo on WhatsApp and receive a useful diagnosis + advice within ~15 seconds.
- A farmer can send a Hindi/Hinglish voice note and receive a relevant reply.
- A farmer can have a basic text conversation about crops, weather, or prices.
- The bot can reply with a Hindi voice message.
- The system runs entirely on free tiers for the duration of the hackathon.
- A simple admin view shows recent conversations.

### 3.2 Non-Goals (Explicitly Out of Scope)

- Continuous satellite or sensor-based farm monitoring
- Full multi-language support beyond Hindi + English/Hinglish
- Complex proactive notification engine
- Full KVK / expert escalation workflow
- Production-grade Meta WhatsApp Business verification
- RAG / vector search knowledge base
- Full Celery distributed task system
- ISRO Bhuvan or advanced satellite data integration

---

## 4. Target Users

| Attribute | Description |
| --- | --- |
| Primary User | Small / marginal farmer in rural India |
| Language | Hindi and Hinglish (MVP) |
| Device | Android smartphone with WhatsApp |
| Literacy | Low to moderate — voice and simple language essential |
| Secondary User | Hackathon judges and internal team (via Streamlit admin) |

---

## 5. User Stories

### US-01 — Photo Diagnosis

As a farmer, I want to send a photo of my crop so that I can immediately know what disease or pest is affecting it and what I should do next.

### US-02 — Voice Question

As a farmer, I want to send a voice note in Hindi asking about my crop or weather so that I do not have to type.

### US-03 — Text Advice

As a farmer, I want to ask simple text questions and receive clear, short answers in Hindi or Hinglish.

### US-04 — Voice Reply

As a farmer, I want the bot to sometimes reply with a voice message so that I can listen instead of reading.

### US-05 — Weather

As a farmer, I want to ask about the weather for my area so that I can decide whether to spray or irrigate.

### US-06 — Mandi Price

As a farmer, I want a quick idea of current market prices so that I can plan when to sell.

### US-07 — Admin Visibility

As a team member, I want to see recent farmer conversations and diagnoses so that I can demonstrate the system and debug issues.

---

## 6. Functional Requirements

### 6.1 Must-Have Requirements

| ID | Requirement |
| --- | --- |
| FR-01 | System shall accept crop images via WhatsApp and return a diagnosis + simple treatment advice. |
| FR-02 | System shall accept Hindi/Hinglish voice notes, transcribe them, and process the resulting text. |
| FR-03 | System shall accept text messages in Hindi or English and generate relevant replies. |
| FR-04 | System shall be able to convert text replies into Hindi speech and send them as WhatsApp voice messages. |
| FR-05 | System shall provide a simple weather reply using farmer location and OpenWeather free tier. |
| FR-06 | System shall provide a simple mandi price reply (hardcoded or cached samples acceptable for MVP). |
| FR-07 | System shall store conversations and expose a basic admin view (Streamlit). |
| FR-08 | All core flows shall work on free-tier services for the duration of the hackathon demo. |

### 6.2 Nice-to-Have (Only if time permits)

- Location sharing and persistent storage of farmer location
- Slightly richer weather interpretation
- Basic rate limiting and duplicate message protection

---

## 7. Non-Functional Requirements

- Response time for photo diagnosis: ideally under 15 seconds
- System must remain usable within free-tier rate limits during a live demo
- Graceful degradation: if any AI service fails, fall back or send a polite error message
- No credit card or paid plan should be required to run the demo

---

## 8. Success Metrics for the Hackathon

- Live demo of photo → diagnosis works end-to-end
- Live demo of voice note → reply works end-to-end
- Judges can understand the value in under 60 seconds of explanation
- No critical crash during the presentation
- Admin page shows at least the demo conversations

---

## 9. Constraints and Assumptions

- Hackathon duration is 48–72 hours maximum
- Team will strictly follow the Scope Lock
- Free-tier rate limits are sufficient for a short demo
- Telegram Sandbox limits are acceptable for the presentation
- Internet connectivity will be available during the demo

---

## 10. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Free-tier rate limits hit during demo | Have Groq + local faster-whisper fallbacks ready; pre-warm services |
| Telegram rate limits | Prepare a simple Web Chat UI as backup demo channel |
| Slow photo processing | Keep processing synchronous first; add background task only if needed |
| Scope creep | Strict Scope Lock section — no new features after lock |
| API key or service downtime | Multiple model fallbacks (Gemini ↔ Groq) and text-only fallback |

---

## 11. Hackathon Scope Lock (Non-Negotiable)

### Must work in demo

- Crop photo → diagnosis + advice (Gemini Vision)
- Text chat in Hindi / English
- Voice note → text (Groq Whisper primary, faster-whisper fallback)
- Text reply → voice (edge-tts)
- One simple weather reply
- One simple mandi price reply (hardcoded or cached)
- Basic admin view of recent conversations (Streamlit)

### Explicitly out of scope

- Full Celery architecture
- RAG / pgvector
- ISRO Bhuvan
- Multiple regional languages beyond Hindi
- Complex proactive messaging
- Full KVK / expert escalation system
- Continuous farm monitoring

---

## 12. Future Roadmap (Post-Hackathon)

- Move to Meta WhatsApp Business Cloud API for real farmer numbers
- Upgrade TTS to Sarvam Bulbul or Bhashini for higher quality
- Add proper RAG for richer agricultural knowledge
- Explore satellite / NDVI based insights
- Build full admin and analytics dashboard
- Support additional Indian languages
- Introduce simple proactive alerts (weather warnings, follow-ups)
