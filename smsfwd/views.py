from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
import telnyx

from . import models, router, serializers


@csrf_exempt
def teamnum_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        teamnums = models.TeamNumber.objects.all()
        serializer = serializers.TeamNumber(teamnums, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = serializers.TeamNumber(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "OPTIONS":
        return HttpResponse(status=204)


@csrf_exempt
def teamnum_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        teamnum = models.TeamNumber.objects.get(pk=pk)
    except models.TeamNumber.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = serializers.TeamNumber(teamnum)
        return JsonResponse(serializer.data)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = serializers.TeamNumber(teamnum, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "DELETE":
        teamnum.delete()
        return HttpResponse(status=204)

    elif request.method == "OPTIONS":
        return HttpResponse(status=204)


@csrf_exempt
def msgprof_configure(request):
    """
    Update **THE** profile (create to fake it)
    """
    msgprof = models.TelnyxMessagingProfile.load()

    if request.method == "GET":
        serializer = serializers.TelnyxMessagingProfile(msgprof)
        return JsonResponse(serializer.data)

    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = serializers.TelnyxMessagingProfile(msgprof, data=data)
        if serializer.is_valid():
            try:
                serializer.save()
            except telnyx.error.ResourceNotFoundError:
                return JsonResponse({"error": "profile not found"}, status=400)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "OPTIONS":
        return HttpResponse(status=204)


@csrf_exempt
def telnyx_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "must POST"}, status=405)
    if request.content_type != "application/json":
        return JsonResponse({"error": "wrong content-type, must be JSON"}, status=415)

    payload = request.body
    signature_header = request.headers["Telnyx-Signature-Ed25519"]
    timestamp = request.headers["Telnyx-Timestamp"]

    webhook = telnyx.Webhook.construct_event(payload, signature_header, timestamp)

    router.handle_webhook(webhook)

    return HttpResponse(status=200)


@csrf_exempt
def message_list(request):
    if request.method != "GET":
        return JsonResponse({"error": "must GET"}, status=405)

    messages = models.Message.objects.all().order_by("-created")[:50]
    serializer = serializers.Message(messages, many=True)
    return JsonResponse(serializer.data, safe=False)
