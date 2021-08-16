from typing import Union
import argparse
import datetime
import glob
import json
import os

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
_parser.add_argument('-geoevents_list_glob', metavar='crud_prefixture_*.json',
                     help='Glob to select the files created by the script "fixture_converter-timeseries_csv.py".', 
                     type=str, required=True)
_parser.add_argument('-output_folderpath', metavar='/some/folder_path/',
                     help='Folder path in which output files will be created as output.',
                     type=str, required=True)

# ## CONS ############################################################################### #

OUT_GEOFILTERS_FIPA = "crud_fixtureAuto_geoevents.json"
OUT_BOUNDARIES_FIPA = "crud_fixtureAuto_boundaries.json"
OUT_MAPS_FIPA = "crud_fixtureAuto_maps.json"

GEOFILTERS_DB_COLLECTION = "crud.crud.filter"
BOUNDARIES_DB_COLLECTION = "crud.boundary"
MAPS_DB_COLLECTION = "crud.map"


# ## DEFS ############################################################################### #

def generate_boundaries_and_maps_dicts(geo_filter_id: str, geo_filter_dict: dict) -> \
        Union[tuple, None]:
    """

    :param geo_filter_id:
    :param geo_filter_dict:
    :return: Fixture dictionary for boundary, fixture dictionary for map extent
    """

    # build fixture for boundary
    ret_boundary_dict = {
        "model": BOUNDARIES_DB_COLLECTION,
        "fields": {
            "id": geo_filter_id,
            "name": geo_filter_dict["name"]
        }
    }
    ret_boundary_dict["fields"].update(geo_filter_dict["boundary"])

    # build fixture for map extent
    ret_map_dict = {
        "model": MAPS_DB_COLLECTION,
        "fields": {
            "id": geo_filter_id,
        }
    }
    ret_map_dict["fields"].update(geo_filter_dict["map"])

    return ret_boundary_dict, ret_map_dict


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
    geo_filter_id = geo_evt_id.split(".")[1]
    ret_dict = {
        "model": "crud.filter",
        "fields": {
            "id": geo_evt_id,
            "description": "%s @ %s" % (evt_filter_dict["filter_name"],
                                        geo_filter_dict["name"]),
            "boundary": geo_filter_id,
            "map": geo_filter_id
        }
    }
    print(" Building %s + %s" % (evt_filter_id, geo_filter_id))

    return ret_dict


# ## DEFS ############################################################################### #

def read_all_geoevents_list(glob_pattern: str) -> list:
    ret_set = set()
    all_geoenv_fipas = glob.glob(glob_pattern)
    print("Reading geoevents from %d files..." % len(all_geoenv_fipas))
    for cur_geoenv_fipa in all_geoenv_fipas:
        print(" ...read: %s." % os.path.basename(cur_geoenv_fipa))
        with open(cur_geoenv_fipa, "r") as r_file:
            cur_geoevt_list = json.load(r_file)
        ret_set.update(cur_geoevt_list)
        del cur_geoenv_fipa, cur_geoevt_list

    return list(ret_set)


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
    _geoevt_list = read_all_geoevents_list(_args.geoevents_list_glob)
    _output_fdpa = _args.output_folderpath
    del _parser, _args

    # build map extent and boundary fixtures
    _all_boundary_dicts, _all_map_dicts = [], []
    for _cur_geoflt_id, _cur_geoflt_dict in _geoflt_dict.items():
        _cur_boundary_dict, _cur_mapextent_dict = generate_boundaries_and_maps_dicts(
            _cur_geoflt_id, _cur_geoflt_dict)
        _all_boundary_dicts.append(_cur_boundary_dict)
        _all_map_dicts.append(_cur_mapextent_dict)
        del _cur_geoflt_id, _cur_geoflt_dict, _cur_boundary_dict, _cur_mapextent_dict

    # write map extent and boundary fixture files
    _out_bdary_fipa = os.path.join(_output_fdpa, OUT_BOUNDARIES_FIPA)
    _out_mpext_fipa = os.path.join(_output_fdpa, OUT_MAPS_FIPA)
    with open(_out_bdary_fipa, "w") as _w_b_file, open(_out_mpext_fipa, "w") as _w_m_file:
        json.dump(_all_boundary_dicts, _w_b_file, indent=4)
        json.dump(_all_map_dicts, _w_m_file, indent=4)
        print("Wrote: '%s' and '%s' at '%s'" % (OUT_BOUNDARIES_FIPA, OUT_MAPS_FIPA,
                                                _output_fdpa))
    del _out_bdary_fipa, _out_mpext_fipa

    # build geo-event filter fixtures
    _all_geoevt_dicts = []
    for _cur_geoevt in _geoevt_list:
        _cur_geoevt_dict = generate_geoevent_dict(_cur_geoevt, _reqest_dict, _geoflt_dict)
        if _cur_geoevt_dict is not None:
            _all_geoevt_dicts.append(_cur_geoevt_dict)
        del _cur_geoevt, _cur_geoevt_dict

    # write output file
    _geoevt_fixture_fipa = os.path.join(_output_fdpa, OUT_GEOFILTERS_FIPA)
    with open(_geoevt_fixture_fipa, "w") as w_file:
        json.dump(_all_geoevt_dicts, w_file, indent=4)
        print("Wrote: %s" % _geoevt_fixture_fipa)
    del _geoevt_fixture_fipa

    print("Finished (%d seconds)." % (datetime.datetime.now() - _ini_time).total_seconds())
