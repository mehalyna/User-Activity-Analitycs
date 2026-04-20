# Demo Examples and Presentation Guide

## Quick Start Demo

### 1. Setup (5 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# (Optional) Setup HBase
python manage.py setup_hbase

# Generate demo data
python manage.py generate_demo_data --scenario default

# Start server
python manage.py runserver
```

### 2. Verify Setup

```bash
# Check Django
python manage.py check

# Test HBase connection (if available)
python manage.py test_hbase_connection
```

## Demo Scenarios

### Scenario 1: Default - Balanced Activity

**Generate Data:**
```bash
python manage.py generate_demo_data --scenario default
```

**What it creates:**
- 10 users (demo_user_001 to demo_user_010)
- ~30 events per user over 7 days
- Balanced mix of all event types
- Realistic timestamps and metadata

**Demo Steps:**

1. **Get Daily Report:**
```bash
curl http://127.0.0.1:8000/api/reports/daily/
```

2. **Get User Activity:**
```bash
curl http://127.0.0.1:8000/api/users/demo_user_001/events/
```

3. **Filter by Date:**
```bash
curl "http://127.0.0.1:8000/api/users/demo_user_001/events/?start_date=2026-04-20&limit=10"
```

### Scenario 2: E-commerce - Shopping Journeys

**Generate Data:**
```bash
python manage.py generate_demo_data --scenario ecommerce
```

**What it creates:**
- 5 shoppers (shopper_001 to shopper_005)
- Complete purchase funnels
- Product browsing -> Add to cart -> Checkout sequences
- Realistic e-commerce metadata

**Demo Steps:**

1. **View Complete Shopping Journey:**
```bash
curl http://127.0.0.1:8000/api/users/shopper_001/events/
```

2. **Analyze Add to Cart Events:**
```bash
curl http://127.0.0.1:8000/api/users/shopper_001/events/ | \
  jq '.events[] | select(.event_type == "add_to_cart")'
```

3. **Daily Shopping Report:**
```bash
curl http://127.0.0.1:8000/api/reports/daily/
```

### Scenario 3: Campaign - Marketing Impact

**Generate Data:**
```bash
python manage.py generate_demo_data --scenario campaign
```

**What it creates:**
- 15 campaign users
- Low activity before campaign (7-14 days ago)
- High activity during campaign (last 7 days)
- Campaign attribution metadata

**Demo Steps:**

1. **Compare Pre-Campaign Activity:**
```bash
# Before campaign (14-7 days ago)
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-06&end_date=2026-04-13"
```

2. **During Campaign Activity:**
```bash
# During campaign (last 7 days)
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-14&end_date=2026-04-20"
```

3. **Campaign Attribution:**
```bash
curl http://127.0.0.1:8000/api/users/campaign_user_001/events/ | \
  jq '.events[] | select(.metadata.campaign != null)'
```

### Scenario 4: Minimal - Quick Testing

**Generate Data:**
```bash
python manage.py generate_demo_data --scenario minimal
```

**What it creates:**
- 3 users (alice, bob, charlie)
- 5 events each (15 total)
- Simple, predictable data

**Demo Steps:**

```bash
# View all users' events
curl http://127.0.0.1:8000/api/users/alice/events/
curl http://127.0.0.1:8000/api/users/bob/events/
curl http://127.0.0.1:8000/api/users/charlie/events/

# Daily report
curl http://127.0.0.1:8000/api/reports/daily/
```

## Example API Requests

### Create Events

#### 1. Simple Page View
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "page_view",
    "page_url": "https://example.com/home"
  }'
```

#### 2. Click Event with Metadata
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "click",
    "page_url": "https://example.com/products",
    "target_id": "btn_buy_now",
    "metadata": {
      "button_text": "Buy Now",
      "position": "top-right",
      "color": "green"
    }
  }'
```

#### 3. Add to Cart Event
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_001",
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

#### 4. Navigation Event
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_001",
    "event_type": "navigation",
    "page_url": "https://example.com/category/electronics",
    "metadata": {
      "from_url": "https://example.com/home",
      "navigation_type": "menu_click"
    }
  }'
```

### Retrieve Events

#### 1. All Events for User
```bash
curl http://127.0.0.1:8000/api/users/demo_user_001/events/
```

#### 2. Events with Date Filter
```bash
curl "http://127.0.0.1:8000/api/users/demo_user_001/events/?start_date=2026-04-20&end_date=2026-04-20"
```

#### 3. Limited Results
```bash
curl "http://127.0.0.1:8000/api/users/demo_user_001/events/?limit=10"
```

#### 4. Combined Filters
```bash
curl "http://127.0.0.1:8000/api/users/demo_user_001/events/?start_date=2026-04-15&end_date=2026-04-20&limit=50"
```

### Generate Reports

#### 1. Full Daily Report
```bash
curl http://127.0.0.1:8000/api/reports/daily/
```

#### 2. Weekly Report
```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-14&end_date=2026-04-20"
```

#### 3. Monthly Report
```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-01&end_date=2026-04-30"
```

#### 4. Single Day Report
```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-20&end_date=2026-04-20"
```

## Validation Examples

### Valid Requests

#### User ID Validation
```bash
# Valid: alphanumeric, underscore, hyphen
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "event_type": "page_view"}'

curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user_01", "event_type": "page_view"}'
```

### Invalid Requests (Demonstrate Validation)

#### 1. Empty User ID
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "", "event_type": "page_view"}'

# Expected: 400 Bad Request - "User ID cannot be empty"
```

#### 2. Invalid User ID Characters
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user@email.com", "event_type": "page_view"}'

# Expected: 400 Bad Request - "User ID must contain only alphanumeric..."
```

#### 3. Invalid Event Type
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123", "event_type": "invalid_type"}'

# Expected: 400 Bad Request - "Invalid choice"
```

#### 4. Future Timestamp
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "event_type": "page_view",
    "created_at": "2030-01-01T00:00:00Z"
  }'

# Expected: 400 Bad Request - "Event timestamp cannot be in the future"
```

#### 5. Oversized Metadata
```bash
# Metadata > 10KB
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"user_123\", \"event_type\": \"page_view\", \"metadata\": {\"large_data\": \"$(python -c 'print(\"x\" * 11000)')\" }}"

# Expected: 400 Bad Request - "Metadata size cannot exceed 10KB"
```

## PowerShell Demo Examples

### Create Event
```powershell
$body = @{
    user_id = "demo_user_001"
    event_type = "page_view"
    page_url = "https://example.com/home"
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

### Get User Events
```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/demo_user_001/events/"

Write-Host "Total Events: $($response.total_events)"
$response.events | ForEach-Object {
    Write-Host "$($_.created_at) - $($_.event_type)"
}
```

### Get Daily Report
```powershell
$params = @{
    start_date = "2026-04-01"
    end_date = "2026-04-30"
}
$query = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"

$report = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/reports/daily/?$query"

Write-Host "Total Events: $($report.total_events)"
Write-Host "Total Days: $($report.total_days)"
Write-Host "Unique Users: $($report.total_unique_users)"
```

## Python Demo Script

### Complete Demo Workflow
```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

# 1. Create some events
print("Creating demo events...")
for i in range(5):
    event = {
        "user_id": "python_demo_user",
        "event_type": "page_view",
        "page_url": f"https://example.com/page{i}",
        "metadata": {"sequence": i, "demo": "python"}
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=event)
    if response.status_code == 201:
        print(f"  Created event: {response.json()['event_id']}")

# 2. Retrieve user events
print("\nRetrieving user events...")
response = requests.get(f"{BASE_URL}/users/python_demo_user/events/")
data = response.json()
print(f"  Total events: {data['total_events']}")

# 3. Get daily report
print("\nGetting daily report...")
today = datetime.now().strftime('%Y-%m-%d')
response = requests.get(
    f"{BASE_URL}/reports/daily/",
    params={'start_date': today, 'end_date': today}
)
report = response.json()
print(f"  Total events today: {report['total_events']}")
print(f"  Unique users today: {report['total_unique_users']}")

# 4. Analyze event types
print("\nEvent type distribution:")
for day in report['daily_stats']:
    print(f"  {day['date']}:")
    for et in day['event_types']:
        print(f"    {et['event_type']}: {et['count']}")
```

## Presentation Flow

### 1. Introduction (2 minutes)
- Show README.md overview
- Explain HBase row key design: `user_id#date#event_id`
- Explain event types: click, page_view, navigation, add_to_cart

### 2. Setup Demo (3 minutes)
```bash
# Show project structure
ls -la

# Generate demo data
python manage.py generate_demo_data --scenario default

# Start server
python manage.py runserver
```

### 3. API Demonstration (10 minutes)

**Create Event:**
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "live_demo",
    "event_type": "page_view",
    "page_url": "https://example.com/demo",
    "metadata": {"presenter": "demo", "audience": "students"}
  }'
```

**Retrieve Events:**
```bash
curl http://127.0.0.1:8000/api/users/live_demo/events/ | jq .
```

**Daily Report:**
```bash
curl http://127.0.0.1:8000/api/reports/daily/ | jq .
```

### 4. Validation Demo (5 minutes)

Show invalid requests and error handling:
```bash
# Invalid event type
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo", "event_type": "invalid"}'

# Empty user ID
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "", "event_type": "page_view"}'
```

### 5. HBase Integration (5 minutes)

**Show row key design benefits:**
```bash
# Efficient user queries
curl http://127.0.0.1:8000/api/users/demo_user_001/events/

# Efficient date range queries
curl "http://127.0.0.1:8000/api/users/demo_user_001/events/?start_date=2026-04-20&end_date=2026-04-20"

# Aggregation over HBase data
curl http://127.0.0.1:8000/api/reports/daily/
```

### 6. Q&A and Extensions (5 minutes)

Demonstrate advanced features:
- Logging: `tail -f logs/events.log`
- Health check: `python manage.py test_hbase_connection`
- Batch generation: `python manage.py generate_sample_events --users 100`

## Common Questions and Answers

**Q: Why HBase?**
A: HBase excels at:
- Fast writes for high-volume events
- Row-key based reads
- Time-oriented data access
- Horizontal scalability

**Q: Why this row key design?**
A: `user_id#date#event_id` enables:
- Fast user-specific queries (scan by user_id prefix)
- Efficient date-range queries
- Natural chronological ordering

**Q: How does aggregation work?**
A: Server-side aggregation:
- Scans events in date range
- Groups by date in memory
- Counts by event type
- Tracks unique users

**Q: What about authentication?**
A: Not included in minimal demo, but would add:
- Token-based auth
- User permissions
- API rate limiting

## Troubleshooting Demo Issues

### Issue: HBase Not Available
```bash
# Check status
python manage.py test_hbase_connection

# API still works (returns empty results)
curl http://127.0.0.1:8000/api/reports/daily/
```

### Issue: No Data
```bash
# Generate demo data
python manage.py generate_demo_data --scenario minimal

# Verify
curl http://127.0.0.1:8000/api/users/alice/events/
```

### Issue: Port Already in Use
```bash
# Use different port
python manage.py runserver 8001
```

## Post-Demo Resources

- API Documentation: See `API_EXAMPLES.md`, `USER_EVENTS_API.md`, `DAILY_REPORT_API.md`
- Setup Guide: See `SETUP.md`
- Project Status: See `PROJECT_STATUS.md`
- Epic Completion Details: See `EPIC1_COMPLETE.md` through `EPIC5_COMPLETE.md`
