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

        # Base Queryset: Only permit Districts or relevant levels from the database
        self.fields['jurisdiction'].queryset = Jurisdiction.objects.all().order_by('name')

        if current_user:
            # 1. MoSPI Admin Flow (Apex National Oversight)
            if current_user.is_mospi_admin:
                self.fields['role'].choices = User.Role.choices
                self.fields['jurisdiction'].empty_label = "-- Select Jurisdiction (Optional for National) --"

            # 2. State Nodal Authority Flow
            elif current_user.is_state_nodal:
                allowed_roles = [User.Role.MP, User.Role.DISTRICT_AUTHORITY]
                self.fields['role'].choices = [
                    (k, v) for k, v in User.Role.choices if k in allowed_roles
                ]
                # Can scope jurisdictions within their state if needed

            # 3. District Authority Flow
            elif current_user.is_district_authority:
                allowed_roles = [User.Role.DISTRICT_AUTHORITY]
                self.fields['role'].choices = [
                    (k, v) for k, v in User.Role.choices if k in allowed_roles
                ]
                if current_user.jurisdiction:
                    self.fields['jurisdiction'].initial = current_user.jurisdiction
                    self.fields['jurisdiction'].disabled = True
                    self.fields['jurisdiction'].required = True

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        jurisdiction = cleaned_data.get('jurisdiction')

        # Rule validation: District Authorities and MPs generally require a jurisdiction
        if role in [User.Role.DISTRICT_AUTHORITY, User.Role.MP] and not jurisdiction:
            if self.fields['jurisdiction'].disabled and self.fields['jurisdiction'].initial:
                cleaned_data['jurisdiction'] = self.fields['jurisdiction'].initial
            else:
                self.add_error('jurisdiction', 'A valid Jurisdiction must be assigned for this role.')

        return cleaned_data