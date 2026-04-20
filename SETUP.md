# Setup Guide

## Prerequisites

- Python 3.13+
- HBase (with Thrift server running on port 9090)
- pip

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` to match your HBase configuration:
- `HBASE_HOST`: HBase Thrift server host (default: localhost)
- `HBASE_PORT`: HBase Thrift server port (default: 9090)
- `HBASE_TABLE_PREFIX`: Prefix for HBase tables (default: demo_)

### 3. Set Up HBase Tables

Run the Django management command to create the required HBase table:

```bash
python manage.py setup_hbase
```

This command creates the `user_activity` table with the following structure:
- Row key format: `user_id#date#event_id`
- Column family: `cf` (contains event_type, page_url, target_id, created_at, metadata)

### 4. Run Migrations

Although we're using HBase for event storage, Django still needs its database for admin and authentication:

```bash
python manage.py migrate
```

### 5. Create a Superuser (Optional)

To access the Django admin interface:

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Testing HBase Connection

You can test the HBase connection by running:

```bash
python manage.py shell
```

Then in the Python shell:

```python
from events.hbase_client import HBaseClient

# Check if connection works
connection = HBaseClient.get_connection()
print(connection.tables())

# Check if the table exists
print(HBaseClient.table_exists('user_activity'))
```

## Troubleshooting

### HBase Connection Issues

If you get connection errors:

1. Ensure HBase is running
2. Verify the Thrift server is running:
   ```bash
   hbase thrift start
   ```
3. Check that port 9090 is accessible
4. Verify your `.env` configuration

### Import Errors

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

## Project Structure

```
User-Activity-Analitycs/
├── user_activity_analytics/     # Django project settings
│   ├── settings.py              # Main settings with HBase config
│   └── urls.py                  # Root URL configuration
├── events/                      # Events application
│   ├── hbase_client.py         # HBase connection management
│   ├── storage.py              # Event storage operations
│   ├── management/             
│   │   └── commands/
│   │       └── setup_hbase.py  # HBase table setup command
│   └── urls.py                 # API endpoints (to be implemented)
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies
└── manage.py                   # Django management script
```

## Next Steps

With Epic 1 complete, you can now proceed to:
- Epic 2: Implement the Event Collection API
- Epic 3: Enhance HBase Storage Integration
- Epic 4: Add User Activity History endpoints
- Epic 5: Build Daily Activity Reports
