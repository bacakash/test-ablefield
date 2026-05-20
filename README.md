# Customer AI Agent + CRM Demo

A modular FastAPI backend that includes:
- Customer records
- CRM notes and support tickets
- Customer conversation handling
- Rule-based intent detection and sentiment scoring
- CRM automation
- Analytics summary endpoints

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Main API Endpoints

- `GET /health`
- `POST /customers`
- `GET /customers/{customer_id}`
- `POST /customers/{customer_id}/notes`
- `POST /customers/{customer_id}/tickets`
- `POST /conversations/{customer_id}/message`
- `GET /conversations/{customer_id}`
- `GET /analytics/summary`

## Notes

This project is intentionally backend-focused and can be paired later with a UI test fixture for accessibility/compliance testing.
