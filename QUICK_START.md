# Quick Start Guide

## Prerequisites Check

```bash
python --version   # Should be 3.13+
pip --version      # Should be available
```

## Installation (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
The `.env` file is already configured with defaults. To customize:
```bash
# Edit .env if needed
notepad .env  # Windows
```

### Step 3: Run Django Migrations
```bash
python manage.py migrate
```

### Step 4: Verify Setup (without HBase)
```bash
python test_storage_manual.py
```

## Running the Application

### Start Development Server
```bash
python manage.py runserver
```

Access at: http://127.0.0.1:8000/

## HBase Setup (Optional - for full functionality)

### If HBase is Running:

1. **Setup HBase tables:**
   ```bash
   python manage.py setup_hbase
   ```

2. **Verify HBase connection:**
   ```bash
   python verify_setup.py
   ```

### If HBase is NOT Running:

The project structure is complete, but you'll need HBase running to:
- Store actual events
- Read event data
- Generate reports

You can still:
- Explore the code structure
- Review the API design
- Run unit tests for row key operations

## Common Commands

```bash
# Check Django configuration
python manage.py check

# Run tests
python test_storage_manual.py

# Create admin user
python manage.py createsuperuser

# Django shell
python manage.py shell
```

## Project Structure at a Glance

```
User-Activity-Analitycs/
├── events/                     # Main application
│   ├── hbase_client.py        # HBase connection layer
│   ├── storage.py             # Event storage operations
│   └── management/commands/
│       └── setup_hbase.py     # Table setup command
├── user_activity_analytics/   # Django settings
├── manage.py                  # Django CLI
├── requirements.txt           # Dependencies
└── .env                       # Configuration
```

## What's Next?

Epic 1 ✓ **COMPLETE** - Project Setup

Ready for:
- **Epic 2**: Event Collection API
- **Epic 3**: Enhanced HBase Integration
- **Epic 4**: User Activity History
- **Epic 5**: Daily Reports
- **Epic 6**: Demo Data

## Need Help?

- See [SETUP.md](SETUP.md) for detailed instructions
- See [EPIC1_COMPLETE.md](EPIC1_COMPLETE.md) for technical details
- Check Django docs: https://docs.djangoproject.com/
- Check HBase docs: https://hbase.apache.org/

## Verification Checklist

- [x] Python 3.13+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] Django migrations applied (`python manage.py migrate`)
- [x] Manual tests passing (`python test_storage_manual.py`)
- [x] Development server starts (`python manage.py runserver`)
- [ ] HBase connection verified (optional: `python verify_setup.py`)
- [ ] HBase tables created (optional: `python manage.py setup_hbase`)
