from typing import Union, Tuple


# ## CONS ##################################################################################### #

class CalcTypes:
    eval = "evaluation"
    cmpr = "comparison"
    cmpt = "competition"

CALCS = {}


# ## DEFS ##################################################################################### #

def calc_rmse(timeseries_1, timeseries_2) -> float:
    """
    
    :return:
    """
    return 0.0


def calculate(calc_type: str, filter_id: str, calc: str, parameter_group: str,
              obsv_moduleInstId: str, model_moduleInstId: str,
              model_moduleInstIds: Union[list, None]) -> \
                  Tuple[Union[str, None], Union[str, None]]:
    """

    :return: Two strings. Success message / None; Error message / None
    """

    if calc_type == CalcTypes.eval:
        return calculate_eval(filter_id, calc, parameter_group, obsv_moduleInstId, 
            model_moduleInstId)
    elif calc_type == CalcTypes.cmpr:
        return calculate_cmpr(filter_id, calc, parameter_group, model_moduleInstIds)
    elif calc_type == CalcTypes.cmpt:
        return calculate_cmpt(filter_id, calc, parameter_group, obsv_moduleInstId,
            model_moduleInstIds)
    else:
        return None, "Not implemented yet"


def calculate_eval(filter_id: str, calc: str, parameter_group: str, obsv_moduleInstId: str,
                   model_moduleInstId: str) -> Tuple[Union[str, None], Union[str, None]]:
    """
    
    :return:
    """

    # get all timeseries headers of the filter
    # TODO

    # identifies the reference and the model parameters
    # TODO

    # 

    # apply metric
    # TODO

    return None, "EVAL not implemented yet"


def calculate_cmpr(filter_id: str, calc: str, parameter_group: str, model_moduleInstIds: list) \
                    -> Tuple[Union[str, None], Union[str, None]]:
    """
    
    :return:
    """
    return None, "CMPR not implemented yet"


def calculate_cmpt(filter_id: str, calc: str, parameter_group: str, obsv_moduleInstId: str,
                   model_moduleInstIds: list) -> Tuple[Union[str, None], Union[str, None]]:
    """
    
    :return:
    """
    return None, "CMPT not implemented yet"


def get_calculation_type(filter_id: str, calc: str, parameter_group: str, obsv_moduleInstId: str,
                         model_moduleInstId: str, model_moduleInstIds: Union[list, None]) -> \
                         Tuple[Union[str, None], Union[str, None]]:
    """
    Checks the consistency of the arguments and identify what to do.
    :return: 
    """
    
    # check if mandatory arguments were given
    for curv, curn in ((filter_id, "filter"), (calc, "calc"), (parameter_group, "parameterGroup")):
        if curv is None:
            return None, "Missing mandatory argument '%s'." % curn

    # check if 'calc' exists and get its value
    if calc not in CALCS:
        return None, "Unexpected value for 'calc': '%s'." % calc
    calc_dict = CALCS[calc]

    # try to identify the type of the calculation from the arguments given
    if obsv_moduleInstId is not None:
        if (model_moduleInstId is not None) and (model_moduleInstIds is None):
            return CalcTypes.eval, None
        elif (model_moduleInstId is None) and (model_moduleInstIds is not None):
            return CalcTypes.cmpt, None
    elif (model_moduleInstIds is not None) and (len(model_moduleInstIds) > 1):
        if model_moduleInstId is None:
            return CalcTypes.cmpr, None
    
    return None, "Unable to define the type of calculation from the set of arguments."


# ## DEFS ##################################################################################### #

CALCS["RMSE"] = {
    "function": calc_rmse,
    "types": set([CalcTypes.eval, CalcTypes.cmpt])
}
