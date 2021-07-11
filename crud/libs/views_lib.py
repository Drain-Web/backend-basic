import copy


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
