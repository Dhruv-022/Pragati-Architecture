from django.db import migrations

def seed_jurisdictions(apps, schema_editor):
    Jurisdiction = apps.get_model('jurisdictions', 'Jurisdiction')

    # Structure: State -> List of Districts
    dataset = {
        'Rajasthan': ['Jaipur', 'Jodhpur', 'Kota', 'Udaipur', 'Ajmer', 'Bikaner'],
        'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
        'Maharashtra': ['Mumbai Suburban', 'Pune', 'Nagpur', 'Nashik'],
    }

    for state_name, districts in dataset.items():
        state_obj, _ = Jurisdiction.objects.get_or_create(
            name=state_name,
            level='STATE'
        )
        for dist_name in districts:
            Jurisdiction.objects.get_or_create(
                name=dist_name,
                level='DISTRICT',
                parent=state_obj
            )

def reverse_seed(apps, schema_editor):
    Jurisdiction = apps.get_model('jurisdictions', 'Jurisdiction')
    Jurisdiction.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('jurisdictions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_jurisdictions, reverse_seed),
    ]