from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework import viewsets, views, response


def index(request):
    return HttpResponse("Paolo won!")


class TestViewSet(views.APIView):
    def get(self, request):
        value = request.query_params.get('q', 'test one two three')
        return response.Response({'say': value})


class GameViewSet(views.APIView):
    def get(self, request):
        value = request.query_params.get('q', 'test one two three')
        return response.Response({'say': value})
