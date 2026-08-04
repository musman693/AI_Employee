# Frontend modules

Each product module owns its feature-specific screens, components, data types,
and API integration in a dedicated directory.

## Current modules

- `email-whatsapp/` - Unified Email and WhatsApp assistant inbox (Module 1)
- `crm/` - Customer records, lead management, and sales pipeline (Module 2)
- `finance/` - API-connected quotations, invoices, payments, and finance insights (Module 3)

Application routes under `app/` should remain small and import their interface
from the corresponding module directory.

Module 3 connects to FastAPI through `app/api/backend/[...path]/route.ts`. Set
`BACKEND_URL` when the API is not running at `http://127.0.0.1:8000`.
