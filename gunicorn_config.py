bind = "unix:/run/gunicorn.sock"
workers = 3
wsgi_app = "service_manager.wsgi:application"
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
capture_output = True