import os
import django
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# Get credentials from environment variables
username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
password = os.getenv('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully")
else:
    print(f"Superuser '{username}' already exists.")
    # Update password to match .env file
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"Password updated for '{username}' to match .env configuration")
