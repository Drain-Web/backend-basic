from typing import Union
import argparse
import datetime
import random
import json
import sys
import os
import re


# ## DEFS ############################################################################### #

"""
Modifies the content of the input directory 'content'.
"""
def disturb_file_content(content: dict, disturbance: dict,
                         id_shift: Union[dict, None] = None) -> None:
    fields = content[0]["fields"]

    # update metadata
    fields["header_parameterId"] = disturbance["parameterId"]
    fields["header_moduleInstanceId"] = disturbance["module_instance_id"]
    fields["header_stationName"] = disturbance["station_name"]

    # disturb values in the timeseries
    min_rand, max_rand = disturbance["events_multiplication_range"]
    for cur_event in fields["events"]:
        cur_random = random.uniform(min_rand, max_rand)
        cur_event["value"] = "%.02f" % (float(cur_event["value"]) * cur_random)
        del cur_event, cur_random

    # shift ID if needed
    if id_shift is not None:
        cur_id_value = fields[id_shift["id_field"]]
        fields[id_shift["id_field"]] = cur_id_value + id_shift["shift_value"]
        print("Shifted id of %s from %d to %d" % (fields["header_location"], cur_id_value, fields[id_shift["id_field"]]))
        del cur_id_value
    else:
        print("Not shifted id of %s." % fields["header_location"])

    return None


def disturb_files(input_folder_path: str, input_file_names: list, 
                  disturbance: dict, output_folder_path: str,
                  id_shift: Union[dict, None] = None) -> None:

    if not os.path.exists(output_folder_path):
        os.mkdir(output_folder_path)
        print("Created dir: %s" % output_folder_path)

    for cur_input_fina in input_file_names:
        print("Disturbing file '%s'..." % cur_input_fina)

        # read file
        input_file_path = os.path.join(input_folder_path, cur_input_fina)
        with open(input_file_path, "r") as r_file:
            file_content = json.load(r_file)
        del input_file_path

        # disturb
        disturb_file_content(file_content, disturbance, id_shift=id_shift)

        # define output file path
        if disturbance["output_file_tag"] is not None:
            out_fina = cur_input_fina.replace("-", "%s-" % disturbance["output_file_tag"])
        else:
            out_fina = cur_input_fina
        output_file_path = os.path.join(output_folder_path, out_fina)
        del out_fina

        # save output file
        with open(output_file_path, "w") as w_file:
            json.dump(file_content, w_file, indent=4)
        print(" Wrote: %s" % output_file_path)
        del output_file_path, cur_input_fina

    return None


def get_arguments() -> dict:

    # define arguments
    _parser = argparse.ArgumentParser(description='Process some integers.')
    _parser.add_argument('-request_filepath', metavar='request.json', type=str,
                         required=True, help='Path for the .json request file.')

    # get args
    _args = _parser.parse_args()
    with open(_args.request_filepath, "r") as _r_file:
        try:
            _args_dict = json.load(_r_file)
        except json.decoder.JSONDecodeError as e:
            print("Unable to read request file. Invalid .json structure.")
            sys.exit("Error: {0}".format(e))
    del _parser, _args

    return _args_dict


def get_arguments_debug() -> dict:
    return {
        "input_folder": "/home/work/DATA/andre/laboro/202X_DrainWeb/git_repositories/backend-basic_LINUX/crud/fixtures/crud_fixture_timeseries/q",
        "input_filename_regex": "Q_.{8}-.*\.json",
        "disturbance": {
            "events_multiplication_range": [1.15, 1.40],
            "module_instance_id": "Dist115t140USGSobs",
            "station_name": None,
            "parameterId": "Q.sim",
            "output_file_tag": "d115t140USGSobs"
        },
        "output_folder": "/home/work/DATA/andre/laboro/202X_DrainWeb/git_repositories/backend-basic_LINUX/crud/fixtures/crud_fixture_timeseries/q_d115t140USGSobs"
    }


def select_files(folder_path: str, filename_regex: str) -> list:
    all_file_names = os.listdir(folder_path)
    selected_finas = [fina for fina in all_file_names if re.match(filename_regex, fina)]
    print("Selected %d out of %d files." % (len(selected_finas), len(all_file_names)))
    return selected_finas


# ## MAIN ############################################################################### #

if __name__ == "__main__":

    # for timing
    _ini_time = datetime.datetime.now()

    # get arguments
    _args_dict = get_arguments()
    # _args_dict = get_arguments_debug()
    _input_folder_path = _args_dict["input_folder"]
    _input_filename_regex = _args_dict["input_filename_regex"]
    _disturbance = _args_dict["disturbance"]
    _id_shift = _args_dict["id_shift"] if "id_shift" in _args_dict else None
    _output_folder_path = _args_dict["output_folder"]
    del _args_dict

    # list input files
    _selected_file_names = select_files(_input_folder_path, _input_filename_regex)

    # disturb and save output files
    disturb_files(_input_folder_path, _selected_file_names, _disturbance,
                  _output_folder_path, id_shift=_id_shift)

    print("Finished (%d seconds)." % (datetime.datetime.now() - _ini_time).total_seconds())
