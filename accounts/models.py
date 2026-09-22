from django.contrib.auth.models import AbstractUser
from django.db import models
from jurisdictions.models import Jurisdiction

class User(AbstractUser):
    class Role(models.TextChoices):
        MOSPI_ADMIN = 'MOSPI_ADMIN', 'MoSPI Admin'
        STATE_NODAL = 'STATE_NODAL', 'State Nodal Authority'
        MP = 'MP', 'Member of Parliament'
        DISTRICT_AUTHORITY = 'DISTRICT_AUTHORITY', 'District Authority'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    user_id = models.CharField(max_length=20, unique=True, help_text="e.g. MOSPI-001, STA-012, MP-045, DIST-008")
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.DISTRICT_AUTHORITY)
    is_nominated_mp = models.BooleanField(default=False, help_text="Nominated MP with Pan-India jurisdiction")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    jurisdiction = models.ForeignKey(
        Jurisdiction, on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )

    def save(self, *args, **kwargs):
        # Automatically assign MOSPI_ADMIN role to superusers
        if self.is_superuser and self.role != self.Role.MOSPI_ADMIN:
            self.role = self.Role.MOSPI_ADMIN
        super().save(*args, **kwargs)

    @property
    def is_mospi_admin(self):
        return self.role == self.Role.MOSPI_ADMIN or self.is_superuser

    @property
    def is_state_nodal(self):
        return self.role == self.Role.STATE_NODAL

    @property
    def is_mp(self):
        return self.role == self.Role.MP

    @property
    def is_district_authority(self):
        return self.role == self.Role.DISTRICT_AUTHORITY

    def __str__(self):
        return f"{self.user_id} - {self.get_full_name() or self.username} ({self.get_role_display()})"