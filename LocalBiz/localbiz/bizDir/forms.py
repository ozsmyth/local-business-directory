from django import forms
from .models import Business, Review

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            "name", "description", "address", "city", "state", "country",
            "phone", "email", "website", "categories", "latitude",
            "longitude", "featured", "established_date", "logo"
        ]
        widgets = {
            "categories": forms.CheckboxSelectMultiple(),
            "established_date": forms.DateInput(attrs={"type": "date"}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "rating", "comment"
        ]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }
