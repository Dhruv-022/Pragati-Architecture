from django.db import models
from django.conf import settings

class Project(models.Model):
    class Status(models.TextChoices):
        PROPOSED = 'PROPOSED', 'Proposed'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'

    # 1. Basic Identification
    project_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)  # e.g., Roads, Healthcare, Education

    # 2. Location & Jurisdiction
    jurisdiction = models.ForeignKey(
        'jurisdictions.Jurisdiction',
        on_delete=models.CASCADE,
        related_name='projects',
        null=True,
        blank=True
    )
    location_details = models.CharField(max_length=255)  # e.g., Sanganer Ward 4

    # 3. Financial Data
    sanctioned_amount = models.DecimalField(max_digits=12, decimal_places=2)
    funds_released = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # 4. Role Assignments
    assigned_monitoring_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monitored_projects'
    )
    assigned_investigator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investigated_projects'
    )

    # 5. Project Lifecycle Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROPOSED
    )

    # 6. Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Flag indicating whether an investigation has been requested
    is_under_investigation = models.BooleanField(default=False)
    
    # Reference to the Monitoring Officer who requested the investigation
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='flagged_investigations'
    )
    
    # Optional investigation reason/notes
    investigation_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.project_id} - {self.title}"