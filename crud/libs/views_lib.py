import copy


def include_filters_to_locations(all_locations: list, all_timeseries: list) -> None:
    """
    Changes are performed in the objects of 'all_locations'.
    :param all_locations: 
    :param all_timeseries: Objects from TimeseriesDatalessSerializer
    """

    # create dictionary ('location_id': [filter_obj, filter_obj, ...]) from multiple TimeseriesDatalessSerializer
    filters_by_loc_dict = {}
    for cur_timeseries in all_timeseries:
        # get location id and filters associated to this timeseries
        cur_ts_location_id = cur_timeseries["header"]["location_id"]
        cur_ts_filters = cur_timeseries["filter_set"]

        # create new dict for a location if needed
        if cur_ts_location_id not in filters_by_loc_dict:
            filters_by_loc_dict[cur_ts_location_id] = {}

        # add filters to each location
        if cur_ts_filters is not None:
            for cur_ts_filter in cur_ts_filters:
                filters_by_loc_dict[cur_ts_location_id][cur_ts_filter["id"]] = cur_ts_filter
                del cur_ts_filter

        del cur_timeseries, cur_ts_location_id, cur_ts_filters

    # add list of filters to each location
    for cur_location in all_locations:
        cur_location_id = cur_location["locationId"]
        if cur_location_id in filters_by_loc_dict:
            cur_location["filters"] = list(filters_by_loc_dict[cur_location_id].values())
        else:
            cur_location["filters"] = []
        del cur_location, cur_location_id

    return None


def threshold_groups_list_invert_levels(selected_level_thresholds: list) -> list:
    """
    Gets all ThresholdGroup serialized objects with an additional field "ThresholdLevels", 'inverting' the relationship
    """

    thresh_groups = {}
    for lvl_thresh in selected_level_thresholds:
        for tgroup in lvl_thresh["thresholdGroup"]:
            cur_tgroup_id = tgroup["id"]
            cur_tgroup_obj = thresh_groups[cur_tgroup_id] if cur_tgroup_id in thresh_groups else copy.deepcopy(tgroup)

            # 
            cur_lvl_thresh = copy.deepcopy(lvl_thresh)
            del cur_lvl_thresh["thresholdGroup"]
            cur_tgroup_obj["threshold_levels"] = cur_tgroup_obj["threshold_levels"] \
                if "threshold_levels" in cur_tgroup_obj else []
            cur_tgroup_obj["threshold_levels"].append(cur_lvl_thresh)

            # include "threshold_levels" to the threhold group and add it to the return dictionary
            thresh_groups[cur_tgroup_id] = cur_tgroup_obj
            del tgroup, cur_tgroup_id, cur_tgroup_obj, cur_lvl_thresh
        del lvl_thresh
    del selected_level_thresholds
    
    return list(thresh_groups.values())
