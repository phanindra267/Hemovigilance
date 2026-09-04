from django import forms
from django.utils import timezone
from appointments.models import Appointment
from core.models import BloodBank

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['donor', 'blood_bank', 'camp', 'appointment_type', 'scheduled_date', 'time_slot', 'notes']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data['scheduled_date']
        if scheduled_date < timezone.now().date():
            raise forms.ValidationError("Appointment cannot be scheduled for a past date.")
        return scheduled_date


class DonorSelfAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['blood_bank', 'camp', 'appointment_type', 'scheduled_date', 'time_slot', 'notes']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data['scheduled_date']
        if scheduled_date < timezone.now().date():
            raise forms.ValidationError("Appointment cannot be scheduled in the past.")
        return scheduled_date
