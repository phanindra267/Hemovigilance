from django import forms
from camps.models import BloodCamp

class BloodCampForm(forms.ModelForm):
    class Meta:
        model = BloodCamp
        fields = [
            'name', 'organizer_name', 'organizer_phone', 'organizer_email',
            'venue', 'address', 'city', 'district', 'state',
            'start_date', 'end_date', 'start_time', 'end_time',
            'coordinator', 'blood_bank', 'expected_donors', 'status', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
