from django.http import Http404, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from breach.strategy import Strategy
from breach.models import Target
from django.core import serializers
from .forms import TargetForm
import json


def get_work(request, victim_id=0):
    assert(victim_id)

    try:
        victim = Victim.objects.get(pk=victim_id)
    except:
        raise Http404('Victim not found')

    strategy = Strategy(victim)
    new_work = strategy.get_work()

    return JsonResponse(new_work)


@csrf_exempt
def work_completed(request, victim_id=0):
    assert(victim_id)

    realtime_parameters = json.loads(request.body.decode('utf-8'))
    assert('success' in realtime_parameters)

    success = realtime_parameters['success']

    try:
        victim = Victim.objects.get(pk=victim_id)
    except:
        raise Http404('Victim not found')

    strategy = Strategy(victim)
    victory = strategy.work_completed(success)

    return JsonResponse({
        'victory': victory
    })


class TargetView(View):

    def post(self, request):
        form = TargetForm(json.loads(request.body.decode('utf-8')))
        if form.is_valid():
            target = form.save()
            return JsonResponse({
               'target_name': target.name
            })

    def get(self, request):
        return JsonResponse({
            'targets': list(Target.objects.all().values())
        })
