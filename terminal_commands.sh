# Stop all containers and remove orphaned ones
docker-compose down --remove-orphans

# Remove all volumes
docker volume prune -f

# Remove any existing containers with the same names
docker rm -f service_manager_db_1 service_manager_web_1 service_manager_nginx_1