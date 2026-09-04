from django import forms
from blood_components.models import BloodComponent
from laboratory.models import BloodBag

class BloodComponentForm(forms.ModelForm):
    class Meta:
        model = BloodComponent
        fields = [
            'parent_bag', 'component_type', 'blood_group', 'rh_factor',
            'volume_ml', 'prepared_date', 'expiry_date', 'storage_location',
            'leukoreduced', 'irradiated', 'status', 'notes'
        ]
        widgets = {
            'prepared_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})


class ComponentSeparationForm(forms.Form):
    create_prbc = forms.BooleanField(required=False, initial=True, label="Packed Red Blood Cells (PRBC)")
    prbc_volume = forms.IntegerField(initial=250, label="PRBC Volume (mL)")
    
    create_ffp = forms.BooleanField(required=False, initial=True, label="Fresh Frozen Plasma (FFP)")
    ffp_volume = forms.IntegerField(initial=180, label="FFP Volume (mL)")
    
    create_platelet = forms.BooleanField(required=False, initial=True, label="Platelet Concentrate (RDP)")
    platelet_volume = forms.IntegerField(initial=50, label="Platelet Volume (mL)")
    
    create_cryo = forms.BooleanField(required=False, initial=False, label="Cryoprecipitate")
    cryo_volume = forms.IntegerField(initial=20, label="Cryo Volume (mL)")
    
    leukoreduced = forms.BooleanField(required=False, initial=False, label="Pre-storage Leukoreduction Performed")
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}), label="Processing Notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-check-input'})
