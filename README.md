# AI Receptionist

AI Receptionist is a multi-industry voice receptionist MVP. You teach the receptionist a business
by creating one JSON profile, then callers can speak with it through LiveKit voice. It greets
callers, answers from the profile, takes messages, captures appointment requests, saves leads, and
asks for human callbacks when it should not guess.

## Project Snapshot

- Full-stack voice AI MVP with a React frontend and Python backend.
- LiveKit-powered browser voice calls.
- OpenAI realtime audio agent with business-specific prompts.
- SQLite lead capture for customers, messages, callbacks, and appointment requests.
- Reusable business profile system for adapting the receptionist to different industries.

## What This Does

- Browser voice call UI with LiveKit.
- AI voice receptionist powered by LiveKit Agents and OpenAI realtime audio.
- Business knowledge loaded from `backend/business_profile.json`.
- Local language/accent/persona settings through env and the profile.
- Lead, customer, message, appointment request, and callback capture in SQLite.
- Token server for creating LiveKit rooms.

## Teach The Agent

Copy the sample profile:

```bash
cp backend/business_profile.sample.json backend/business_profile.json
```

Put the business name, industry, market, services, FAQs, handoff rules, and fallback answer there.
The sample file is a dental clinic example:

```bash
backend/business_profile.sample.json
```

This is the main product idea: for every client, create a business profile and the same agent can
work for a clinic, school, repair shop, salon, real estate office, restaurant, coaching business,
ecommerce brand, or any other service.

## Project Structure

- `backend/agent.py` starts the LiveKit AI worker.
- `backend/prompts.py` builds the agent instructions from the business profile.
- `backend/api.py` exposes tools for knowledge lookup, lead capture, appointments, messages, customer save, and callbacks.
- `backend/db_driver.py` stores customers and leads in SQLite.
- `backend/server.py` serves `/getToken` and `/health` for the frontend.
- `frontend/` contains the Vite/React customer UI.

## Setup

### 1. Backend environment

Copy `backend/sample.env` to `backend/.env`, then fill in:

```bash
LIVEKIT_URL="wss://your-livekit-project.livekit.cloud"
LIVEKIT_API_KEY="your-livekit-api-key"
LIVEKIT_API_SECRET="your-livekit-api-secret"
OPENAI_API_KEY="your-openai-api-key"
OPENAI_REALTIME_MODEL="gpt-realtime"
```

Tune the local voice/persona:

```bash
BUSINESS_PROFILE_PATH="business_profile.json"
ASSISTANT_LANGUAGE="English and Hindi"
ASSISTANT_ACCENT="friendly local Indian English accent"
ASSISTANT_MARKET="India"
ASSISTANT_VOICE="marin"
```

### 2. Frontend environment

Copy `frontend/sample.env` to `frontend/.env`, then set:

```bash
VITE_LIVEKIT_URL="wss://your-livekit-project.livekit.cloud"
```

### 3. Install and run

Backend:

```bash
cd backend
pip install -r requirements.txt
python server.py
```

In a second terminal:

```bash
cd backend
python agent.py dev
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, enter a name, and connect. Try saying: "I want to book an appointment tomorrow"
or "Please take a message for the owner."

Quick frontend commands from the repo root:

```bash
npm run frontend:dev
npm run frontend:build
npm run frontend:lint
```

## Real Phone Calls

The current app supports voice through the browser. For a real receptionist phone number, add a phone
provider/SIP trunk connected to LiveKit SIP. Then inbound calls route into the same LiveKit room and
the same receptionist answers.

## Sellable MVP Roadmap

- Admin screen for uploading business details instead of editing JSON.
- Real phone number via LiveKit SIP.
- Call recordings and transcripts.
- Lead dashboard with callback status.
- WhatsApp/SMS follow-up after calls.
- Per-client deployment and billing.
