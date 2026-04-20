# Quick API Reference Card

## Start the Server
```bash
python manage.py runserver
```

## Create an Event

### Minimal Request
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "42", "event_type": "page_view"}'
```

### Full Request
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "page_view",
    "page_url": "https://example.com/products/laptop",
    "target_id": "prod_123",
    "metadata": {"browser": "Chrome", "device": "desktop"}
  }'
```

## Event Types
- `click` - User clicks on an element
- `page_view` - User views a page
- `navigation` - User navigates to a new page
- `add_to_cart` - User adds item to cart

## Required Fields
- `user_id` (string)
- `event_type` (string)

## Optional Fields
- `page_url` (URL string)
- `target_id` (string)
- `created_at` (ISO 8601 datetime)
- `metadata` (JSON object)

## Response (Success)
```json
{
  "event_id": "evt_a1b2c3d4e5f6",
  "user_id": "42",
  "event_type": "page_view",
  "created_at": "2026-04-20T17:00:00",
  "status": "created",
  "message": "Event created successfully"
}
```

## Response (Error)
```json
{
  "error": "Invalid request data",
  "details": {
    "user_id": ["This field is required."]
  }
}
```

## Test the API
```bash
python test_api.py
```

## View API Docs
```bash
curl http://127.0.0.1:8000/api/events/
```

## PowerShell (Windows)
```powershell
$body = @{user_id="42"; event_type="page_view"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/" -Method Post -Body $body -ContentType "application/json"
```

## Python
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/events/",
    json={"user_id": "42", "event_type": "page_view"}
)
print(response.json())
```

## Status Codes
- `200 OK` - GET request successful
- `201 Created` - Event created successfully
- `400 Bad Request` - Validation error
- `500 Internal Server Error` - Storage error (HBase unavailable)

## HBase Requirements
For full functionality, ensure:
1. HBase is running
2. Thrift server is running on port 9090
3. Tables are created: `python manage.py setup_hbase`

## Common Issues

**"Could not connect to HBase"**
- Start HBase: `hbase thrift start`
- Check port 9090 is accessible
- Verify `.env` configuration

**"This field is required"**
- Include both `user_id` and `event_type` in request
- Check JSON syntax

**"Invalid choice"**
- Use only: click, page_view, navigation, add_to_cart
- Check spelling and case
