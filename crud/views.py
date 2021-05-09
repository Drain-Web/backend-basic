from django.shortcuts import render

from crud.models import Region
from crud.serializers import RegionSerializer
from rest_framework.decorators import api_view
from django.http.response import JsonResponse

# Create your views here.

@api_view(['GET'])
def region(request):

    if request.method == 'GET':

        region = Region.objects.first()
        region_serializer = RegionSerializer(region, many=False)
        
        return JsonResponse(region_serializer.data, safe=False)
