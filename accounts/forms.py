from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from jurisdictions.models import Jurisdiction

class DynamicUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'user_id', 'first_name', 'last_name', 
            'email', 'role', 'status', 'state', 'is_nominated_mp', 'jurisdiction'
        )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('logged_in_user', None)
        super().__init__(*args, **kwargs)

        if 'jurisdiction' in self.fields:
            self.fields['jurisdiction'].required = False
            self.fields['jurisdiction'].queryset = Jurisdiction.objects.all().order_by('name')
        
        if 'state' in self.fields:
            self.fields['state'].required = False
            
        if 'is_nominated_mp' in self.fields:
            self.fields['is_nominated_mp'].required = False

        if current_user:
            if current_user.is_mospi_admin:
                self.fields['role'].choices = User.Role.choices
                self.fields['jurisdiction'].empty_label = "-- Select Jurisdiction (Optional) --"

            elif current_user.is_state_nodal:
                allowed_roles = [User.Role.MP, User.Role.DISTRICT_AUTHORITY]
                self.fields['role'].choices = [
                    (k, v) for k, v in User.Role.choices if k in allowed_roles
                ]

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

        is_nominated = cleaned_data.get('is_nominated_mp') or self.data.get('is_nominated_mp') in [True, 'true', 'True', '1', 'on']

        if role == User.Role.DISTRICT_AUTHORITY and not jurisdiction:
            if self.fields['jurisdiction'].disabled and self.fields['jurisdiction'].initial:
                cleaned_data['jurisdiction'] = self.fields['jurisdiction'].initial
            else:
                self.add_error('jurisdiction', 'A valid Jurisdiction must be assigned for District Authority.')

        elif role == User.Role.MP:
            if is_nominated:
                cleaned_data['jurisdiction'] = None
                cleaned_data['state'] = None
                cleaned_data['is_nominated_mp'] = True
            else:
                state = cleaned_data.get('state') or self.data.get('state')
                if not jurisdiction and not state:
                    self.add_error('jurisdiction', 'Please select a State or Jurisdiction for the elected MP.')

        elif role == User.Role.MOSPI_ADMIN:
            cleaned_data['jurisdiction'] = None

        return cleaned_data


class OfficialProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'status', 'state', 'jurisdiction')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'jurisdiction' in self.fields:
            self.fields['jurisdiction'].required = False
            self.fields['jurisdiction'].queryset = Jurisdiction.objects.all().order_by('name')
        if 'state' in self.fields:
            self.fields['state'].required = False