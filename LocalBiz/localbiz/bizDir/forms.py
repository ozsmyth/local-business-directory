from django import forms
from django.forms import modelformset_factory
from .models import Business, BusinessImage, BusinessHours, Review

### Business Form ###
class BusinessForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # Use Bootstrap styling for all except checkbox/multi
            if isinstance(field.widget, forms.CheckboxInput) or isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Business
        fields = [
            "name", "description", "address", "city", "state", "country",
            "phone", "email", "website", "categories", "featured",
            "established_date", "logo"
        ]
        widgets = {
            "categories": forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
            "established_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "featured": forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

### Business Image Form ###
class BusinessImageForm(forms.ModelForm):
    class Meta:
        model = BusinessImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image caption'}),
        }

### Business Hours Form ###
class BusinessHoursForm(forms.ModelForm):
    class Meta:
        model = BusinessHours
        fields = ['day_of_week', 'opening_time', 'closing_time', 'closed']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

### Review Form ###
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }

### Formsets ###
BusinessImageFormSet = modelformset_factory(
    BusinessImage,
    form=BusinessImageForm,
    extra=1,
    can_delete=True
)

BusinessHoursFormSet = modelformset_factory(
    BusinessHours,
    form=BusinessHoursForm,
    extra=1,  # We'll use existing 7 records later
    can_delete=True
)
