import json
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from breach.strategy import Strategy
from breach.models import Victim


def get_work(request, victim_id):
    try:
        victim = Victim.objects.get(pk=victim_id)
    except:
        raise Http404('Victim not found')

    strategy = Strategy(victim)

    # Example work structure:
    # return {'url': 'https://www.dimkarakostas.com/?breach-test',
    #         'amount': 10,
    #         'timeout': 0}

    new_work = strategy.get_work()

    return HttpResponse(json.dumps(new_work), content_type='application/json')

@csrf_exempt
def work_completed(request, victim_id):
    try:
        victim = Victim.objects.get(pk=victim_id)
    except:
        raise Http404('Victim not found')

    strategy = Strategy(victim)
    strategy.work_completed()

    return JsonResponse()
