from django.db import models

class Jurisdiction(models.Model):
    class Type(models.TextChoices):
        STATE = 'STATE', 'State / UT'
        DISTRICT = 'DISTRICT', 'District'
        
    name = models.CharField(max_length=255)
    jurisdiction_type = models.CharField(max_length=50, choices=Type.choices, blank=True, null=True, default='DISTRICT')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='sub_jurisdictions')

    def __str__(self):
        return self.name