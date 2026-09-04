from django import forms
from laboratory.models import BloodBag, LabSample, ScreeningResult

class LabSampleForm(forms.ModelForm):
    class Meta:
        model = LabSample
        fields = ['blood_bag', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class ScreeningResultForm(forms.ModelForm):
    class Meta:
        model = ScreeningResult
        fields = [
            'test_category', 'test_name', 'result',
            'kit_lot_number', 'kit_expiry', 'quantitative_value', 'interpretation_notes'
        ]
        widgets = {
            'kit_expiry': forms.DateInput(attrs={'type': 'date'}),
            'interpretation_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class BloodBagForm(forms.ModelForm):
    class Meta:
        model = BloodBag
        fields = ['blood_group', 'rh_factor', 'volume_ml', 'bag_type', 'storage_location', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
