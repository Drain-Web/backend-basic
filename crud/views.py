from django.shortcuts import render

from crud.models import Filter, Location, Region, Timeseries
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from crud.serializers import FilterSerializer, LocationSerializer, RegionSerializer, TimeseriesSerializer
from rest_framework import status

# Create your views here.

@api_view(['GET'])
def filter_detail(request, id):

    if request.method == 'GET':
        try:
            filt = Filter.objects.get(pk=id)
            filt_serializer = FilterSerializer(filt, many=False)
            return JsonResponse(filt_serializer.data, safe=False)
        except Filter.DoesNotExist:
            return JsonResponse({'message': 'The tutorial does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def filter_list(request):
    
    if request.method == 'GET':
        filts = Filter.objects.all()
        filts_serializer = FilterSerializer(filts, many=True)
        return JsonResponse(filts_serializer.data, safe=False)


@api_view(['GET'])
def location(request):

    if request.method == 'GET':
        locs = Location.objects.all()
        locs_serializer = LocationSerializer(locs, many=True)
        return JsonResponse(locs_serializer.data, safe=False)


@api_view(['GET'])
def region(request):

    if request.method == 'GET':
        region = Region.objects.first()
        region_serializer = RegionSerializer(region, many=False)
        return JsonResponse(region_serializer.data, safe=False)

# ## TIMESERIES ###################################################################################################### #

@api_view(['GET'])
def timeseries_list(request):

    if request.method == 'GET':
        all_timeseries = Timeseries.objects.all()
        timeseries_serializer = TimeseriesSerializer(all_timeseries, many=True)
        return JsonResponse(timeseries_serializer.data, safe=False)
