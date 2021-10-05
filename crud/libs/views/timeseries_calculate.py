from crud.models import Boundary, Filter, Location, Map, Region, Timeseries, TimeseriesParameter
from crud.serializers import TimeseriesDatalessSerializer, TimeseriesDatafullSerializer
from typing import Union, Tuple
import pandas as pd
import numpy as np
import scipy.stats
import statistics
import math

# ############################################################################################# #

# http://127.0.0.1:8000/v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=KGE&modParameterId=Q.sim&obsParameterId=Q.obs&obsModuleInstanceId=ImportUSGSobs&modModuleInstanceId=ImportHLModelHist01
# http://127.0.0.1:8000/v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=RMSE&modParameterId=Q.sim&obsParameterId=Q.obs&obsModuleInstanceId=ImportUSGSobs&modModuleInstanceId=ImportHLModelHist01

# ## CONS ##################################################################################### #

class CalcTypes:
    eval = "evaluation"
    cmpr = "comparison"
    cmpt = "competition"

CALCS = {}


# ## DEFS - EQUATIONS ######################################################################### #

def calc_kge(obs_timeseries, sim_timeseries) -> float:
    """
    
    """

    # build pandas series
    obs_sr = convert_events_to_series(obs_timeseries)
    sim_sr = convert_events_to_series(sim_timeseries)
    
    # sincronize values
    indexes = obs_sr.index.intersection(sim_sr.index)
    if len(indexes) == 0:
        return None

    # subselect and get basic statistics
    obs_vals, sim_vals = obs_sr[indexes].values, sim_sr[indexes].values
    obs_stdv, sim_stdv = statistics.stdev(obs_vals), statistics.stdev(sim_vals)
    obs_mean, sim_mean = statistics.mean(obs_vals),  statistics.mean(sim_vals)

    # calculate components and final value
    r2 = (scipy.stats.pearsonr(obs_vals, sim_vals)[0] - 1) ** 2
    a2 = (((sim_stdv / sim_mean) / (obs_stdv / obs_mean)) - 1) ** 2
    b2 = ((sim_mean / obs_mean) - 1) ** 2
    return np.round(1 - math.sqrt(r2 + a2 + b2), decimals=3)


def calc_rmse(obs_timeseries, sim_timeseries) -> float:
    """
    
    :return:
    """

    # build pandas series
    obs_sr = convert_events_to_series(obs_timeseries)
    sim_sr = convert_events_to_series(sim_timeseries)

    # sincronize values
    indexes = obs_sr.index.intersection(sim_sr.index)
    if len(indexes) == 0:
        return None

    # 
    obs_vals, sim_vals = obs_sr[indexes].values, sim_sr[indexes].values
    return np.round(math.sqrt(np.sum((obs_vals - sim_vals)**2)/len(indexes)), decimals=3)


# ## DEFS ##################################################################################### #


def calculate(calc_type: str, filter_id: str, calc: str, obs_param_id: Union[str, None],
              mod_param_id: str, obsv_moduleInstId: str, model_moduleInstId: str,
              model_moduleInstIds: Union[list, None]) -> \
                  Tuple[Union[str, None], Union[str, None]]:
    """

    :return: Two strings. Success message / None; Error message / None
    """

    if calc_type == CalcTypes.eval:
        return calculate_evals(filter_id, calc, obs_param_id, mod_param_id, obsv_moduleInstId,
            model_moduleInstId)
    elif calc_type == CalcTypes.cmpr:
        return calculate_cmpr(filter_id, calc, mod_param_id, model_moduleInstIds)
    elif calc_type == CalcTypes.cmpt:
        return calculate_cmpt(filter_id, calc, obs_param_id, mod_param_id, obsv_moduleInstId,
            model_moduleInstIds)
    else:
        return None, "Not implemented yet"


def calculate_eval(calc: str, obs_timeseries_evts, mod_timeseries_evts) -> float:

    return 1.23


def calculate_evals(filter_id: str, calc: str, obs_parameter_id: str, mod_parameter_id: str, 
                    obsv_moduleInstId: str, model_moduleInstId: str) -> \
                       Tuple[Union[dict, None], Union[str, None]]:
    """
    
    :return:
    """

    # get all timeseries headers of the filter
    ts_objs = Timeseries.objects.defer('events').filter(filter_set__id__contains=filter_id)
    ts_objs = TimeseriesDatalessSerializer(ts_objs, many=True).data

    # groups timeseries by locations
    ts_ids_by_location = {}
    for _, cur_ts in enumerate(ts_objs):
        
        # get base info
        cur_ts_id, cur_h = cur_ts["id"], cur_ts["header"]
        cur_modInstId, cur_paramId = cur_h["moduleInstanceId"], cur_h["parameterId"]
        cur_loc_id = cur_h["location_id"]
        cur_obs_or_mod = None

        # check if it is the obs or continue it
        if   (cur_paramId == obs_parameter_id) and (cur_modInstId == obsv_moduleInstId):
            cur_obs_or_mod = "obsTimeseriesId"
        elif (cur_paramId == mod_parameter_id) and (cur_modInstId == model_moduleInstId):
            cur_obs_or_mod = "simTimeseriesId"
        else:
            continue

        # create entry if needed and add record
        if cur_loc_id not in ts_ids_by_location:
            ts_ids_by_location[cur_loc_id] = {}
        ts_ids_by_location[cur_loc_id][cur_obs_or_mod] = cur_ts_id

        del cur_ts, cur_ts_id, cur_h, cur_modInstId, cur_paramId, cur_obs_or_mod

    # remove all incomplete locations
    ts_ids_by_location_checked = {}
    for cur_loc_id, cur_loc_dict in ts_ids_by_location.items():
        if ("obsTimeseriesId" in cur_loc_dict) and ("simTimeseriesId" in cur_loc_dict):
            ts_ids_by_location_checked[cur_loc_id] = cur_loc_dict
    del ts_ids_by_location

    # get all timeseries with a single query
    all_obs_tss = [t["obsTimeseriesId"] for t in ts_ids_by_location_checked.values()]
    all_mod_tss = [t["simTimeseriesId"] for t in ts_ids_by_location_checked.values()]
    all_tss = all_obs_tss + all_mod_tss
    all_tss = Timeseries.objects.filter(pk__in=all_tss)
    all_tss = TimeseriesDatafullSerializer(all_tss, many=True).data
    del all_obs_tss, all_mod_tss

    # conver list in a dictionary to facilitate search
    all_tss = dict([(obj["id"], obj) for obj in all_tss])
    
    # calculate metric location by location
    for cur_loc_id, cur_dict in ts_ids_by_location_checked.items():
        cur_obs_ts = all_tss[cur_dict["obsTimeseriesId"]]
        cur_sim_ts = all_tss[cur_dict["simTimeseriesId"]]
        calc_value = CALCS[calc]["function"](cur_obs_ts["events"], cur_sim_ts["events"])
        cur_dict["value"] = calc_value
        del cur_loc_id, cur_dict, cur_obs_ts, cur_sim_ts

    # "tss": all_tss
    return {"metric": calc, "locations": ts_ids_by_location_checked}, None


def calculate_cmpr(filter_id: str, calc: str, parameter_group: str, model_moduleInstIds: set) \
                    -> Tuple[Union[str, None], Union[str, None]]:
    """
    
    :return:
    """
    
    return None, "CMPR not implemented yet"


def calculate_cmpt(filter_id: str, calc: str, obs_parameter_id: str, mod_parameter_id: str,
                   obsv_moduleInstId: str, model_moduleInstIds: set) -> \
                       Tuple[Union[str, None], Union[str, None]]:
    """
    Performs the competition between multiple modules
    TODO: untested due to only one model available, needs two or more
    :return:
    """

    # get all timeseries headers of the filter
    ts_objs = Timeseries.objects.defer('events').filter(filter_set__id__contains=filter_id)
    ts_objs = TimeseriesDatalessSerializer(ts_objs, many=True).data

    # groups timeseries by locations
    ts_ids_by_location = {}
    for _, cur_ts in enumerate(ts_objs):
        
        # get base info
        cur_ts_id, cur_h = cur_ts["id"], cur_ts["header"]
        cur_modInstId, cur_paramId = cur_h["moduleInstanceId"], cur_h["parameterId"]
        cur_loc_id = cur_h["location_id"]
        cur_obs_or_mod = None

        # check if it is the obs or continue it
        if   (cur_paramId == obs_parameter_id) and (cur_modInstId == obsv_moduleInstId):
            cur_obs_or_mod = "obsTimeseriesId"
        elif (cur_paramId == mod_parameter_id) and (cur_modInstId in model_moduleInstIds):
            cur_obs_or_mod = "simulations"
        else:
            continue

        # create entry if needed
        if cur_loc_id not in ts_ids_by_location:
            ts_ids_by_location[cur_loc_id] = {}

        # case observation: direct add
        if cur_obs_or_mod == "obsTimeseriesId":
            ts_ids_by_location[cur_loc_id][cur_obs_or_mod] = cur_ts_id
        else:
            if cur_obs_or_mod not in ts_ids_by_location[cur_loc_id]:
                ts_ids_by_location[cur_loc_id][cur_obs_or_mod] = {}
            ts_ids_by_location[cur_loc_id][cur_obs_or_mod][cur_modInstId] = {
                "timeseriesId": cur_ts_id
            }

        del cur_ts, cur_ts_id, cur_h, cur_modInstId, cur_paramId, cur_obs_or_mod

    # remove all incomplete locations
    ts_ids_by_location_checked = {}
    for cur_loc_id, cur_loc_dict in ts_ids_by_location.items():
        if ("obsTimeseriesId" in cur_loc_dict) and ("simulations" in cur_loc_dict):
            ts_ids_by_location_checked[cur_loc_id] = cur_loc_dict
    del ts_ids_by_location

    # get all timeseries ids
    all_obs_tss = [t["obsTimeseriesId"] for t in ts_ids_by_location_checked.values()]
    all_mod_tss = []
    for cur_loc in ts_ids_by_location_checked.values():
        for cur_sim_dict in cur_loc[cur_obs_or_mod].values():
            all_mod_tss.append(cur_sim_dict["timeseriesId"])
            del cur_ts_id
        del cur_loc
    all_tss = all_obs_tss + all_mod_tss
    all_tss = Timeseries.objects.filter(pk__in=all_tss)
    all_tss = TimeseriesDatafullSerializer(all_tss, many=True).data
    del all_obs_tss, all_mod_tss

    # conver list in a dictionary to facilitate search
    all_tss = dict([(obj["id"], obj) for obj in all_tss])

    # calculate metric location by location, moodule instance by module instance
    for cur_loc_id, cur_dict in ts_ids_by_location_checked.items():
        cur_obs_ts = all_tss[cur_dict["obsTimeseriesId"]]
        cur_sim_tss = ts_ids_by_location_checked[cur_loc_id]["simulations"]

        # 
        for _, cur_sim_dict in cur_sim_tss.items():
            cur_sim_ts = all_tss[cur_sim_dict["timeseriesId"]]
            calc_value = CALCS[calc]["function"](cur_obs_ts["events"], cur_sim_ts["events"])
            cur_sim_dict["value"] = calc_value
            del cur_sim_ts, calc_value, cur_sim_dict
        del cur_loc_id, cur_dict, cur_obs_ts

    # 
    return {"metric": calc, "locations": ts_ids_by_location_checked}, None


def convert_events_to_series(timeseries_events: list) -> pd.Series:
    dts = ["%s %s" % (v["date"], v["time"]) for v in timeseries_events]
    val = [v["value"] for v in timeseries_events]
    ret_sr = pd.Series(index=dts, data=val)
    return ret_sr


def get_calculation_type(filter_id: str, calc: str, obs_param_id: Union[str, None],
                         mod_param_id: str, obsv_moduleInstId: str, model_moduleInstId: str,
                         model_moduleInstIds: Union[list, None]) -> \
                         Tuple[Union[str, None], Union[str, None]]:
    """
    Checks the consistency of the arguments and identify what to do.
    :return: 
    """
    
    # check if mandatory arguments were given
    for curv, curn in ((filter_id, "filter"), (calc, "calc"), (mod_param_id, "modParameterId")):
        if curv is None:
            return None, "Missing mandatory argument '%s'." % curn

    # check if 'calc' exists and get its value
    if calc not in CALCS:
        return None, "Unexpected value for 'calc': '%s'." % calc
    calc_dict = CALCS[calc]

    # try to identify the type of the calculation from the arguments given
    if (obsv_moduleInstId is not None) and (obs_param_id is not None):
        if (model_moduleInstId is not None) and (model_moduleInstIds is None):
            return CalcTypes.eval, None
        elif (model_moduleInstId is None) and (model_moduleInstIds is not None):
            return CalcTypes.cmpt, None
    elif (model_moduleInstIds is not None) and (len(model_moduleInstIds) > 1):
        if model_moduleInstId is None:
            return CalcTypes.cmpr, None
    
    return None, "Unable to define the type of calculation from the set of arguments."


def get_timeseries_by_id(time_series_ids: list):
    Timeseries.objects.filter(pk__in=time_series_ids).data


# ## DEFS ##################################################################################### #

CALCS["RMSE"] = {
    "function": calc_rmse,
    "types": set([CalcTypes.eval, CalcTypes.cmpt])
}
CALCS["KGE"] = {
    "function": calc_kge,
    "types": set([CalcTypes.eval, CalcTypes.cmpt])
}
