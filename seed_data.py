import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from jurisdictions.models import Jurisdiction
from projects.models import Project
from accounts.models import User

def seed_projects_only():
    print("🧹 Cleaning old project records...")
    Project.objects.all().delete()

    print("📍 Fetching existing Jurisdictions...")
    jurisdictions = list(Jurisdiction.objects.all())
    
    if not jurisdictions:
        print("❌ Error: No Jurisdictions found in the database. Please populate jurisdictions first.")
        return

    print(f"✅ Found {len(jurisdictions)} jurisdictions in the database.")

    # Grab existing officers if present
    monitoring_officers = list(User.objects.filter(role=User.Role.MONITORING_OFFICER))
    investigators = list(User.objects.filter(role=User.Role.INVESTIGATOR))

    print("📦 Provisioning 500 Projects across all jurisdictions...")
    categories = ['Roads & Transport', 'Healthcare Facilities', 'Water Supply', 'Sanitation & Waste', 'Education Infrastructure', 'Solar & Energy', 'Public Parks']
    statuses = [Project.Status.PROPOSED, Project.Status.IN_PROGRESS, Project.Status.COMPLETED]
    reasons = [
        "Unexplained budget delay beyond milestone phase.",
        "Quality mismatch reported during field inspection.",
        "Discrepancy between funds released and physical progress.",
        "Contractor compliance audit requested by district board.",
        "Citizen complaint regarding material grade."
    ]

    projects_to_create = []

    for i in range(1, 501):
        # Pick a random jurisdiction for each project
        j = random.choice(jurisdictions)
        
        # Dynamically create an identifier prefix from the jurisdiction name
        clean_name = j.name.replace(" ", "").upper()
        code_prefix = clean_name[:3] if len(clean_name) >= 3 else clean_name.ljust(3, 'X')
        
        p_id = f"{code_prefix}-2026-{i:04d}"
        cat = random.choice(categories)
        sanctioned = random.randint(1000000, 10000000)
        status = random.choice(statuses)
        released = sanctioned * 0.5 if status == Project.Status.IN_PROGRESS else (sanctioned if status == Project.Status.COMPLETED else 0)

        # Match officers specific to the picked jurisdiction if available
        j_monitors = [m for m in monitoring_officers if m.jurisdiction == j]
        j_investigators = [inv for inv in investigators if inv.jurisdiction == j]

        assigned_mo = random.choice(j_monitors) if j_monitors else None
        should_investigate = random.random() < 0.20  # ~20% audit rate
        flagged_by_officer = assigned_mo if should_investigate else None
        assigned_inv = random.choice(j_investigators) if (should_investigate and j_investigators) else None
        reason = random.choice(reasons) if should_investigate else None

        project = Project(
            project_id=p_id,
            title=f"{cat} Project - Ward {random.randint(1, 30)} ({j.name})",
            category=cat,
            jurisdiction=j,
            location_details=f"{j.name} Sector {random.randint(1, 15)}",
            sanctioned_amount=sanctioned,
            funds_released=released,
            assigned_monitoring_officer=assigned_mo,
            assigned_investigator=assigned_inv,
            status=status,
            is_under_investigation=should_investigate,
            flagged_by=flagged_by_officer,
            investigation_reason=reason
        )
        projects_to_create.append(project)

    # Use bulk_create for super fast database insertion
    Project.objects.bulk_create(projects_to_create)

    print("✅ 500 Projects successfully populated across all jurisdictions!")

if __name__ == '__main__':
    seed_projects_only()