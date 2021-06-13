from django.shortcuts import render

from crud.models import Filter, Location, Region, Timeseries, TimeseriesParameter
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from crud.serializers import FilterSerializer, LocationSerializer, RegionSerializer, TimeseriesParameterSerializer
from crud.serializers import FilterListItemSerializer, TimeseriesDatalessSerializer, TimeseriesDatafullSerializer
from rest_framework import status

# ## CONSTANTS ####################################################################################################### #

API_VERSION = "1.25"


# ## DEFS ############################################################################################################ #

@api_view(['GET'])
def location(request):

    if request.method == 'GET':
        locs = Location.objects.all()
        locs_serializer = LocationSerializer(locs, many=True)
        return JsonResponse(locs_serializer.data, safe=False)


@api_view(['GET'])
def region(request):

    if request.method == 'GET':
        region_obj = Region.objects.first()
        region_serializer = RegionSerializer(region_obj, many=False)
        return JsonResponse(region_serializer.data, safe=False)


# ## FILTERS ######################################################################################################### #

@api_view(['GET'])
def filter_detail(request, filter_id):
    """
    Gets a single filter object by its id. All information is retrieved.
    """

    if request.method == 'GET':
        try:
            filt = Filter.objects.get(pk=filter_id)
            filt_serializer = FilterSerializer(filt, many=False)
            return JsonResponse(filt_serializer.data, safe=False)
        except Filter.DoesNotExist:
            return JsonResponse({'message': 'Filter with id "%s" not found.' % filter_id},
                                status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def filter_list(request):
    """
    Lists all filters withouth their polygon data.
    """

    filts = Filter.objects.all()
    filts_serializer = FilterListItemSerializer(filts, many=True)
    return JsonResponse(filts_serializer.data, safe=False)


@api_view(['GET'])
def filter_list_by_querystring(request):
    """
    Lists all filters including (or not) polygons.
    """

    # default 'includePolygon': false
    include_polygon = request.GET.get('includePolygon')
    if (include_polygon is None) or (include_polygon.lower() == "false"):
        filts = Filter.objects.all()
        filts_serializer = FilterListItemSerializer(filts, many=True)
        return JsonResponse(filts_serializer.data, safe=False)

    # includes polygon
    filts = Filter.objects.all()
    filts_serializer = FilterSerializer(filts, many=True)

    # built return object
    ret_dict = {
        "version": API_VERSION,
        "locations": filts_serializer.data
    }

    return JsonResponse(ret_dict, safe=False)


# ## PARAMETERS ###################################################################################################### #

@api_view(['GET'])
def list_parameters(request):

    all_ts_parameters = TimeseriesParameter.objects.all()
    ts_parameters_serializer = TimeseriesParameterSerializer(all_ts_parameters, many=True)
    ret_dict = {
        "version": API_VERSION,
        "timeSeriesParameters": ts_parameters_serializer.data
    }
    return JsonResponse(ret_dict, safe=False)


# ## TIMESERIES ###################################################################################################### #

@api_view(['GET'])
def timeseries_list_by_querystring(request):
    filter_id = request.GET.get('filter')
    location_id = request.GET.get('location')

    # basic check - must provide a filter
    if filter_id is None:
        return JsonResponse({"message": "Filter ID not provided. Must be given as '?filter='."},
                            status=status.HTTP_400_BAD_REQUEST)

    # only returns the header of the timeseries
    if location_id is None:
        selected_timeseries = Timeseries.objects.filter(filter_set_id__id__contains=filter_id)
        timeseries_serializer = TimeseriesDatalessSerializer(selected_timeseries, many=True)
        return JsonResponse(timeseries_serializer.data, safe=False)

    # return full content of the timeseries
    if location_id is not None:
        all_timeseries = Timeseries.objects.filter(filter_set_id__id__contains=filter_id,
                                                   header_location_id=location_id)
        timeseries_serializer = TimeseriesDatafullSerializer(all_timeseries, many=True)
        return JsonResponse(timeseries_serializer.data, safe=False)

    return JsonResponse({"message": "Unexpected query sting."}, status=status.HTTP_400_BAD_REQUEST, safe=False)
