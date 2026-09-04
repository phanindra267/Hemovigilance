from django import forms
from inventory.models import StorageArea, StorageDevice, TemperatureLog, QuarantineRecord

class TemperatureLogForm(forms.ModelForm):
    class Meta:
        model = TemperatureLog
        fields = ['storage_device', 'temperature_celsius', 'corrective_action_taken']
        widgets = {
            'corrective_action_taken': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class QuarantineForm(forms.ModelForm):
    class Meta:
        model = QuarantineRecord
        fields = ['reason', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class QuarantineReleaseForm(forms.Form):
    release_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}), label="Clinical / QA Authorization Reason for Release", required=True)
