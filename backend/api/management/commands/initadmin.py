from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Creates a superuser from environment variables'

    def handle(self, *args, **options):
        load_dotenv()
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('ADMIN_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING("ADMIN_PASSWORD not found in .env. Skipping admin creation."))
            return

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = email
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists. Password and email updated from .env."))
