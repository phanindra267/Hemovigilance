from django import forms
from donations.models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            'donor', 'blood_bank', 'camp', 'appointment', 'assessment',
            'donation_type', 'bag_type', 'volume_ml', 'vein_used',
            'collected_by', 'status', 'adverse_reaction', 'adverse_reaction_notes',
            'notes'
        ]
        widgets = {
            'adverse_reaction_notes': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
