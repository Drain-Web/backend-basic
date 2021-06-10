import random
from typing import Union
import pandas as pd
import argparse
import datetime
import json
import sys
import os

# ## INFO ############################################################################### #

# Given a .JSON request file with the instructions for conversion, generate the fixture
#  .JSON event files out of .CSV files.
# Each .JSON fixture file is named '[station_id]-[event_id].json'.

# ## ARGS ############################################################################### #

_parser = argparse.ArgumentParser(description='Process some integers.')
_parser.add_argument('-request_filepath', metavar='request.json', type=str, required=True,
                     help='Path for the .json request file.')


# ## CONS ############################################################################### #

MONGODB_MODEL = "crud.timeseries"
DEFAULT_DATA_FLAG = "0"
DEFAULT_DATA_DATE = "%Y-%m-%d"
DEFAULT_DATA_TIME = "%H:%M:%S"
DEBUG_LINES_PRINT = 10000
IS_DEBUGGING = False


# ## DEFS ############################################################################### #

def convert_all_csv_files(args_dict: dict) -> (int, set):
    """
    One-time-per request file call.
    :param args_dict:
    :return: Number of files written in the file system, set of filters created.
    """

    inp_fdpa = args_dict["input_folder_path"]
    out_fdpa = args_dict["output_timeseries_folder_path"]
    glb_attr = args_dict["global"]
    evts_dct = args_dict["events"]

    # convert file by file
    dbg_count = 2
    total_files_written, all_geoevents = 0, set()
    for cur_fina, cur_file_dict in args_dict["files"].items():

        # define inp and out file paths

        cur_inp_fipa = os.path.join(inp_fdpa, cur_fina)
        if not os.path.exists(cur_inp_fipa):
            print("File not found: %s" % cur_inp_fipa)
            del cur_inp_fipa, cur_fina, cur_file_dict
            continue

        # perform conversion of file
        cur_files_written, cur_geoevents = convert_one_csv_file(cur_inp_fipa, out_fdpa,
                                                                glb_attr, cur_file_dict,
                                                                evts_dct)
        total_files_written += cur_files_written
        all_geoevents = set.union(all_geoevents, cur_geoevents)
        del cur_inp_fipa, cur_fina, cur_file_dict, cur_files_written

        # debug
        dbg_count -= 1
        if IS_DEBUGGING and (dbg_count == 0):
            print("DEBUG BREAK: 2 stations")
            break

    return total_files_written, all_geoevents


def convert_one_csv_file(inp_fipa: str, out_fdpa: str, global_attr: dict,
                         file_attr: dict, events_dict: Union[dict, None]) -> (int, set):
    """
    Called sequentially by convert_all_csv_files()
    :param inp_fipa:
    :param out_fdpa:
    :param global_attr:
    :param file_attr:
    :param events_dict:
    :return: Number of files created in the file system and unique geo-event filters.
    """

    def datetime_parser(datetime_str: str):
        # function to peed up datetime parsing
        return datetime.datetime.strptime(datetime_str, global_attr["datetime_format"])

    # get base fina
    base_filename = os.path.basename(inp_fipa)

    # read csv file
    print(" Reading file '%s'..." % base_filename)
    inp_df = pd.read_csv(inp_fipa, parse_dates=[global_attr["datetime_column_id"], ],
                         date_parser=datetime_parser)
    inp_df.index = inp_df[global_attr["datetime_column_id"]]
    inp_df.drop(columns=[global_attr["datetime_column_id"], ], inplace=True)
    print("  ...read {0:,} rows from file '{1}'.".format(
        inp_df.shape[0], os.path.basename(inp_fipa)), flush=True)

    # reduce pdf size if needed
    base_filename = base_filename[0:-4]
    count_out_files, geo_time_filters = 0, set()
    if events_dict is not None:

        # set base and init variables
        dt_format = events_dict["datetime_format"]
        evts_defs = events_dict["definitions"]
        dbg_count = 2

        # iterate event by event
        for evt_id, evt_defs in evts_defs.items():

            # get ids and limit date times
            cur_filter_id, cur_filter_name = evt_id, evt_defs["filter_name"]
            cur_min_dt = datetime.datetime.strptime(evt_defs["min_date"], dt_format)
            cur_max_dt = datetime.datetime.strptime(evt_defs["max_date"], dt_format)

            # extract event data frame and check not empty
            cur_evt_df = inp_df[(inp_df.index >= cur_min_dt) &
                                (inp_df.index <= cur_max_dt)].copy()
            if cur_evt_df.shape[0] == 0:
                print(" No records for event ''")
                continue

            print(" Got a DF with shape {0} for event '{1}', station '{2}'.".format(
                cur_evt_df.shape, evt_id, base_filename), flush=True)

            # define geo-event filters
            cur_geo_time_filters = []
            for cur_geo_filter in file_attr["geoFilters"]:
                cur_geo_time_filter = "%s.%s" % (evt_id, cur_geo_filter)
                geo_time_filters.add(cur_geo_time_filter)
                cur_geo_time_filters.append(cur_geo_time_filter)
                del cur_geo_time_filter

            # convert extracted event into .json
            cur_entry_dict = convert_df_to_timeseries(cur_evt_df, global_attr,
                                                      file_attr["stationName"],
                                                      file_attr["location"],
                                                      cur_geo_time_filters)
            del cur_geo_time_filters

            # write json file
            cur_out_fina = "%s-%s.json" % (base_filename, evt_id)
            cur_out_fipa = os.path.join(out_fdpa, cur_out_fina)
            with open(cur_out_fipa, "w") as w_file:
                json.dump([cur_entry_dict], w_file, indent=4)
                print("  ...wrote: %s" % cur_out_fina)
                count_out_files += 1

            del evt_id, evt_defs, cur_min_dt, cur_max_dt, cur_evt_df
            del cur_out_fina, cur_out_fipa

            # debug
            dbg_count -= 1
            if IS_DEBUGGING and (dbg_count == 0):
                print(" DEBUG BREAK: 2 events per station")
                break

        print(" Wrote %d files on '%s'." % (count_out_files, out_fdpa))
        del dt_format

    else:
        print(" No events provided. Should we store all as implemented in the 'v01' "
              "version of the script?", flush=True)

    return count_out_files, geo_time_filters


def convert_df_to_timeseries(data_df: pd.DataFrame, global_attr: dict, station_name: str,
                             location_id: str, filter_set: list) -> dict:
    """
    Should be applied to an event DF
    :param data_df:
    :param global_attr:
    :param station_name:
    :param location_id:
    :param filter_set: List of filter IDs
    :return: Ready-to-be-written dictionary
    """

    # build event list
    out_events = []
    for cur_datetime, cur_value in data_df.iterrows():
        out_events.append({
            "date": cur_datetime.strftime(DEFAULT_DATA_DATE),
            "time": cur_datetime.strftime(DEFAULT_DATA_TIME),
            "value": global_attr["dataFormatting"] % cur_value,
            "flag": DEFAULT_DATA_FLAG
        })
        del cur_datetime, cur_value

    out_dict = {
        "model": MONGODB_MODEL,
        "fields": {
            "header_units": global_attr["timeStep"]["unit"],
            "header_missVal": global_attr["missVal"],
            "header_type": "instantaneous",
            "header_parameterId": global_attr["parameterId"],
            "header_stationName": station_name,
            "header_location": location_id,
            "header_timeStep_unit": global_attr["timeStep"]["unit"],

            "filter_set": filter_set,
            "events": out_events
        }
    }

    return out_dict


# ## MAIN ############################################################################### #

if __name__ == "__main__":

    # for timing
    _ini_time = datetime.datetime.now()

    # get args
    _args = _parser.parse_args()
    with open(_args.request_filepath, "r") as _r_file:
        try:
            _args_dict = json.load(_r_file)
        except json.decoder.JSONDecodeError as e:
            print("Unable to read request file. Invalid .json structure.")
            sys.exit("Error: {0}".format(e))
    del _parser, _args

    # convert all timeseries
    print("Converting %d files..." % len(_args_dict["files"].keys()), flush=True)
    _total_files_written, _all_geoevents = convert_all_csv_files(_args_dict)

    # debug
    print("Wrote a total of %d fixture files." % _total_files_written)
    print("Need to create the geo event filters: {0}".format(_all_geoevents), flush=True)

    # save geo events list
    with open(_args_dict["output_geoevtfilters_file_path"], "w") as _w_file:
        json.dump(sorted(list(_all_geoevents)), _w_file)
    print("Wrote geo events file: %s" % _args_dict["output_geoevtfilters_file_path"])

    print("Finished (%d seconds)." % (datetime.datetime.now() - _ini_time).total_seconds())
