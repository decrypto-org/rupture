from django.contrib import admin

from breach.models import Target, Victim, SampleSet

admin.site.register(Target)
admin.site.register(Victim)
admin.site.register(SampleSet)
