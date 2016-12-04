from __future__ import division
from django.http import Http404, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from breach.strategy import Strategy
from breach.models.victim import Victim
from breach.models.target import Target
from breach.models.round import Round
from breach.models.sampleset import SampleSet
from django.core import serializers
from breach.analyzer import decide_next_world_state

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


def victimID(request, victim_id=0):
    if request.method == 'GET':
        # get victim with the given ID
        victim = Victim.objects.get(pk=victim_id)

        rounds = Round.objects.filter(victim_id=victim_id)
        attack_details_list = []
        for round_details in rounds:
            attack_details_list.extend(round_details.fetch_per_batch_info())

        return JsonResponse({
            'victim_ip': victim.sourceip,
            'target_name': victim.target.name,
            'attack_details': attack_details_list,
            'percentage': victim.percentage
        })
    elif request.method == 'PUT':
        victim = Victim.objects.get(pk=request.PUT['victim_id'])[0]
        if victim.state == 'running':
            victim.state = 'paused'
        elif victim.state == 'paused':
            victim.state = 'running'
        victim.save()
        return HttpResponse(status=200)
