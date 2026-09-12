from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from jurisdictions.models import Jurisdiction

class DynamicUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'user_id', 'first_name', 'last_name', 'email', 'role', 'jurisdiction', 'status')

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('logged_in_user', None)
        super().__init__(*args, **kwargs)

        # Base Queryset: Only permit assigned Districts from the database
        self.fields['jurisdiction'].queryset = Jurisdiction.objects.filter(
            level=Jurisdiction.Level.DISTRICT
        ).select_related('parent').order_by('parent__name', 'name')

        if current_user:
            # 1. District Admin Flow
            if current_user.is_district_admin:
                # Restrict selectable roles
                allowed_roles = [User.Role.MONITORING_OFFICER, User.Role.INVESTIGATOR]
                self.fields['role'].choices = [
                    (k, v) for k, v in User.Role.choices if k in allowed_roles
                ]

                # Lock and enforce the District Admin's jurisdiction
                if current_user.jurisdiction:
                    self.fields['jurisdiction'].initial = current_user.jurisdiction
                    self.fields['jurisdiction'].disabled = True
                    self.fields['jurisdiction'].required = True

            # 2. System Admin Flow
            elif current_user.is_system_admin:
                self.fields['role'].choices = User.Role.choices
                self.fields['jurisdiction'].empty_label = "-- Select District Jurisdiction --"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        jurisdiction = cleaned_data.get('jurisdiction')

        # Rule validation: Any role other than SYSTEM_ADMIN MUST have a jurisdiction selected
        if role and role != User.Role.SYSTEM_ADMIN and not jurisdiction:
            # If disabled field was ignored by browser or not bound, check initial value
            if self.fields['jurisdiction'].disabled and self.fields['jurisdiction'].initial:
                cleaned_data['jurisdiction'] = self.fields['jurisdiction'].initial
            else:
                self.add_error('jurisdiction', 'A valid District Jurisdiction must be assigned for this role.')

        return cleaned_data