# API Reference

## Health
- GET /health
- Returns service status.

## Email endpoints
- POST /email/draft
  - Body: {"instruction": "..."}
  - Returns a draft subject and body.
- POST /email/auto-reply
  - Body: {"sender": "...", "subject": "...", "body": "..."}
  - Returns an AI-generated reply.
- POST /email/summarize
  - Body: {"messages": ["..."]}
  - Returns a summary string.
- POST /email/classify
  - Body: {"subject": "...", "body": "..."}
  - Returns a category and confidence score.
- POST /email/prioritize
  - Body: {"emails": ["..."]}
  - Returns ranked emails.
- POST /email/follow-up
  - Body: {"instruction": "..."}
  - Returns a follow-up suggestion.

## WhatsApp endpoints
- POST /whatsapp/support-reply
- POST /whatsapp/order-confirmation
- POST /whatsapp/recommend
- POST /whatsapp/send-invoice
- POST /whatsapp/voice-message
- POST /whatsapp/webhook
