from django import forms
from requests_app.models import BloodRequest, BloodRequestItem, BloodIssue, BloodReturn, DiscardRecord

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'hospital', 'patient', 'blood_bank', 'requesting_doctor',
            'urgency', 'required_date_time', 'clinical_diagnosis',
            'transfusion_indication', 'special_requirements', 'notes'
        ]
        widgets = {
            'required_date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'clinical_diagnosis': forms.Textarea(attrs={'rows': 2}),
            'transfusion_indication': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class BloodRequestItemForm(forms.ModelForm):
    class Meta:
        model = BloodRequestItem
        fields = ['component_type', 'blood_group', 'units_requested']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class BloodIssueForm(forms.ModelForm):
    class Meta:
        model = BloodIssue
        fields = ['recipient_name', 'recipient_id_proof', 'crossmatch_compatible', 'crossmatch_details', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class BloodReturnForm(forms.ModelForm):
    class Meta:
        model = BloodReturn
        fields = [
            'returned_by_name', 'cold_chain_maintained', 'visual_inspection_passed',
            'bag_seal_intact', 'condition_notes', 'disposition', 'disposition_notes'
        ]
        widgets = {
            'condition_notes': forms.Textarea(attrs={'rows': 2}),
            'disposition_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class DiscardForm(forms.ModelForm):
    class Meta:
        model = DiscardRecord
        fields = ['discard_reason', 'reason_details', 'biohazard_disposal_method', 'disposal_manifest_number']
        widgets = {
            'reason_details': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
