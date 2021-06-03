from typing import Union
import argparse
import datetime
import json

# ## INFO ############################################################################### #

# This file generates the fixtures for the geo event filters
# It crosses the information about:
# - the events in the request file (handmade);
# - the geofilters in the geofilters file (handmade),
# - the geofilters list in the geofilters file ().

# ## ARGS ############################################################################### #

_parser = argparse.ArgumentParser(description='Process some integers.')
_parser.add_argument('-request_filepath', metavar='request.json', type=str, required=True,
                     help='Path for the .json request file used to run '
                          '"fixture_converter-timeseries_csv_v02.py".')
_parser.add_argument('-geofilters_filepath', metavar='geofilters.json', type=str,
                     help='Path for the .json file with basic definitions of the '
                          'geofilters.', required=True)
_parser.add_argument('-geoevents_list_filepath', metavar='crud_prefixture_geoevts.json',
                     help='File created by "fixture_converter-timeseries_csv.py".',
                     type=str, required=True)
_parser.add_argument('-geoevents_fixture_filepath', metavar='crud_fixture_geoevts.json',
                     help='File to be created as output.', type=str, required=True)

# ## CONS ############################################################################### #


# ## DEFS ############################################################################### #

def generate_geoevent_dict(geo_evt_id: str, request_info: dict, geo_filters: dict) -> \
        Union[dict, None]:
    """

    :param geo_evt_id: Primary Key (string)
    :param request_info:
    :param geo_filters:
    :return:
    """

    print("Setting up: %s" % geo_evt_id)

    # separate id
    try:
        evt_filter_id, geo_filter_id = geo_evt_id.split(".")
    except ValueError:
        print(" Unable to parse geo event filter: {0}".format(geo_evt_id))
        return None

    # grab event info
    try:
        evt_filter_dict = request_info["events"]["definitions"][evt_filter_id]
    except KeyError:
        print(" Unable to find event '%s'." % evt_filter_id)
        return None

    # grab geo info
    try:
        geo_filter_dict = geo_filters[geo_filter_id]
    except KeyError:
        print(" Unable to find geo filter '%s'." % geo_filter_id)
        return None

    # build output object
    ret_dict = {
        "model": "crud.filter",
        "fields": {
            "id": geo_evt_id,
            "description": "%s @ %s" % (evt_filter_dict["filter_name"],
                                        geo_filter_dict["name"]),
            "boundary": geo_filter_dict["boundary"],
            "mapExtent": geo_filter_dict["mapExtent"]
        }
    }
    print(" Building %s + %s" % (evt_filter_id, geo_filter_id))

    return ret_dict


# ## MAIN ############################################################################### #

if __name__ == "__main__":

    # for timing
    _ini_time = datetime.datetime.now()

    # get args
    _args = _parser.parse_args()
    with open(_args.request_filepath, "r") as _r_file:
        _reqest_dict = json.load(_r_file)
    with open(_args.geofilters_filepath, "r") as _r_file:
        _geoflt_dict = json.load(_r_file)
    with open(_args.geoevents_list_filepath, "r") as _r_file:
        _geoevt_list = json.load(_r_file)
    _geoevt_fixture_fipa = _args.geoevents_fixture_filepath
    del _parser, _args

    # build fixtures
    _all_geoevt_dicts = []
    for _cur_geoevt in _geoevt_list:
        _cur_geoevt_dict = generate_geoevent_dict(_cur_geoevt, _reqest_dict, _geoflt_dict)
        if _cur_geoevt_dict is not None:
            _all_geoevt_dicts.append(_cur_geoevt_dict)
        del _cur_geoevt, _cur_geoevt_dict

    # write output file
    with open(_geoevt_fixture_fipa, "w") as w_file:
        json.dump(_all_geoevt_dicts, w_file, indent=4)
        print("Wrote: %s" % _geoevt_fixture_fipa)

    print("Finished (%d seconds)." % (datetime.datetime.now() - _ini_time).total_seconds())
