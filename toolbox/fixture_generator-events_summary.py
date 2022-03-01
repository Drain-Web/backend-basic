import argparse
import datetime
import glob
import json
import sys

# ## DEFS - ARGS ######################################################################## #

def get_arguments() -> dict:
    """
    
    """

    parser = argparse.ArgumentParser(description='Summarizes all events in a list of \
        import request files.')
    parser.add_argument('-import_files_glob', metavar='"/a_folder/import_*.json"', 
                        help='Glob pattern that points to all import files considered. \
                            Note that it is double-quoted.', type=str, required=True)
    parser.add_argument('-output_file_path', metavar='/a_folder/events_summary.json',
                        help='Output file path.', type=str, required=True)
    
    return parser.parse_args()


def extract_events(all_file_paths: list) -> dict:
    """
    
    """

    ret_dict = {
        "events": {
            "definitions": {}
        }
    }

    # iterate file por file
    for cur_fipa in all_file_paths:
        
        # read file
        with open(cur_fipa, "r") as r_file:
            cur_obj = json.load(r_file)
        del cur_fipa

        # extract information
        for cur_event_id, cur_event_dict in cur_obj["events"]["definitions"].items():
            ret_dict["events"]["definitions"][cur_event_id] = {
                "filter_name": cur_event_dict["filter_name"]
            }
            del cur_event_id, cur_event_dict
        del cur_obj

    return ret_dict


# ## MAIN ############################################################################### #

if __name__ == "__main__":

    # for timing
    _ini_time = datetime.datetime.now()
    
    # read args
    _args = get_arguments()

    # list all input files and check it
    _all_inp_fipa = glob.glob(_args.import_files_glob)
    if (len(_all_inp_fipa) == 0):
        print("No files found with pattern '%s'. Aborting." % _all_inp_fipa)
        sys.exit()

    # extract all events
    _all_events = extract_events(_all_inp_fipa)
    if len(_all_events["events"]["definitions"].keys()) == 0:
        print("No events found. Aborting.")
        sys.exit()

    # save output file
    with open(_args.output_file_path, "w") as w_file:
        json.dump(_all_events, w_file, indent=4)
        print("Wrote: %s" % _args.output_file_path)

    # wrap up
    print("Finished (%d seconds)." % (datetime.datetime.now() - _ini_time).total_seconds())
