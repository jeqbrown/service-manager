# Service Manager

A streamlined service management solution built with Django that helps track service activities, customer interactions, and equipment inventory.

## Features

- Service Reports Management
- Customer Interaction Tracking
- Equipment Inventory Management
- Admin Portal for System Management
- Modern, Responsive Interface

## Technical Stack

- Python 3.12
- Django 5.1.5
- Modern CSS with Tailwind-style classes
- Feather Icons for UI elements

## Project Setup

1. Create and activate a virtual environment:
```python
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

2. Install dependencies:
```python
pip install django
```

3. Run migrations:
```python
python manage.py migrate
```

4. Start the development server:
```python
python manage.py runserver
```

## Project Structure

- `service/` - Main application directory
  - `templates/` - HTML templates
  - `static/` - CSS, JavaScript, and other static files
- `staticfiles/` - Collected static files for production

## Development

This project is under version control using Git. To make changes:

1. Create a new branch for your feature
2. Make your changes
3. Commit with a descriptive message
4. Merge back into the main branch

## License

[Your chosen license here]