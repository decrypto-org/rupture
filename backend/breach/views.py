import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def create_new_work():
    return {'url': 'https://www.dimkarakostas.com/?breach-test',
            'amount': 10,
            'timeout': 0}


def get_work(request):
    new_work = create_new_work()
    return HttpResponse(json.dumps(new_work), content_type='application/json')


@csrf_exempt
def work_completed(request):
    return HttpResponse('Not implemented')
