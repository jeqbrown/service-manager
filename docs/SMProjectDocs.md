# Service Manager Project Documentation

## Project Overview

Service Manager is a comprehensive application designed to streamline service operations, transforming chaotic service management into a structured, systematic process. The application handles service reports, customer interactions, equipment inventory, and more through a modern, responsive interface.

## Technical Stack

- **Backend**: Python 3.12, Django 5.1.5
- **Frontend**: React 19.0.0 with TypeScript
- **CSS Framework**: Custom Tailwind-style classes
- **Database**: PostgreSQL 15
- **Deployment**: Docker, Nginx
- **Icons**: Feather Icons

## Project Structure

```
Service_Manager/
├── service/                      # Main Django application
│   ├── admin/                    # Admin customizations
│   │   ├── __init__.py
│   │   ├── customer_admin.py
│   │   ├── instrument_admin.py
│   │   ├── agreement_admin.py
│   │   ├── workorder_admin.py
│   │   ├── servicereport_admin.py
│   │   └── site.py
...
│   │       └── dist/
│   │           └── styles.css
│   └── package.json
├── service_manager/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scripts/                      # Utility scripts
│   ├── setup_react.sh
│   ├── deploy_changes.sh
│   ├── update_droplet.sh
│   └── configurable_setup_droplet.sh
├── staticfiles/                  # Collected static files
├── media/                        # User-uploaded files
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── nginx.dev.conf                # Nginx configuration for development
└── .env                          # Environment variables
```

## Core Components and Interdependencies

### Backend (Django)

#### Models

1. **Customer** (`service/models/customer.py`)
   - Core entity representing service clients
   - Related to: ServiceAgreement, WorkOrder
   - Tracking fields:
     - created_by: User who created the record
     - updated_by: User who last modified the record
     - created_at: Timestamp of creation
     - updated_at: Timestamp of last update

2. **Instrument** (`service/models/instrument.py`)
   - Equipment being serviced
   - Related to: InstrumentType, WorkOrder

3. **ServiceAgreement** (`service/models/agreement.py`)
   - Contracts between customers and service provider
   - Related to: Customer, Entitlement
   - Features automatic status updates based on dates

4. **WorkOrder** (`service/models/workorder.py`)
   - Service requests
   - Related to: Customer, Instrument, Entitlement, ServiceReport
   - Improved relationship with ServiceReport for better tracking

5. **ServiceReport** (`service/models/servicereport.py`)
   - Documentation of completed service work
   - Related to: WorkOrder, User

#### Data Tracking

All major models now include tracking fields for improved audit capabilities:
- Creation tracking (created_by, created_at)
- Update tracking (updated_by, updated_at)
- Automatic timestamp management
- User association for all changes

#### API Serializers

Serializers have been enhanced to:
- Automatically handle tracking fields
- Maintain audit trail for all changes
- Include user context in nested operations
- Provide read-only access to tracking information

#### Admin Interface

Custom admin interfaces for each model are defined in the `service/admin/` directory, with the main admin site configuration in `site.py`. Notable features include:
- Custom status badges for visual status indication
- Bulk update capabilities for service agreements
- Integrated management commands for maintenance tasks

### Frontend (React)

#### Key Components

1. **Dashboard** (`frontend/src/pages/Dashboard.tsx`)
   - Main dashboard interface displaying service operations overview
   - Features:
     - Real-time statistics display
     - Recent work orders list with status indicators
     - Upcoming services schedule
     - Date range filtering
     - Refresh capability
     - Responsive layout with grid system
   - State Management:
     - Local state for dashboard data
     - Loading and error states
     - Date range filter state
   - Testing:
     - Comprehensive test suite in `Dashboard.test.tsx`
     - Coverage includes loading states, data display, error handling, and user interactions

2. **Components** (`frontend/src/components/`)
   - Reusable UI elements
   - Layout components (Sidebar, Header, etc.)

#### Testing Strategy

1. **Component Testing**
   - Using React Testing Library
   - Mock API responses with axios-mock-adapter
   - Test coverage includes:
     - Initial rendering
     - Loading states
     - Error handling
     - User interactions
     - Data filtering
     - Navigation

2. **Integration Testing**
   - API integration tests
   - Route protection tests
   - Authentication flow tests

#### Data Flow

1. Dashboard Component:
   - Fetches data from `/dashboard` endpoint
   - Updates based on date range filters
   - Handles loading and error states
   - Manages navigation to detail views

### Styling

The project uses a custom Tailwind-style CSS approach:

1. **Theme Package** (`theme/`)
   - Contains Tailwind configuration
   - Source styles in `static_src/src/styles.css`
   - Compiled output in `static/css/dist/styles.css`

### Infrastructure

1. **Docker**
   - `Dockerfile`: Defines the application container with multi-stage build
   - `docker-compose.yml`: Orchestrates services (web, db, nginx)
   - Security hardened with non-root user

2. **Nginx**
   - Serves static files
   - Proxies requests to the Django application

3. **Deployment Scripts**
   - `deploy_changes.sh`: Manages GitHub deployments
   - `update_droplet.sh`: Updates existing deployments
   - `configurable_setup_droplet.sh`: Configurable initial setup

## Data Flow

1. User interacts with React frontend
2. Frontend makes API calls to Django backend
3. Django processes requests, interacts with database
4. Results are returned to frontend for display

## Authentication and Authorization

- Django's built-in authentication system
- Custom user groups for role-based access control
- JWT or session-based authentication for API requests

## Development Workflow

1. Backend changes:
   - Modify Django models, views, or admin
   - Run migrations if needed
   - Test with Django development server

2. Frontend changes:
   - Modify React components
   - Test with React development server
   - Build for production when ready

3. Deployment:
   - Use `deploy_changes.sh` to package and deploy changes to GitHub
   - Use `update_droplet.sh` for quick updates to production
   - Use `configurable_setup_droplet.sh` for new environment setup

## API Endpoints

The application exposes RESTful API endpoints for:

- Customers
- Instruments
- Service Agreements
- Work Orders
- Service Reports

Each endpoint supports standard CRUD operations with appropriate permissions.

## Configuration

Key configuration files:

1. `service_manager/settings.py`: Django settings
2. `.env`: Environment variables
3. `docker-compose.yml`: Service configuration
4. `nginx.dev.conf`: Web server configuration

## Dependencies

### Backend Dependencies

- Django: Web framework
- Django REST Framework: API toolkit
- django-cors-headers: CORS support
- whitenoise: Static file serving
- psycopg2-binary: PostgreSQL adapter
- python-dotenv: Environment variable management

### Frontend Dependencies

- React: UI library
- React Router: Navigation
- Axios: HTTP client
- TypeScript: Type checking
- Headless UI: Unstyled UI components
- Heroicons: SVG icons

## Deployment

The application is containerized with Docker and can be deployed to:

- DigitalOcean Droplets (using the provided setup script)
- Any Docker-compatible hosting platform

The deployment process is streamlined with:
- `deploy_changes.sh` for GitHub deployments
- `update_droplet.sh` for quick updates
- `configurable_setup_droplet.sh` for new environments

## Testing

### Backend Testing
- Django test suite for models and views
- Coverage reports generated with pytest-cov
- API endpoint testing with DRF test utilities

### Frontend Testing
- React Testing Library for component tests
- Jest for unit testing
- End-to-end testing with Cypress (planned)

## Troubleshooting

Common issues:

1. CORS errors: Check CORS configuration in settings.py
2. Static files not loading: Verify whitenoise configuration and collectstatic
3. Database connection issues: Check environment variables and PostgreSQL configuration
4. React test failures: Ensure proper mocking of context providers and router

## Future Enhancements

Planned enhancements in progress:
1. Complete REST API implementation
2. Modern React frontend with TypeScript (completed)
3. Comprehensive testing suite (in progress)
4. CI/CD pipeline for automated deployment

Potential future areas for expansion:
1. Mobile application integration
2. Advanced reporting and analytics
3. Customer portal for self-service
4. Integration with third-party services (payment processors, CRM systems)

## Current Status

The backend infrastructure and model relationships have been optimized. Deployment scripts are in place for various scenarios. The next phase focuses on API development and frontend implementation.

## Testing Documentation

### Customer API Tests (`service/tests/test_api/test_customer.py`)

The Customer API test suite verifies the functionality, permissions, and validation rules for customer-related operations.

#### Test Coverage

1. **Authentication & Permissions**
   - Staff users can create, update, and delete customers
   - Regular users can only list and view customers
   - Unauthenticated users have no access
   - Admin users have full access

2. **CRUD Operations**
   - Create customer with nested contacts
   - List customers with pagination
   - Update customer details and contacts
   - Delete customer and associated contacts

3. **Validation Rules**
   - Email format validation for contacts
   - Single primary contact enforcement
   - Required fields validation
   - Proper error responses for invalid data

#### Test Cases Overview

| Test Method | Description | Expected Outcome |
|------------|-------------|------------------|
| `test_create_customer_staff` | Staff user creates customer with contact | Status 201, Customer created |
| `test_create_customer_regular_user` | Regular user attempts creation | Status 403, Forbidden |
| `test_list_customers_authenticated` | Authenticated user lists customers | Status 200, Customer list |
| `test_list_customers_unauthenticated` | Unauthenticated access attempt | Status 401, Unauthorized |
| `test_update_customer_staff` | Staff user updates customer | Status 200, Customer updated |
| `test_update_customer_regular_user` | Regular user attempts update | Status 403, Forbidden |
| `test_delete_customer_staff` | Staff user deletes customer | Status 204, Customer deleted |
| `test_delete_customer_regular_user` | Regular user attempts deletion | Status 403, Forbidden |
| `test_contact_validation` | Validate contact data rules | Status 400 for invalid data |
| `test_multiple_primary_contacts` | Test primary contact constraints | Status 400 for multiple primary |

#### Running the Tests

```bash
# Run all customer API tests
python manage.py test service.tests.test_api.test_customer

# Run specific test case
python manage.py test service.tests.test_api.test_customer.CustomerAPITests.test_create_customer_staff
```

#### Test Dependencies

- Django REST Framework
- Django Test Client
- Customer and Contact models
- User authentication

#### Coverage Report

Current test coverage for the Customer API:
- Lines: 95%
- Branches: 90%
- Functions: 100%
