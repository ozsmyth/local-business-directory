from django import forms
from .models import Business

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            "name", "description", "address", "city", "state", "zip_code",
            "phone", "email", "website", "categories", "latitude",
            "longitude", "featured", "established_date", "logo"
        ]
        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
            "established_date": forms.DateInput(attrs={"type": "date"}),
        }
