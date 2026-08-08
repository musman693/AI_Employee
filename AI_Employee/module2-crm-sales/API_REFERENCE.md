# API Reference

## Customers
- `POST /customers` — create a customer
- `GET /customers` — list customers with search/filter pagination
- `GET /customers/{id}` — fetch a customer
- `PATCH /customers/{id}` — update a customer
- `DELETE /customers/{id}` — soft-delete a customer

## Leads
- `POST /leads` — create a lead
- `GET /leads` — list leads
- `PATCH /leads/{id}` — update lead status or owner
- `POST /leads/{id}/convert` — convert a lead to a customer

## Deals
- `POST /deals` — create a deal
- `GET /deals` — list deals filtered by stage and owner
- `PATCH /deals/{id}` — update a deal
- `POST /deals/{id}/stage` — move a deal to a new stage

## Activities
- `POST /activities` — log an activity
- `GET /activities` — list activities filtered by customer/lead/type

## Health
- `GET /health` — simple health check
