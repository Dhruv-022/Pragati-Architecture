# projects/models.py
from django.db import models

class Project(models.Model):
    sr_no = models.TextField(primary_key=True, db_column='sr_no')
    work_category = models.TextField(blank=True, null=True)
    work = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True, db_index=True)
    ida = models.TextField(blank=True, null=True)
    hon_ble_members_of_parliament = models.TextField(
        db_column="hon'ble_members_of_parliament", 
        blank=True, 
        null=True
    )
    constituency = models.TextField(blank=True, null=True, db_index=True)
    work_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'WORKS_RECOMMENDED'

    def __str__(self):
        return f"{self.work or self.work_description or 'Project'} ({self.constituency}, {self.state})"