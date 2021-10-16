from numpy.lib.function_base import iterable
from crud.models import Boundary, Filter, Location, Map, Region, Timeseries, TimeseriesParameter
from crud.serializers import TimeseriesDatalessSerializer, TimeseriesDatafullSerializer
from typing import Union, Tuple
import pandas as pd
import numpy as np
import scipy.stats
import statistics
import math

# ############################################################################################# #

# Evaluation KGE
# http://127.0.0.1:8000/v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=KGE&modParameterId=Q.sim&obsParameterId=Q.obs&obsModuleInstanceId=ImportUSGSobs&modModuleInstanceId=ImportHLModelHist01

# Evaluation RMSE
# http://127.0.0.1:8000/v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=RMSE&modParameterId=Q.sim&obsParameterId=Q.obs&obsModuleInstanceId=ImportUSGSobs&modModuleInstanceId=ImportHLModelHist01

# Competition KGE
# http://127.0.0.1:8000/v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=KGE&modParameterId=Q.sim&obsParameterId=Q.obs&obsModuleInstanceId=ImportUSGSobs&modModuleInstanceIds=ImportHLModelHist01,Dist050t065USGSobs

# Comparison peak
# http://127.0.0.1:8000/v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=peak&modParameterId=Q.sim&obsParameterId=Q.obs&modModuleInstanceIds=ImportHLModelHist01,Dist050t065USGSobs

# ## CONS ##################################################################################### #

class CalcTypes:
    eval = "evaluation"
    cmpr = "comparison"
    cmpt = "competition"

CALCS = {}

SIMU_TIMESERIES = "simulations"
OBSV_TIMESERIES = "observations"
DECIMALS = 3


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
    return _round_float(1 - math.sqrt(r2 + a2 + b2))


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
    return _round_float(math.sqrt(np.sum((obs_vals - sim_vals)**2)/len(indexes)))


def calc_mean(sim_timeseries) -> float:
    return _round_float(convert_events_to_series(sim_timeseries).mean())


def calc_peak(sim_timeseries) -> float:
    return _round_float(convert_events_to_series(sim_timeseries).max())


# ## DEFS - private ########################################################################### #

def _group_timeseries_by_locations(all_timeseries: list, obs_parameter_id: str, 
                                   obsv_moduleInstId: str, mod_parameter_id: str,
                                   model_moduleInstIds: set) -> dict:
    """
    
    """

    ts_ids_by_location = {}
    for _, cur_ts in enumerate(all_timeseries):
        
        # get base info
        cur_ts_id, cur_h = cur_ts["id"], cur_ts["header"]
        cur_modInstId, cur_paramId = cur_h["moduleInstanceId"], cur_h["parameterId"]
        cur_loc_id = cur_h["location_id"]
        cur_obs_or_mod = None

        # check if it is the obs or continue it
        if   (cur_paramId == obs_parameter_id) and (cur_modInstId == obsv_moduleInstId):
            cur_obs_or_mod = OBSV_TIMESERIES
        elif (cur_paramId == mod_parameter_id) and (cur_modInstId in model_moduleInstIds):
            cur_obs_or_mod = SIMU_TIMESERIES
        else:
            continue

        # create entry if needed
        if cur_loc_id not in ts_ids_by_location:
            ts_ids_by_location[cur_loc_id] = {}

        # add record
        if (cur_obs_or_mod == SIMU_TIMESERIES) and (len(model_moduleInstIds) > 1):
            if cur_obs_or_mod not in ts_ids_by_location[cur_loc_id]:
                ts_ids_by_location[cur_loc_id][cur_obs_or_mod] = {}
            ts_ids_by_location[cur_loc_id][cur_obs_or_mod][cur_modInstId] = {
                "timeseriesId": cur_ts_id
            }
        else:
            ts_ids_by_location[cur_loc_id][cur_obs_or_mod] = cur_ts_id

        del cur_ts, cur_ts_id, cur_h, cur_modInstId, cur_paramId, cur_obs_or_mod
    
    return ts_ids_by_location


def _query_all_timeseries_by(locations: dict, keys: tuple, leveled: Union[set, None] = None) \
        -> list:
    """
    
    """

    all_tss = []
    for cur_key in keys:
        if (leveled is not None) and (cur_key in leveled):
            for cur_loc in locations.values():
                for cur_sim_dict in cur_loc[cur_key].values():
                    all_tss.append(cur_sim_dict["timeseriesId"])
                    del cur_sim_dict
                del cur_loc
        else:
            all_tss = all_tss + [t[cur_key] for t in locations.values()]
        del cur_key
    all_tss = Timeseries.objects.filter(pk__in=all_tss)
    all_tss = TimeseriesDatafullSerializer(all_tss, many=True).data
    return all_tss


def _remove_locs_without(locations: dict, needed_keys: tuple) -> None:
    """
    
    """

    all_locs_ids = list(locations.keys())
    for cur_loc_id in all_locs_ids:
        if False in [(k in locations[cur_loc_id]) for k in needed_keys]:
            del locations[cur_loc_id]
        del cur_loc_id
    return None


def _round_float(raw_value: float) -> None:
    return np.round(raw_value, decimals=DECIMALS)

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
        return calculate_cmpts(filter_id, calc, obs_param_id, mod_param_id, obsv_moduleInstId,
            model_moduleInstIds)
    else:
        return None, "Not implemented yet"


def calculate_evals(filter_id: str, calc: str, obs_parameter_id: str, mod_parameter_id: str, 
                    obsv_moduleInstId: str, model_moduleInstId: str) -> \
                       Tuple[Union[dict, None], Union[str, None]]:
    """
    
    :return:
    """

    obs_sim = (OBSV_TIMESERIES, SIMU_TIMESERIES)

    # get all timeseries headers of the filter
    ts_objs = Timeseries.objects.defer('events').filter(filter_set__id__contains=filter_id)
    ts_objs = TimeseriesDatalessSerializer(ts_objs, many=True).data

    # groups timeseries by locations and remove all incomplete locations
    ts_ids_by_location = _group_timeseries_by_locations(ts_objs, obs_parameter_id, 
        obsv_moduleInstId, mod_parameter_id, set([model_moduleInstId, ]))
    _remove_locs_without(ts_ids_by_location, obs_sim)

    # get all timeseries with a single query and convert list to dict
    all_tss = _query_all_timeseries_by(ts_ids_by_location, obs_sim)
    all_tss = dict([(obj["id"], obj) for obj in all_tss])
    
    # calculate metric location by location
    for cur_loc_id, cur_d in ts_ids_by_location.items():
        cur_o, cur_s = all_tss[cur_d[OBSV_TIMESERIES]], all_tss[cur_d[SIMU_TIMESERIES]]
        cur_d["value"] = CALCS[calc]["function"](cur_o["events"], cur_s["events"])
        del cur_loc_id, cur_d, cur_o, cur_s

    # "tss": all_tss
    return {"metric": calc, "locations": ts_ids_by_location}, None


def calculate_cmpr(filter_id: str, calc: str, mod_parameter_id: str, model_moduleInstIds: set) \
                    -> Tuple[Union[str, None], Union[str, None]]:
    """
    
    :return:
    """

    sim = (SIMU_TIMESERIES, )

    # get all timeseries headers of the filter
    ts_objs = Timeseries.objects.defer('events').filter(filter_set__id__contains=filter_id)
    ts_objs = TimeseriesDatalessSerializer(ts_objs, many=True).data

    # groups timeseries by locations and remove all incomplete locations
    ts_ids_by_location = _group_timeseries_by_locations(ts_objs, None, None, mod_parameter_id,
                                                        model_moduleInstIds)
    _remove_locs_without(ts_ids_by_location, sim)

    # get all timeseries with a single query and convert list to dict
    all_tss = _query_all_timeseries_by(ts_ids_by_location, sim, sim)
    all_tss = dict([(obj["id"], obj) for obj in all_tss])
    
    # calculate metric location by location, module instance by module instance
    for cur_loc_id, cur_dict in ts_ids_by_location.items():
        # get variables
        cur_sim_tss = ts_ids_by_location[cur_loc_id][SIMU_TIMESERIES]

        # calculate module instance by module instance
        for _, cur_sim_dict in cur_sim_tss.items():
            cur_sim_ts = all_tss[cur_sim_dict["timeseriesId"]]
            calc_value = CALCS[calc]["function"](cur_sim_ts["events"])
            cur_sim_dict["value"] = calc_value
            del cur_sim_ts, calc_value, cur_sim_dict
        del cur_loc_id, cur_dict

    # 
    return {"metric": calc, "locations": ts_ids_by_location}, None


def calculate_cmpts(filter_id: str, calc: str, obs_parameter_id: str, mod_parameter_id: str,
                   obsv_moduleInstId: str, model_moduleInstIds: set) -> \
                       Tuple[Union[str, None], Union[str, None]]:
    """
    Performs the competition between multiple modules
    :return:
    """

    obs_sim = (OBSV_TIMESERIES, SIMU_TIMESERIES)

    # get all timeseries headers of the filter
    ts_objs = Timeseries.objects.defer('events').filter(filter_set__id__contains=filter_id)
    ts_objs = TimeseriesDatalessSerializer(ts_objs, many=True).data

    # groups timeseries by locations and remove all incomplete locations
    ts_ids_by_location = _group_timeseries_by_locations(ts_objs, obs_parameter_id, 
        obsv_moduleInstId, mod_parameter_id, model_moduleInstIds)
    _remove_locs_without(ts_ids_by_location, obs_sim)

    # get all timeseries with a single query and convert list to dict
    all_tss = _query_all_timeseries_by(ts_ids_by_location, obs_sim, (SIMU_TIMESERIES,))
    all_tss = dict([(obj["id"], obj) for obj in all_tss])

    # calculate metric location by location, module instance by module instance
    for cur_loc_id, cur_dict in ts_ids_by_location.items():
        # get variables
        cur_obs_ts = all_tss[cur_dict[OBSV_TIMESERIES]]
        cur_sim_tss = ts_ids_by_location[cur_loc_id][SIMU_TIMESERIES]

        # calculate module instance by module instance
        for _, cur_sim_dict in cur_sim_tss.items():
            cur_sim_ts = all_tss[cur_sim_dict["timeseriesId"]]
            calc_value = CALCS[calc]["function"](cur_obs_ts["events"], cur_sim_ts["events"])
            cur_sim_dict["value"] = calc_value
            del cur_sim_ts, calc_value, cur_sim_dict
        del cur_loc_id, cur_dict, cur_obs_ts

    # 
    return {"metric": calc, "locations": ts_ids_by_location}, None


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
CALCS["mean"] = {
    "function": calc_mean,
    "types": set([CalcTypes.cmpr, ])
}
CALCS["peak"] = {
    "function": calc_peak,
    "types": set([CalcTypes.cmpr, ])
}
