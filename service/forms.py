from django import forms
from .models import ServiceReport

class ServiceReportForm(forms.ModelForm):
    class Meta:
        model = ServiceReport
        fields = '__all__'
