# Service Manager

"Ordo ab Chao" - Order from Chaos. Service Manager transforms the typically chaotic world of service operations into a streamlined, systematic process. Born from the recognition that service organizations often struggle with scattered paperwork, disconnected processes, and ad-hoc tracking methods, this application brings structure and clarity to every aspect of service management.

## Features

- Equipment Inventory Management
  - Track instruments and their service history
  - Monitor instrument status and location
  - Manage instrument types and configurations

- Service Operations
  - Work order management
  - Service report generation
  - Maintenance scheduling
  - Service agreement tracking

- Customer Management
  - Customer profile management
  - Service history tracking
  - Equipment inventory per customer
  - Entitlement tracking

- Modern Admin Interface
  - Intuitive dashboard
  - Real-time status updates
  - Comprehensive search capabilities
  - Role-based access control

## Technical Stack

### Backend
- Python 3.12
- Django 5.1.5
- Django REST Framework
- PostgreSQL 15

### Frontend
- React 19.0.0
- TypeScript
- Custom Tailwind-style CSS
- Feather Icons

### Infrastructure
- Docker
- Nginx
- GitHub Actions (CI/CD)

## Development Setup

1. Clone the repository:
```bash
git clone git@github.com:jeqbrown/service-manager.git
cd service-manager
```

2. Environment Setup:
```bash
# Create .env file with required variables
cp .env.example .env
# Edit .env with your settings
```

3. Start the Development Environment:
```bash
# Start all services
docker-compose up -d

# Create database migrations
docker-compose exec web python manage.py migrate

# Create a superuser
docker-compose exec web python manage.py createsuperuser
```

4. Frontend Development:
```bash
cd frontend
npm install
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin Interface: http://localhost:8000/admin/

## Project Structure

```
Service_Manager/
├── service/                 # Main Django application
│   ├── models/             # Database models
│   ├── admin/             # Admin interface customizations
│   ├── api/               # REST API endpoints
│   └── tests/             # Backend tests
├── frontend/              # React frontend application
├── scripts/               # Utility scripts
├── docs/                  # Project documentation
└── docker/                # Docker configuration files
```

## Documentation

- Full documentation: `docs/SMProjectDocs.md`
- Project plan and status: `docs/PROJECT_PLAN.md`
- API documentation: Available at `/api/docs/` when running

## Testing

### Backend Tests:
```bash
docker-compose exec web python manage.py test
```

### Frontend Tests:
```bash
cd frontend
npm test
```

## Deployment

Deployment scripts are provided for various scenarios:

```bash
# Deploy to GitHub
./scripts/deploy_changes.sh

# Update existing deployment
./scripts/update_droplet.sh

# Set up new environment
./scripts/configurable_setup_droplet.sh
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

[License details here]

## Contact

[Contact information here]
