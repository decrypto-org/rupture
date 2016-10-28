from django.forms import ModelForm
from breach.models import Target


class TargetForm(ModelForm):
    class Meta:
        model = Target
        fields = (
            'name',
            'endpoint',
            'prefix',
            'alphabet',
            'secretlength',
            'alignmentalphabet',
            'recordscardinality',
            'method'
        )
