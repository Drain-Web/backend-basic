import numpy as np
import argparse
import datetime
import json
import sys


# ## MAIN ############################################################################### #

if __name__ == "__main__":

    # get arguments
    _parser = argparse.ArgumentParser(description='Process some integers.')
    _parser.add_argument('-input_filepath', metavar='input.json', type=str, required=True,
                         help='Path for the .json to be simplified.')
    _parser.add_argument('-output_filepath', metavar='output.json', type=str, required=True,
                         help='Path for the new .json to be generated.')
    _parser.add_argument('-decimal_places', metavar='3', type=int, required=False, 
                         help='Path for the .json to be simplified.', default=4)

    # get args
    _args = _parser.parse_args()
    with open(_args.input_filepath, "r") as _r_file:
        try:
            _args_list = json.load(_r_file)
        except json.decoder.JSONDecodeError as e:
            print("Unable to read request file. Invalid .json structure.")
            sys.exit("Error: {0}".format(e))
    del _parser

    # output text
    _dp = _args.decimal_places
    _out_list = [[np.round(v[0], _dp), np.round(v[1], _dp)] for v in _args_list]

    # write file
    with open(_args.output_filepath, "w") as _w_file:
        json.dump(_out_list, _w_file)
        print("Wrote: %s" % _args.output_filepath)

    print("Done.")
