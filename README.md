# Service Manager System Overview

A streamlined service management solution built with Django that helps track service activities, customer interactions, and equipment inventory.

## Core Functionality

### Customer & Equipment Management
- Customer profile management with contact information
- Equipment/instrument tracking with serial numbers and types
- Installation date and service history tracking for each instrument

### Service Agreement Management
- Tracks active and expired service agreements
- Manages entitlements and service quotas
- Monitors agreement status and expiration dates
- Automatic status updates and expiration handling

### Work Order System
- Creation and assignment of work orders
- Status tracking (Draft, In Progress, Completed, etc.)
- Links to specific instruments and service agreements
- Assignment to technicians
- Detailed work descriptions and tracking

### Service Reporting
- Comprehensive service report creation
- Multi-stage approval workflow
- Tracks findings and actions taken
- Links reports to work orders
- Technician assignment and completion tracking

## Administrative Features

### Dashboard
- Real-time statistics and metrics
- Overview of open work orders
- Pending service reports
- Agreement status summary
- Recent activity tracking

### User Management
- Role-based access control
- Technician assignment system
- Report approval workflows
- Activity tracking by user

### Reporting & Analytics
- Service history tracking
- Equipment service patterns
- Customer interaction history
- Entitlement usage tracking
- Agreement utilization metrics

## Technical Implementation

### Interface
- Modern, responsive admin interface
- Tailwind-style CSS classes
- Feather Icons integration
- Custom status badges and visual indicators

### Data Management
- Robust data models with relationships
- Automated status updates
- Data validation and integrity checks
- Backup and maintenance tools

### Development Tools
- Database reset capabilities
- Cache management
- Development workflow support
- Backup creation utilities

## Technical Stack

- Python 3.12
- Django 5.1.5
- Modern CSS with Tailwind-style classes
- Feather Icons for UI elements

## Local Development Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create .env file:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://127.0.0.1:8000/admin to access the admin interface

## Project Structure

- `service/` - Main application directory
  - `templates/` - HTML templates
  - `static/` - CSS, JavaScript, and other static files
  - `models/` - Database models
  - `views/` - View logic
  - `admin/` - Admin interface customizations
- `service_manager/` - Project configuration
- `staticfiles/` - Collected static files

## Development Workflow

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Commit with a descriptive message
5. Push to GitHub

## License

[Your chosen license here]
</augment_code_snippet>
