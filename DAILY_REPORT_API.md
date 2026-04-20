# Daily Activity Report API Documentation

## Endpoint

`GET /api/reports/daily/`

Generate aggregated daily activity reports showing event counts by date and type.

## Base URL

```
http://127.0.0.1:8000/api/reports/daily/
```

## Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `start_date` | string | No | Start date for filtering (YYYY-MM-DD format, inclusive) | `2026-04-01` |
| `end_date` | string | No | End date for filtering (YYYY-MM-DD format, inclusive) | `2026-04-30` |

## Request Examples

### 1. Get All Daily Activity

```bash
curl http://127.0.0.1:8000/api/reports/daily/
```

### 2. Get Activity for Specific Date Range

```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-01&end_date=2026-04-30"
```

### 3. Get Activity for a Single Day

```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-20&end_date=2026-04-20"
```

### 4. Get Current Week Activity

```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-14&end_date=2026-04-20"
```

## Response Format

### Success Response (200 OK)

```json
{
  "report_type": "daily",
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "total_days": 30,
  "total_events": 1523,
  "total_unique_users": 45,
  "daily_stats": [
    {
      "date": "2026-04-01",
      "total_events": 52,
      "unique_users": 12,
      "event_types": [
        {
          "event_type": "page_view",
          "count": 28
        },
        {
          "event_type": "click",
          "count": 15
        },
        {
          "event_type": "add_to_cart",
          "count": 7
        },
        {
          "event_type": "navigation",
          "count": 2
        }
      ]
    },
    {
      "date": "2026-04-02",
      "total_events": 48,
      "unique_users": 10,
      "event_types": [
        {
          "event_type": "page_view",
          "count": 25
        },
        {
          "event_type": "click",
          "count": 18
        },
        {
          "event_type": "add_to_cart",
          "count": 5
        }
      ]
    }
  ]
}
```

### Empty Results (200 OK)

```json
{
  "report_type": "daily",
  "start_date": null,
  "end_date": null,
  "total_days": 0,
  "total_events": 0,
  "total_unique_users": 0,
  "daily_stats": []
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
  "error": "Failed to generate report",
  "message": "An error occurred while generating the report"
}
```

## Response Fields

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `report_type` | string | Type of report (always "daily") |
| `start_date` | string or null | Start date filter applied (if any) |
| `end_date` | string or null | End date filter applied (if any) |
| `total_days` | integer | Number of days in the report |
| `total_events` | integer | Total events across all days |
| `total_unique_users` | integer | Total unique users across all days |
| `daily_stats` | array | Array of daily statistics objects |

### Daily Stats Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date in YYYY-MM-DD format |
| `total_events` | integer | Total events for this date |
| `unique_users` | integer | Number of unique users for this date |
| `event_types` | array | Array of event type statistics |

### Event Type Stats Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | Type of event (click, page_view, navigation, add_to_cart) |
| `count` | integer | Number of events of this type |

## PowerShell Examples (Windows)

### Get All Daily Reports
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/reports/daily/" -Method Get
```

### Get Reports with Date Range
```powershell
$params = @{
    start_date = "2026-04-01"
    end_date = "2026-04-30"
}
$query = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/reports/daily/?$query" -Method Get
```

## Python Examples

### Using requests library

```python
import requests

# Get daily report
response = requests.get("http://127.0.0.1:8000/api/reports/daily/")
data = response.json()

print(f"Report Type: {data['report_type']}")
print(f"Total Days: {data['total_days']}")
print(f"Total Events: {data['total_events']}")
print(f"Total Unique Users: {data['total_unique_users']}")

print("\nDaily Breakdown:")
for day in data['daily_stats']:
    print(f"\n{day['date']}:")
    print(f"  Total Events: {day['total_events']}")
    print(f"  Unique Users: {day['unique_users']}")
    print(f"  Event Types:")
    for et in day['event_types']:
        print(f"    {et['event_type']}: {et['count']}")
```

### With Date Filtering

```python
import requests

params = {
    'start_date': '2026-04-01',
    'end_date': '2026-04-30'
}

response = requests.get(
    "http://127.0.0.1:8000/api/reports/daily/",
    params=params
)

data = response.json()
print(f"Report from {data['start_date']} to {data['end_date']}")
print(f"Total events in period: {data['total_events']}")
```

### Analyze Event Distribution

```python
import requests
from collections import defaultdict

response = requests.get("http://127.0.0.1:8000/api/reports/daily/")
data = response.json()

# Aggregate event types across all days
total_by_type = defaultdict(int)
for day in data['daily_stats']:
    for et in day['event_types']:
        total_by_type[et['event_type']] += et['count']

print("Event Distribution:")
for event_type, count in sorted(total_by_type.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / data['total_events'] * 100) if data['total_events'] > 0 else 0
    print(f"  {event_type}: {count} ({percentage:.1f}%)")
```

### Generate CSV Report

```python
import requests
import csv

response = requests.get(
    "http://127.0.0.1:8000/api/reports/daily/",
    params={'start_date': '2026-04-01', 'end_date': '2026-04-30'}
)
data = response.json()

with open('daily_report.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date', 'Total Events', 'Unique Users', 'Page Views', 'Clicks', 'Navigation', 'Add to Cart'])
    
    for day in data['daily_stats']:
        event_counts = {et['event_type']: et['count'] for et in day['event_types']}
        writer.writerow([
            day['date'],
            day['total_events'],
            day['unique_users'],
            event_counts.get('page_view', 0),
            event_counts.get('click', 0),
            event_counts.get('navigation', 0),
            event_counts.get('add_to_cart', 0)
        ])

print("Report saved to daily_report.csv")
```

## JavaScript/Fetch Example

```javascript
// Get daily report
async function getDailyReport(startDate = null, endDate = null) {
    const params = new URLSearchParams();
    
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const url = `http://127.0.0.1:8000/api/reports/daily/?${params}`;
    
    const response = await fetch(url);
    const data = await response.json();
    
    return data;
}

// Usage
getDailyReport('2026-04-01', '2026-04-30')
    .then(data => {
        console.log(`Total events: ${data.total_events}`);
        console.log(`Total users: ${data.total_unique_users}`);
        
        data.daily_stats.forEach(day => {
            console.log(`\n${day.date}:`);
            day.event_types.forEach(et => {
                console.log(`  ${et.event_type}: ${et.count}`);
            });
        });
    });
```

### Chart.js Visualization

```javascript
async function createDailyChart() {
    const data = await getDailyReport('2026-04-01', '2026-04-30');
    
    const dates = data.daily_stats.map(d => d.date);
    const totals = data.daily_stats.map(d => d.total_events);
    
    const ctx = document.getElementById('dailyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Daily Events',
                data: totals,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
```

## Use Cases

### 1. Activity Overview Dashboard

Get overall activity metrics for a dashboard:

```bash
curl "http://127.0.0.1:8000/api/reports/daily/"
```

### 2. Weekly Report

Generate a weekly activity report:

```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-14&end_date=2026-04-20"
```

### 3. Monthly Summary

Analyze activity for the entire month:

```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-01&end_date=2026-04-30"
```

### 4. Campaign Analysis

Compare activity before and during a campaign:

```bash
# Before campaign
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-01&end_date=2026-04-14"

# During campaign
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-15&end_date=2026-04-21"
```

### 5. Trend Analysis

Get data for trend analysis:

```bash
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-03-01&end_date=2026-04-30"
```

## Aggregation Details

### How Aggregation Works

The endpoint performs server-side aggregation over HBase data:

1. **Scans events** within the specified date range
2. **Groups by date** using the row key structure (`user_id#date#event_id`)
3. **Counts events** by event type for each date
4. **Tracks unique users** per date
5. **Returns sorted results** by date

### Performance Characteristics

- **Efficient Scanning**: Uses HBase row key design for efficient date range scans
- **In-Memory Aggregation**: Aggregates results in memory for fast processing
- **Scalability**: Performance depends on date range size and event volume

### Optimization Tips

1. **Use date ranges** to limit the amount of data scanned
2. **Request smaller time windows** for faster responses
3. **Cache reports** for frequently accessed date ranges
4. **Schedule report generation** for off-peak hours for large datasets

## Data Freshness

- Reports reflect real-time data from HBase
- No caching (always returns current data)
- New events appear immediately in reports

## Testing

### Test with Sample Data

```bash
# 1. Generate sample events
python manage.py generate_sample_events --users 10 --events-per-user 50 --days 30

# 2. Get daily report
curl "http://127.0.0.1:8000/api/reports/daily/"

# 3. Get report for specific range
curl "http://127.0.0.1:8000/api/reports/daily/?start_date=2026-04-01&end_date=2026-04-07"
```

### Run Automated Tests

```bash
python test_daily_report_api.py
```

## Integration Examples

### Dashboard Widget

```javascript
class DailyReportWidget {
    async load(startDate, endDate) {
        const data = await getDailyReport(startDate, endDate);
        
        document.getElementById('total-events').textContent = data.total_events;
        document.getElementById('total-users').textContent = data.total_unique_users;
        document.getElementById('total-days').textContent = data.total_days;
        
        this.renderChart(data.daily_stats);
    }
    
    renderChart(dailyStats) {
        // Chart rendering logic
    }
}
```

### Email Report Generator

```python
import requests
from datetime import datetime, timedelta

def generate_email_report():
    """Generate HTML email report for the past week"""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = requests.get(
        "http://127.0.0.1:8000/api/reports/daily/",
        params={'start_date': start_date, 'end_date': end_date}
    )
    
    data = response.json()
    
    html = f"""
    <h2>Weekly Activity Report</h2>
    <p>Period: {data['start_date']} to {data['end_date']}</p>
    <p>Total Events: {data['total_events']}</p>
    <p>Total Users: {data['total_unique_users']}</p>
    
    <table>
        <tr>
            <th>Date</th>
            <th>Events</th>
            <th>Users</th>
        </tr>
    """
    
    for day in data['daily_stats']:
        html += f"""
        <tr>
            <td>{day['date']}</td>
            <td>{day['total_events']}</td>
            <td>{day['unique_users']}</td>
        </tr>
        """
    
    html += "</table>"
    
    return html
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Report generated (may be empty) |
| 400 | Bad Request - Invalid parameters |
| 500 | Internal Server Error - Report generation failed |

## Notes

- Empty results return 200 with zero values
- Missing query parameters default to no filtering (all data)
- All dates are in UTC
- Daily stats are sorted chronologically
- The endpoint works even if HBase is unavailable (returns empty results)
