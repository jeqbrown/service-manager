from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Resets the database for development'

    def handle(self, *args, **kwargs):
        self.stdout.write('Resetting database...')
        
        # Close the database connection
        connection.close()
        
        # Remove the database file
        db_path = 'db.sqlite3'
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write('Removed existing database')
        
        # Run migrations
        call_command('migrate')
        self.stdout.write('Applied migrations')
        
        # Create superuser
        self.stdout.write('Creating superuser...')
        call_command('createsuperuser')
        
        self.stdout.write(self.style.SUCCESS('Database reset complete!'))