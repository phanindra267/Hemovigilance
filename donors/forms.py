from django import forms
from donors.models import Donor, EligibilityAssessment

class DonorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = [
            'first_name', 'last_name', 'dob', 'gender', 'blood_group',
            'donor_type', 'donor_status', 'phone', 'email', 'national_id',
            'address', 'city', 'district', 'state', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'notes'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
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


class EligibilityAssessmentForm(forms.ModelForm):
    class Meta:
        model = EligibilityAssessment
        fields = [
            'donor', 'status', 'weight_kg', 'hemoglobin_g_dl',
            'systolic_bp', 'diastolic_bp', 'pulse_bpm', 'temperature_c',
            'deferral_type', 'deferral_reason', 'deferral_start_date', 'deferral_end_date',
            'medical_notes'
        ]
        widgets = {
            'deferral_start_date': forms.DateInput(attrs={'type': 'date'}),
            'deferral_end_date': forms.DateInput(attrs={'type': 'date'}),
            'deferral_reason': forms.Textarea(attrs={'rows': 2}),
            'medical_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
