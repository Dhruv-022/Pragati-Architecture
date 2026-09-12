from django.db import models

class Jurisdiction(models.Model):
    class Level(models.TextChoices):
        STATE = 'STATE', 'State'
        DISTRICT = 'DISTRICT', 'District'

    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.DISTRICT)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_jurisdictions'
    )

    def __str__(self):
        return f"{self.name} ({self.level})"