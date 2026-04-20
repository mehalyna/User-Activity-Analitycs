# API Examples

## Event Collection API

### Endpoint
`POST /api/events/`

### Base URL
```
http://127.0.0.1:8000/api/events/
```

## Request Examples

### 1. Page View Event

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "page_view",
    "page_url": "https://example.com/products/laptop",
    "target_id": "prod_laptop_001",
    "metadata": {
      "browser": "Chrome",
      "device": "desktop",
      "screen_resolution": "1920x1080"
    }
  }'
```

**Response (201 Created):**
```json
{
  "event_id": "evt_a1b2c3d4e5f6",
  "user_id": "42",
  "event_type": "page_view",
  "created_at": "2026-04-20T17:00:00.000000",
  "status": "created",
  "message": "Event created successfully"
}
```

### 2. Click Event

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "click",
    "page_url": "https://example.com/products/laptop",
    "target_id": "btn_add_to_cart",
    "metadata": {
      "button_text": "Add to Cart",
      "position": "top-right"
    }
  }'
```

### 3. Add to Cart Event

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "add_to_cart",
    "page_url": "https://example.com/products/laptop",
    "target_id": "prod_laptop_001",
    "metadata": {
      "product_name": "Gaming Laptop",
      "price": 1299.99,
      "quantity": 1,
      "currency": "USD"
    }
  }'
```

### 4. Navigation Event

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "navigation",
    "page_url": "https://example.com/category/electronics",
    "metadata": {
      "from_url": "https://example.com/home",
      "navigation_type": "menu_click"
    }
  }'
```

### 5. Minimal Event (Only Required Fields)

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "page_view"
  }'
```

### 6. Event with Custom Timestamp

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "click",
    "created_at": "2026-04-20T15:30:00Z",
    "page_url": "https://example.com/products/laptop"
  }'
```

## PowerShell Examples (Windows)

### Basic Event Creation

```powershell
$body = @{
    user_id = "42"
    event_type = "page_view"
    page_url = "https://example.com/products/laptop"
    metadata = @{
        browser = "Edge"
        device = "desktop"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/events/" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## Python Examples

### Using requests library

```python
import requests
import json

url = "http://127.0.0.1:8000/api/events/"

event_data = {
    "user_id": "42",
    "event_type": "page_view",
    "page_url": "https://example.com/products/laptop",
    "target_id": "prod_laptop_001",
    "metadata": {
        "browser": "Chrome",
        "device": "desktop"
    }
}

response = requests.post(url, json=event_data)

if response.status_code == 201:
    print("Event created successfully!")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Batch Event Creation

```python
import requests
from datetime import datetime, timedelta

url = "http://127.0.0.1:8000/api/events/"

# Create multiple events for the same user
user_id = "42"
events = []

for i in range(5):
    event = {
        "user_id": user_id,
        "event_type": "page_view",
        "page_url": f"https://example.com/page{i}",
        "metadata": {
            "session_id": "sess_123",
            "sequence": i
        }
    }
    
    response = requests.post(url, json=event)
    if response.status_code == 201:
        events.append(response.json())
        print(f"Created event {i+1}: {response.json()['event_id']}")

print(f"\nTotal events created: {len(events)}")
```

## Error Examples

### Missing Required Field

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view"
  }'
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid request data",
  "details": {
    "user_id": ["This field is required."]
  }
}
```

### Invalid Event Type

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "invalid_type"
  }'
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid request data",
  "details": {
    "event_type": ["\"invalid_type\" is not a valid choice."]
  }
}
```

### Future Timestamp

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "42",
    "event_type": "click",
    "created_at": "2030-01-01T00:00:00Z"
  }'
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid request data",
  "details": {
    "created_at": ["Event timestamp cannot be in the future"]
  }
}
```

## API Documentation Endpoint

To view API documentation in your browser or via curl:

```bash
curl -X GET http://127.0.0.1:8000/api/events/
```

**Response:**
```json
{
  "endpoint": "/api/events/",
  "method": "POST",
  "description": "Create a new user activity event",
  "required_fields": ["user_id", "event_type"],
  "optional_fields": ["page_url", "target_id", "created_at", "metadata"],
  "event_types": ["click", "page_view", "navigation", "add_to_cart"],
  "example_request": {
    "user_id": "42",
    "event_type": "page_view",
    "page_url": "https://example.com/products/laptop",
    "target_id": "prod_123",
    "metadata": {
      "browser": "Chrome",
      "device": "desktop"
    }
  }
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Unique identifier for the user (max 100 chars) |
| `event_type` | string | Yes | Type of event: `click`, `page_view`, `navigation`, or `add_to_cart` |
| `page_url` | string | No | URL where the event occurred |
| `target_id` | string | No | Target identifier (e.g., product ID, button ID) (max 200 chars) |
| `created_at` | datetime | No | ISO 8601 timestamp. Defaults to current UTC time. Cannot be in the future. |
| `metadata` | object | No | JSON object with additional event data |

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | Unique identifier for the event (format: `evt_` + 12 hex chars) |
| `user_id` | string | User identifier from request |
| `event_type` | string | Event type from request |
| `created_at` | string | ISO 8601 timestamp of event creation |
| `status` | string | Status of the operation (always `created` on success) |
| `message` | string | Success message |

## Testing Tips

1. **Test without HBase**: The API validates requests even if HBase isn't running. You'll get validation errors (400) correctly, but storage errors (500) if HBase is unavailable.

2. **Use the test script**:
   ```bash
   python test_api.py
   ```

3. **Test with Django shell**:
   ```bash
   python manage.py shell
   ```
   ```python
   from events.serializers import EventSerializer
   
   data = {"user_id": "42", "event_type": "page_view"}
   serializer = EventSerializer(data=data)
   serializer.is_valid()
   print(serializer.validated_data)
   ```

4. **Monitor server logs**: Run the dev server with:
   ```bash
   python manage.py runserver
   ```
   All requests will be logged to the console.
