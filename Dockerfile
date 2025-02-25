# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

# Create and set working directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r app_group && useradd -r -g app_group app_user

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p $APP_HOME/staticfiles $APP_HOME/media \
    && chown -R app_user:app_group $APP_HOME

# Switch to non-root user
USER app_user

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "service_manager.wsgi:application"]
