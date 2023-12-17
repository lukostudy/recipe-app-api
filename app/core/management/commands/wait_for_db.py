"""
Django command to wait for db to be available
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command: wait for the database"""

    def handle(self, *args, **options):
        """Entrypoint for the command"""
        self.stdout.write('Waiting for the database...')
        db_up = False
        wait = 0
        max_wait = 10  # seconds
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                wait += 1 if wait < max_wait else 0
                self.stdout.write(f"DB unavailable, waiting {wait} sec ...")
                time.sleep(wait)
        self.stdout.write(self.style.SUCCESS('Database available!'))
