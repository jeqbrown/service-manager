FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app_group && useradd -r -g app_group app_user

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p $APP_HOME/staticfiles $APP_HOME/media \
    && chown -R app_user:app_group $APP_HOME

COPY --chown=app_user:app_group . .

USER app_user

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "service_manager.wsgi:application"]
