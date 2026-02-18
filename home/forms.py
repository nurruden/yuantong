from django import forms
from .models import InventoryOrg

class InventoryOrganizationForm(forms.ModelForm):
    class Meta:
        model = InventoryOrg
        fields = ['org_name', 'org_code']