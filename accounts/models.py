from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from jurisdictions.models import Jurisdiction

class User(AbstractUser):
    class Role(models.TextChoices):
        SYSTEM_ADMIN = 'SYSTEM_ADMIN', 'System Administrator'
        DISTRICT_ADMIN = 'DISTRICT_ADMIN', 'District Administrator'
        MONITORING_OFFICER = 'MONITORING_OFFICER', 'Monitoring Officer'
        INVESTIGATOR = 'INVESTIGATOR', 'Investigator'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    user_id = models.CharField(max_length=20, unique=True, help_text="e.g. ADM-001, OFF-021, INV-008")
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.MONITORING_OFFICER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    jurisdiction = models.ForeignKey(
        Jurisdiction, on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )

    def save(self, *args, **kwargs):
        # Automatically assign SYSTEM_ADMIN role to superusers
        if self.is_superuser and self.role != self.Role.SYSTEM_ADMIN:
            self.role = self.Role.SYSTEM_ADMIN
        super().save(*args, **kwargs)

    @property
    def is_system_admin(self):
        return self.role == self.Role.SYSTEM_ADMIN or self.is_superuser

    @property
    def is_district_admin(self):
        return self.role == self.Role.DISTRICT_ADMIN

    def __str__(self):
        return f"{self.user_id} - {self.get_full_name() or self.username} ({self.get_role_display()})"