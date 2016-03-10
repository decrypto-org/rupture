from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def get_work(request):
    return HttpResponse('Not implemented')


@csrf_exempt
def work_completed(request):
    return HttpResponse('Not implemented')
