import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

# List of real accounts you want to preserve
KEPT_USERNAMES = ['haabu', 'haabu2', 'dhruv9321']

# Delete all users EXCEPT your preserved list
deleted_count, _ = User.objects.exclude(username__in=KEPT_USERNAMES).delete()

print(f"🧹 Successfully cleaned up {deleted_count} seeded user accounts!")
print(f"Remaining active accounts: {list(User.objects.values_list('username', flat=True))}")
