from django.http import Http404, JsonResponse, HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from breach.strategy import Strategy
from breach.models import Target, Victim, Round
from django.core import serializers
from .forms import TargetForm, VictimForm, AttackForm
import json
from django.utils import timezone
from breach.helpers import network
import time


def get_work(request, victim_id=0):
    assert(victim_id)

    try:
        victim = Victim.objects.get(pk=victim_id)
    except:
        raise Http404('Victim not found')

    if victim.state == 'paused':
        raise Http404('The attack for victim %i is paused' % victim.id)

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


class VictimListView(View):

    def post(self, request):
        input_data = json.loads(request.body.decode('utf-8'))
        form = VictimForm(input_data)
        if form.is_valid():
            victim = Victim.objects.create(
                sourceip=input_data['sourceip'],
            )
            return JsonResponse({
                'victim_id': victim.id
            })

    def get(self, request):
        victims = Victim.objects.filter(trashed_at=None)
        ret_victims = []
        for i, victim in enumerate(victims):
            if victim.state == 'discovered':
                if victim.running_time < 900:
                    ret_victims.append({'victim_id': victim.id, 'state': victim.state, 'sourceip': victim.sourceip})
            else:
                ret_victims.append({'victim_id': victim.id, 'state': victim.state, 'target_name': victim.target.name,
                                    'percentage': victim.percentage, 'start_time': time.mktime(victim.attacked_at.timetuple()),
                                    'sourceip': victim.sourceip})

        return JsonResponse({
            'victims': ret_victims,
        })


class AttackView(View):
    def post(self, request):
        input_data = json.loads(request.body.decode('utf-8'))
        if 'id' in input_data:
            form = AttackForm(input_data)
            if form.is_valid():
                target = Target.objects.get(name=input_data['target'])
                victim_id = input_data['id']
                victim = Victim.objects.get(pk=victim_id)
                victim.state = 'running'
                victim.attacked_at = timezone.now()
                victim.target = target
                victim.recordscardinality = target.recordscardinality
                victim.interface = network.get_interface()
                victim.realtimeurl = 'http://' + network.get_local_IP() + ':3031'
                victim.save()
        else:
            form = VictimForm(input_data)
            if form.is_valid():
                target = Target.objects.get(name=input_data['target'])
                victim = Victim.objects.create(
                    sourceip=input_data['sourceip'],
                    target=target,
                    recordscardinality=target.recordscardinality,
                    state='running',
                    attacked_at=timezone.now(),
                    interface=network.get_interface(),
                    realtimeurl='http://' + network.get_local_IP() + ':3031'
                )

        victim.attack

        return JsonResponse({
            'victim_id': victim.id
        })


class VictimDetailView(View):
    def get(self, request, victim_id):
        # get victim with the given ID
        victim = Victim.objects.get(pk=victim_id)

        rounds = Round.objects.filter(victim__id=victim_id)
        attack_details_list = []
        for round_details in rounds:
            attack_details_list.extend(round_details.fetch_per_batch_info())

        try:
            known_secret = rounds.order_by('-id').reverse()[0].knownsecret
        except:
            known_secret = victim.target.prefix

        return JsonResponse({
            'id': victim.id,
            'victim_ip': victim.sourceip,
            'state': victim.state,
            'known_secret': known_secret,
            'target_name': victim.target.name,
            'attack_details': attack_details_list,
            'percentage': victim.percentage
        })

    def put(self, request, victim_id):
        victim = Victim.objects.get(pk=victim_id)
        if victim.state == 'running':
            victim.state = 'paused'
        elif victim.state == 'paused':
            victim.state = 'running'
        victim.save()
        return HttpResponse(status=200)

    def delete(self, request, victim_id):
        victim = Victim.objects.get(pk=victim_id)
        if not victim.trashed_at:
            victim.delete()
        else:
            victim.restore()
        return HttpResponse(status=200)


class DiscoveredVictimsView(View):
    def get(self, request):
        new_victims = []
        for victimip in network.scan_network():
            victim_exists = Victim.objects.filter(state='discovered', sourceip=victimip)
            if not victim_exists:
                victim = Victim.objects.create(sourceip=victimip)
                new_victims.append({'sourceip': victim.sourceip, 'victim_id': victim.id})
            else:
                victim_exists[0].attacked_at = timezone.now()
                victim_exists[0].save()
                new_victims.append({'sourceip': victim_exists[0].sourceip, 'victim_id': victim_exists[0].id})
        return JsonResponse({
            'new_victims': new_victims
        })
