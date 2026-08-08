# AI Email & WhatsApp Assistant Module

This module provides a FastAPI-based backend service for AI-powered email and WhatsApp workflows.

## Features
- Email drafting, auto-reply, summarization, classification, prioritization, and follow-up suggestions
- WhatsApp support replies, order confirmations, recommendations, invoice sharing, and voice-message handling
- Placeholder integrations for Gmail, Outlook, and WhatsApp Business APIs
- OpenAPI documentation at /docs

## Run locally
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in the values.
3. Start the API: `uvicorn app.main:app --reload`

## Run with Docker
- `docker-compose up --build`

## Test
- `pytest -q`
