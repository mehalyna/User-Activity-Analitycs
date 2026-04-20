# User Events API Documentation

## Endpoint

`GET /api/users/{user_id}/events/`

Retrieve activity events for a specific user with optional filtering.

## Base URL

```
http://127.0.0.1:8000/api/users/{user_id}/events/
```

## Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Unique identifier for the user |

## Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `start_date` | string | No | Start date for filtering (YYYY-MM-DD format, inclusive) | `2026-04-01` |
| `end_date` | string | No | End date for filtering (YYYY-MM-DD format, inclusive) | `2026-04-30` |
| `limit` | integer | No | Maximum number of events to return | `100` |

## Request Examples

### 1. Get All Events for a User

```bash
curl http://127.0.0.1:8000/api/users/user_42/events/
```

### 2. Get Events for a Specific Date Range

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-01&end_date=2026-04-30"
```

### 3. Get Limited Number of Events

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?limit=50"
```

### 4. Combine Date Range and Limit

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-20&end_date=2026-04-21&limit=10"
```

### 5. Get Events from a Specific Date

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-20&end_date=2026-04-20"
```

## Response Format

### Success Response (200 OK)

```json
{
  "user_id": "user_42",
  "total_events": 15,
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "limit": null,
  "events": [
    {
      "event_id": "evt_a1b2c3d4e5f6",
      "user_id": "user_42",
      "event_type": "page_view",
      "date": "2026-04-20",
      "created_at": "2026-04-20T10:30:15",
      "page_url": "https://example.com/products/laptop",
      "target_id": "prod_laptop_001",
      "metadata": {
        "browser": "Chrome",
        "device": "desktop",
        "session_id": "sess_1234"
      }
    },
    {
      "event_id": "evt_b2c3d4e5f6g7",
      "user_id": "user_42",
      "event_type": "click",
      "date": "2026-04-20",
      "created_at": "2026-04-20T10:31:22",
      "page_url": "https://example.com/products/laptop",
      "target_id": "btn_add_to_cart",
      "metadata": {
        "button_text": "Add to Cart",
        "position": "top-right"
      }
    }
  ]
}
```

### Empty Results (200 OK)

```json
{
  "user_id": "user_42",
  "total_events": 0,
  "start_date": null,
  "end_date": null,
  "limit": null,
  "events": []
}
```

### Error Response (400 Bad Request)

**Invalid Date Format:**
```json
{
  "error": "Invalid start_date parameter",
  "message": "Date must be in YYYY-MM-DD format"
}
```

**Invalid Limit:**
```json
{
  "error": "Invalid limit parameter",
  "message": "Limit must be a positive integer"
}
```

**Invalid Date Range:**
```json
{
  "error": "Invalid date range",
  "message": "start_date must be before or equal to end_date"
}
```

### Error Response (500 Internal Server Error)

```json
{
  "error": "Failed to retrieve events",
  "message": "An error occurred while retrieving events"
}
```

## Response Fields

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | string | User identifier from the request |
| `total_events` | integer | Total number of events returned |
| `start_date` | string or null | Start date filter applied (if any) |
| `end_date` | string or null | End date filter applied (if any) |
| `limit` | integer or null | Limit applied (if any) |
| `events` | array | Array of event objects |

### Event Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string | Unique event identifier |
| `user_id` | string | User who triggered the event |
| `event_type` | string | Type of event (click, page_view, navigation, add_to_cart) |
| `date` | string | Date of the event (YYYY-MM-DD) |
| `created_at` | string | ISO 8601 timestamp of when the event occurred |
| `page_url` | string | URL where the event occurred (may be empty) |
| `target_id` | string | Target identifier (may be empty) |
| `metadata` | object | Additional event metadata (may be empty) |

## PowerShell Examples (Windows)

### Get All Events
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/user_42/events/" -Method Get
```

### Get Events with Date Range
```powershell
$params = @{
    start_date = "2026-04-01"
    end_date = "2026-04-30"
}
$query = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/user_42/events/?$query" -Method Get
```

### Get Limited Events
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/user_42/events/?limit=10" -Method Get
```

## Python Examples

### Using requests library

```python
import requests

# Get all events
response = requests.get("http://127.0.0.1:8000/api/users/user_42/events/")
data = response.json()

print(f"Total events: {data['total_events']}")
for event in data['events']:
    print(f"{event['created_at']} - {event['event_type']}: {event['page_url']}")
```

### With Date Filtering

```python
import requests

params = {
    'start_date': '2026-04-01',
    'end_date': '2026-04-30'
}

response = requests.get(
    "http://127.0.0.1:8000/api/users/user_42/events/",
    params=params
)

data = response.json()
print(f"Events from {data['start_date']} to {data['end_date']}: {data['total_events']}")
```

### With Limit

```python
import requests

response = requests.get(
    "http://127.0.0.1:8000/api/users/user_42/events/",
    params={'limit': 50}
)

data = response.json()
print(f"Retrieved {len(data['events'])} events (limit: {data['limit']})")
```

### Process Events

```python
import requests
from collections import Counter

response = requests.get("http://127.0.0.1:8000/api/users/user_42/events/")
data = response.json()

# Count events by type
event_types = Counter(event['event_type'] for event in data['events'])
print("Event distribution:")
for event_type, count in event_types.items():
    print(f"  {event_type}: {count}")

# Get unique pages visited
pages = set(event['page_url'] for event in data['events'] if event['page_url'])
print(f"\nUnique pages visited: {len(pages)}")
```

## JavaScript/Fetch Example

```javascript
// Get user events
async function getUserEvents(userId, startDate = null, endDate = null, limit = null) {
    const params = new URLSearchParams();
    
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (limit) params.append('limit', limit);
    
    const url = `http://127.0.0.1:8000/api/users/${userId}/events/?${params}`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    return data;
}

// Usage
getUserEvents('user_42', '2026-04-01', '2026-04-30', 50)
    .then(data => {
        console.log(`Total events: ${data.total_events}`);
        data.events.forEach(event => {
            console.log(`${event.created_at} - ${event.event_type}`);
        });
    });
```

## Use Cases

### 1. User Activity Timeline

Get all events for a user to build an activity timeline:

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?limit=100"
```

### 2. Daily Activity Report

Get events for a specific day:

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-20&end_date=2026-04-20"
```

### 3. Monthly Summary

Get all events for a month:

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-01&end_date=2026-04-30"
```

### 4. Recent Activity

Get the most recent events:

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?limit=10"
```

### 5. Activity During Campaign

Get events during a specific campaign period:

```bash
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-15&end_date=2026-04-22"
```

## Event Ordering

Events are returned in chronological order based on the row key design (`user_id#date#event_id`), which naturally sorts by:
1. User ID
2. Date
3. Event ID (which includes timestamp information)

## Pagination

Currently, the API supports basic pagination through the `limit` parameter. For large result sets:

1. Use `limit` to control the number of events returned
2. Use `start_date` and `end_date` to narrow the time range
3. Consider requesting data in smaller time windows (e.g., day by day)

**Example: Paginate by date**
```bash
# Week 1
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-01&end_date=2026-04-07"

# Week 2
curl "http://127.0.0.1:8000/api/users/user_42/events/?start_date=2026-04-08&end_date=2026-04-14"
```

## Performance Considerations

- **Row Key Design**: The `user_id#date#event_id` format enables efficient scans
- **Date Filtering**: Date range queries are efficient due to the row key structure
- **Limit Parameter**: Use `limit` to reduce data transfer and processing time
- **HBase Scan**: The endpoint uses HBase scan operations, optimized for sequential reads

## Error Handling

### Client-Side Validation

Before making requests, validate:
- Date format is YYYY-MM-DD
- start_date <= end_date
- limit is a positive integer

### Handling Errors

```python
import requests

try:
    response = requests.get(
        "http://127.0.0.1:8000/api/users/user_42/events/",
        params={'start_date': '2026-04-01', 'end_date': '2026-04-30'}
    )
    response.raise_for_status()
    
    data = response.json()
    print(f"Success: {data['total_events']} events")
    
except requests.exceptions.HTTPError as e:
    if response.status_code == 400:
        error_data = response.json()
        print(f"Validation error: {error_data['message']}")
    elif response.status_code == 500:
        print("Server error: Please try again later")
    else:
        print(f"HTTP error: {e}")
        
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
```

## Testing

### Test with Sample Data

```bash
# 1. Generate sample events
python manage.py generate_sample_events --users 5 --events-per-user 20

# 2. Retrieve events for a user
curl "http://127.0.0.1:8000/api/users/user_001/events/"

# 3. Test date filtering
curl "http://127.0.0.1:8000/api/users/user_001/events/?start_date=2026-04-20&end_date=2026-04-20"

# 4. Test limit
curl "http://127.0.0.1:8000/api/users/user_001/events/?limit=5"
```

### Run Automated Tests

```bash
python test_user_events_api.py
```

## Integration Examples

### Dashboard Integration

```javascript
// Fetch and display user activity
async function displayUserActivity(userId) {
    const data = await getUserEvents(userId, null, null, 20);
    
    const timeline = document.getElementById('activity-timeline');
    
    data.events.forEach(event => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
            <div class="time">${event.created_at}</div>
            <div class="type">${event.event_type}</div>
            <div class="url">${event.page_url}</div>
        `;
        timeline.appendChild(item);
    });
}
```

### Analytics Integration

```python
import requests
import pandas as pd

def get_user_events_dataframe(user_id, start_date=None, end_date=None):
    """Get user events as a pandas DataFrame"""
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    response = requests.get(
        f"http://127.0.0.1:8000/api/users/{user_id}/events/",
        params=params
    )
    
    data = response.json()
    df = pd.DataFrame(data['events'])
    
    # Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    return df

# Usage
df = get_user_events_dataframe('user_42', '2026-04-01', '2026-04-30')

# Analyze
print(df['event_type'].value_counts())
print(df.groupby('date').size())
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Events retrieved (may be empty array) |
| 400 | Bad Request - Invalid parameters |
| 500 | Internal Server Error - Storage or processing error |

## Notes

- Empty results return 200 with an empty events array
- Missing query parameters use default values (no filtering)
- All dates are in UTC
- Events are sorted chronologically
- The endpoint works even if HBase is unavailable (returns empty results)
