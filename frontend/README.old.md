# Service Manager Frontend

This directory contains the React frontend for the Service Manager application.

## Project Structure

We've adopted a "frontend" directory approach where:

- All React code lives in this directory
- Django serves the React build as static files
- API endpoints are consumed by the React application

## Development Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Build for production:
```bash
npm run build
```