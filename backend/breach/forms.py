from django.forms import ModelForm
from breach.models import Target, Victim


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


class VictimForm(ModelForm):
    class Meta:
        model = Victim
        fields = (
            'sourceip',
        )


class AttackForm(ModelForm):
    class Meta:
        model = Victim
        fields = (
            'sourceip',
            'target'
        )
