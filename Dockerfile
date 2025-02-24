# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create and switch to non-root user
RUN useradd -m -s /bin/bash app_user
RUN chown -R app_user:app_user /app
USER app_user

# Install Python dependencies
COPY --chown=app_user:app_user requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Add local bin to PATH
ENV PATH="/home/app_user/.local/bin:${PATH}"

# Copy project
COPY --chown=app_user:app_user . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "service_manager.wsgi:application"]
