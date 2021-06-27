from django.shortcuts import render

from crud.models import Boundary, Filter, Location, Map, Region, Timeseries, TimeseriesParameter, ThresholdGroup
from crud.models import ThresholdValueSet, LevelThreshold

from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from crud.serializers import BoundarySerializer, FilterSerializer, LocationSerializer, MapSerializer, RegionSerializer
from crud.serializers import FilterListItemSerializer, TimeseriesDatalessSerializer, TimeseriesDatafullSerializer
from crud.serializers import TimeseriesParameterSerializer, ThresholdGroupSerializer, ThresholdValueSetSerializer
from crud.serializers import LevelThresholdSerializer
from rest_framework import status

# ## CONSTANTS ####################################################################################################### #

API_VERSION = "1.25"
GEO_DATUM = "WGS 1984"


# ## MAPS ############################################################################################################ #

@api_view(['GET'])
def bondary_list(request):

    boundaries = Boundary.objects.all()
    boundary_serializer = BoundarySerializer(boundaries, many=True)
    return JsonResponse(boundary_serializer.data, safe=False)


@api_view(['GET'])
def location(request):

    locs = Location.objects.all()
    locs_serializer = LocationSerializer(locs, many=True)
    ret_dict = {
        "version": API_VERSION,
        "geoDatum": "WGS 1984",
        "locations": locs_serializer.data
    }

    return JsonResponse(ret_dict, safe=False)


@api_view(['GET'])
def maps_list(request):

    maps = Map.objects.all()
    maps_serializer = MapSerializer(maps, many=True)
    return JsonResponse(maps_serializer.data, safe=False)


@api_view(['GET'])
def region(request):

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
        if len(timeseries_serializer.data) == 0:
            return JsonResponse([], safe=False)
        return JsonResponse(timeseries_serializer.data, safe=False)

    # return full content of the timeseries
    if location_id is not None:
        all_timeseries = Timeseries.objects.filter(filter_set_id__id__contains=filter_id,
                                                   header_location_id=location_id)
        timeseries_serializer = TimeseriesDatafullSerializer(all_timeseries, many=True)
        return JsonResponse(timeseries_serializer.data, safe=False)

    return JsonResponse({"message": "Unexpected query sting."}, status=status.HTTP_400_BAD_REQUEST, safe=False)


# ## THRESHOLDS ##################################################################################################### #

@api_view(['GET'])
def threshold_value_sets_list(request):
    all_threshold_value_sets = ThresholdValueSet.objects.all()
    all_threshold_value_sets_serializer = ThresholdValueSetSerializer(all_threshold_value_sets, many=True)
    return JsonResponse(all_threshold_value_sets_serializer.data, safe=False)
 

@api_view(['GET'])
def threshold_groups_list(request):
    filter_id = request.GET.get('filter')

    base_ret_dict = {
        "version": API_VERSION,
        "thresholdGroups": None
    }

    # if no filter provided, lists all threshold groups
    if filter_id is None:
        all_thresholdgroups = ThresholdGroup.objects.all()
        all_thresholdgroups_serializer = ThresholdGroupSerializer(all_thresholdgroups, many=True)
        base_ret_dict["thresholdGroups"] = all_thresholdgroups_serializer.data
        return JsonResponse(base_ret_dict, safe=False)
    
    # if filter was provided, get all timeseries of this filter and map:
    #   timeseries -> thresholdValueSet -> levelThresholdValues -> levelThresholds -> ThreshGroup
    selected_timeseries = Timeseries.objects.filter(filter_set_id__id__contains=filter_id)
    selected_timeseries = TimeseriesDatalessSerializer(selected_timeseries, many=True).data
    level_threshold_ids = set()
    for sel_ts in selected_timeseries:
        for thresh_value_set in sel_ts["thresholdValueSets"]:
            for thresh_value in thresh_value_set["levelThresholdValues"]:
                level_threshold_ids.add(thresh_value["levelThresholdId"])
                del thresh_value
            del thresh_value_set
        del sel_ts
    del selected_timeseries
    selected_level_thresholds = LevelThreshold.objects.filter(id__in=level_threshold_ids)
    selected_level_thresholds = LevelThresholdSerializer(selected_level_thresholds, many=True).data
    thresh_groups = {}
    for lvl_thresh in selected_level_thresholds:
        for thresh_group in lvl_thresh["thresholdGroup"]:
            thresh_groups[thresh_group["id"]] = thresh_group
            del thresh_group
        del lvl_thresh
    del selected_level_thresholds

    base_ret_dict["thresholdGroups"] = list(thresh_groups.values())
    return JsonResponse(base_ret_dict, safe=False)
