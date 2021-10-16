from django.shortcuts import render

from crud.models import Boundary, Filter, Location, Map, Region, Timeseries, TimeseriesParameter
from crud.models import ThresholdValueSet, LevelThreshold, ModuleInstance, ParameterGroup

from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from crud.serializers import BoundarySerializer, FilterSerializer
from crud.serializers import LocationSerializer, LocationWithAttrSerializer
from crud.serializers import LocationDynamicSerializer, TimeseriesDatafullSerializer
from crud.serializers import TimeseriesDatalessSerializer, TimeseriesDatalessStatisticsSerializer
from crud.serializers import TimeseriesWithFiltersSerializer, TimeseriesParameterSerializer
from crud.serializers import FilterListItemSerializer, MapSerializer, RegionSerializer
from crud.serializers import ModuleInstanceSerializer, LevelThresholdSerializer
from crud.serializers import ParameterGroupSerializer, ThresholdValueSetSerializer
from rest_framework import status
import crud.libs.views_lib as lib
from crud.libs.views import timeseries_calculate as timeseries_calculate_lib
from typing import List, Union

import copy

# ## CONSTANTS ####################################################################################################### #

API_VERSION = "1.25"
GEO_DATUM = "WGS 1984"

# ## DEFS ############################################################################################################ #

def get_bool(query_attr_value: Union[None, str]) -> bool:
    if (query_attr_value is None) or (query_attr_value not in {'true', 'True'}):
        return False
    return True


def wrap_error(error_message: str):
    return JsonResponse({"message": error_message}, safe=False, 
        status=status.HTTP_400_BAD_REQUEST)


def wrap_success(data: dict):
    data["version"] = API_VERSION
    return JsonResponse(data, safe=False)


# ## 

@api_view(['GET'])
def module_instances(request):

    module_instances = ModuleInstance.objects.all()
    module_instance_serializer = ModuleInstanceSerializer(module_instances, many=True)
    return JsonResponse(module_instance_serializer.data, safe=False)

# ## MAPS ############################################################################################################ #

@api_view(['GET'])
def bondary_list(request):

    boundaries = Boundary.objects.all()
    boundary_serializer = BoundarySerializer(boundaries, many=True)
    return JsonResponse(boundary_serializer.data, safe=False)


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


# ## LOCATIONS ####################################################################################################### #

@api_view(['GET'])
def location(request):
    showAttr = request.GET.get('showAttributes')

    locs = Location.objects.all()
    if (showAttr is not None) and showAttr:
        locs_serializer = LocationWithAttrSerializer(locs, many=True)
    else:
        locs_serializer = LocationSerializer(locs, many=True)
    ret_dict = {
        "version": API_VERSION,
        "geoDatum": "WGS 1984",
        "locations": locs_serializer.data
    }

    return JsonResponse(ret_dict, safe=False)


@api_view(['GET'])
def locations_dynamic(request):
    fields_show = ['locationId', 'shortName', 'relations', 'x', 'y']
    fields_call = ['id', 'name', 'relations', 'x', 'y']

    # get requests
    show_attr = get_bool(request.GET.get('showAttributes'))
    show_filters = get_bool(request.GET.get('showFilters'))
    show_polygon = get_bool(request.GET.get('showPolygon'))

    # decide what to show and what to request
    if show_attr:
        fields_show.append('attributes')
        fields_call.append('attributes')
    if show_polygon:
        fields_show.extend(['polygon', 'polygonDescription'])
        fields_call.extend(['polygon', 'polygonDescription'])

    # call query
    locs = Location.objects.all().only(*fields_call)
    locs_serializer = LocationDynamicSerializer(locs, many=True, fields=fields_show)
    ret_dict = {
        "version": API_VERSION,
        "geoDatum": "WGS 1984",
        "locations": locs_serializer.data
    }

    # include filters if requested
    if show_filters:
        all_timeseries = Timeseries.objects.defer('events', 'thresholdValueSets', 'filter_set__boundary').all()
        all_timeseries_serializer = TimeseriesWithFiltersSerializer(all_timeseries, many=True)
        del all_timeseries
        lib.include_filters_to_locations(ret_dict["locations"], all_timeseries_serializer.data)

    return JsonResponse(ret_dict, safe=False)


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


# ## PARAMETERS ############################################################################### #

@api_view(['GET'])
def list_parameters(request):

    all_ts_parameters = TimeseriesParameter.objects.all()
    ts_parameters_serializer = TimeseriesParameterSerializer(all_ts_parameters, many=True)
    ret_dict = {
        "version": API_VERSION,
        "timeSeriesParameters": ts_parameters_serializer.data
    }
    return JsonResponse(ret_dict, safe=False)


@api_view(['GET'])
def list_parameter_groups(request):
    all_parameter_groups = ParameterGroup.objects.all()
    parameter_groups_serializer = ParameterGroupSerializer(all_parameter_groups, many=True)
    ret_dict = {
        "version": API_VERSION,
        "parameterGroups": parameter_groups_serializer.data
    }
    return JsonResponse(ret_dict, safe=False)


# ## TIMESERIES ############################################################################### #

@api_view(['GET'])
def timeseries_list_by_querystring(request):
    
    # get parameters
    filter_id = request.GET.get('filter')
    location_id = request.GET.get('location')
    show_statistics = request.GET.get('showStatistics')
    only_headers = request.GET.get('onlyHeaders')

    # set defaults
    show_statistics = False if show_statistics is None else True
    only_headers = False if only_headers is None else True

    # define if the heavy field 'events' should be defered
    defer_evts = True if (not show_statistics) or only_headers else False
    ts_objs = Timeseries.objects.defer('events') if defer_evts else Timeseries.objects
    del defer_evts

    # define filter(s) to apply
    if (filter_id is not None) and (location_id is None):
        ts_objs = ts_objs.filter(filter_set__id__contains=filter_id)
    elif (filter_id is not None) and (location_id is not None):
        ts_objs = ts_objs.filter(filter_set__id__contains=filter_id, \
            header_location_id=location_id)
    elif (filter_id is None) and (location_id is not None):
        ts_objs = ts_objs.filter(header_location_id=location_id)
    else:
        ts_objs = ts_objs.all()

    # define serializer to use
    if only_headers and (not show_statistics):
        serializer = TimeseriesDatalessSerializer
    elif only_headers and show_statistics:
        serializer = TimeseriesDatalessStatisticsSerializer
    elif (not only_headers) and show_statistics:
        return JsonResponse({"message": "Unexpected 'show_statistics' with no 'only_headers'."},
                            status=status.HTTP_400_BAD_REQUEST, safe=False)
    else:
        serializer = TimeseriesDatafullSerializer

    # get data end JSONify it
    serializer = serializer(ts_objs, many=True)
    data = [] if (len(serializer.data) == 0) else serializer.data
    return JsonResponse(data, safe=False)


# ## TIMESERIES CALCULATOR #################################################################### #

@api_view(['GET'])
def timeseries_calculate(request):

    # get parameters
    filter_id = request.GET.get('filter')
    calc = request.GET.get('calc')
    sim_param_id = request.GET.get('simParameterId')
    obs_param_id = request.GET.get('obsParameterId')
    obs_moduleInstId  = request.GET.get('obsModuleInstanceId')
    sim_moduleInstId  = request.GET.get('simModuleInstanceId')
    sim_moduleInstIds = request.GET.get('simModuleInstanceIds')

    # split multstring parameters
    model_moduleInstIds = None if sim_moduleInstIds is None else sim_moduleInstIds.split(",")

    # checks inputs and gets the type of calculation 
    calc_type, fail_mssg = timeseries_calculate_lib.get_calculation_type(filter_id, calc, 
            obs_param_id, sim_param_id, obs_moduleInstId, sim_moduleInstId, model_moduleInstIds)
    if fail_mssg is not None:
        return wrap_error(fail_mssg)
    
    # performs the calculation
    data_mssg, fail_mssg = timeseries_calculate_lib.calculate(calc_type, filter_id, calc, 
        obs_param_id, sim_param_id, obs_moduleInstId, sim_moduleInstId, model_moduleInstIds)
    
    # show output
    return wrap_success({calc_type: data_mssg}) if fail_mssg is None else wrap_error(fail_mssg)


# ## THRESHOLDS ############################################################################### #

@api_view(['GET'])
def threshold_value_sets_list(request):
    all_threshold_value_sets = ThresholdValueSet.objects.all()
    all_threshold_value_sets_serializer = ThresholdValueSetSerializer(all_threshold_value_sets,
                                                                      many=True)
    base_ret_dict = {
        "version": API_VERSION,
        "thresholdValueSets": all_threshold_value_sets_serializer.data
    }
    return JsonResponse(base_ret_dict, safe=False)


@api_view(['GET'])
def threshold_groups_list(request):
    filter_id = request.GET.get('filter')

    base_ret_dict = {
        "version": API_VERSION,
        "thresholdGroups": None
    }

    # if no filter provided, lists all threshold groups
    if filter_id is None:
        all_level_thresholds = LevelThreshold.objects.all()
        all_level_thresholds = LevelThresholdSerializer(all_level_thresholds, many=True).data
        base_ret_dict["thresholdGroups"] = \
            lib.threshold_groups_list_invert_levels(all_level_thresholds)
        return JsonResponse(base_ret_dict, safe=False)
    
    # if filter was provided, get all timeseries of this filter and map:
    #   timeseries -> thresholdValueSet -> levelThresholdValues -> levelThresholds -> ThreshGroup
    selected_timeseries = Timeseries.objects.filter(filter_set__id__contains=filter_id)
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

    # with all Threshold Level IDs, retrieve the Threshold Groups
    selected_level_thresholds = LevelThreshold.objects.filter(id__in=level_threshold_ids)
    selected_level_thresholds = \
        LevelThresholdSerializer(selected_level_thresholds, many=True).data
    base_ret_dict["thresholdGroups"] = \
        lib.threshold_groups_list_invert_levels(selected_level_thresholds)
    return JsonResponse(base_ret_dict, safe=False)
