from django import forms
from hospitals.models import Hospital

class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = [
            'name', 'code', 'license_number', 'category',
            'address', 'city', 'district', 'state', 'postal_code',
            'contact_person', 'phone', 'email', 'emergency_contact',
            'is_active', 'is_verified'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
