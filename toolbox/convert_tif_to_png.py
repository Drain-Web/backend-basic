from convert_tif_to_png.float_to_rgba import float_to_rgb, float_to_alpha
from PIL.TiffTags import TAGS
from typing import Union
from PIL import Image
import numpy as np
import argparse
import glob
import json
import sys
import os

# ## INFO ############################################################################### #

# Given:
# - a geotiff file (.geotiff, .tiff, .tif), or
# - a folder with geotiff files
# Creates:
# - one RBG-colored PNG file for each geotiff file given with the same 2D dimensions by
#     applying the functions in convert_tif_to_png.float_to_rgba pixel-wise, and
# - one (or many) JSON file(s) with geographic metainformation needed for eventual
#     multitiling the raster.

# ## CONS ###################################################################################### ##

DEFAULT_TIF_FILE_EXT = "tif"


# ## DEFS - ARGS ################################################################################## #

def get_arguments() -> dict:
    """
    
    """

    parser = argparse.ArgumentParser(description='Converts GEOTIFF file(s) into PNG file(s).')
    parser.add_argument('-input_path', metavar='"input_file.tiff" or "input_folder/"', type=str,
                        required=True, help='Path for a geotiff file or for a folder with ' +
                                            'geotiff files.')
    parser.add_argument('-input_filename_ext', metavar='*.tif$', type=str, required=False, 
                        default=DEFAULT_TIF_FILE_EXT,
                        help='Extension of the geotiff files in "input_path" if "input_path" is ' +
                             'a folder.')
    parser.add_argument('-output_folder_path', metavar='output_folder/', type=str,
                        required=True, help='Path for the folder in which the output files will ' +
                                            'be written')
    return parser.parse_args()


# ## DEFS ###################################################################################### ##

def colorize_tif_cell(raw_cell_value: float) -> Union[np.array, tuple]:

    if raw_cell_value < -0.015:
        ret_vals = (0, 0, 0, 0)
    elif (raw_cell_value >= -0.015) and (raw_cell_value < 0.0):
        ret_vals = (0, 0, 0, 255)
    else:
        ret_vals = (50*raw_cell_value, 150*raw_cell_value, 250*raw_cell_value, 255)

    return ret_vals


colorize_tif_cell = np.vectorize(colorize_tif_cell)


def create_alpha_channel(data: np.array) -> np.array:
    return np.uint((data > -1.5)*255)


def create_rgb_channels(data: np.array) -> tuple:

    filter = (data > 0)
    r_channel = filter * (data * 0.5)
    g_channel = filter * (data * 1.0)
    b_channel = filter * (data * 2.5)

    return r_channel, g_channel, b_channel


def convert_tif_to_png(tif_file_path: str, out_folder_path: str) -> None:

    # define output file path
    out_basename = os.path.basename(tif_file_path)[:-4]
    out_png_fipa = os.path.join(out_folder_path, "%s.png" % out_basename)
    out_jsn_fipa = os.path.join(out_folder_path, "%s.json" % out_basename)
    del out_basename

    # get image 2D data and metadata
    img = Image.open(tif_file_path)
    img_np_array = np.int16(np.array(img))                                  # data
    img_tag_dict = {TAGS[key]: img.tag[key] for key in img.tag.keys()}  # metadata
    img.close()
    del img

    # create RGBA
    alfa_channel = create_alpha_channel(img_np_array)
    r_channel, g_channel, b_channel = create_rgb_channels(img_np_array)
    rgba_channel = np.uint8([r_channel, g_channel, b_channel, alfa_channel])
    rgba_channel = rgba_channel.transpose(1, 2, 0)
    del alfa_channel, r_channel, g_channel, b_channel
    
    # create, show(?), save, close PNG
    img = Image.fromarray(rgba_channel, 'RGBA')  # 
    # img.show()                                           # show image, but not today
    img.save(out_png_fipa), print("Wrote:", out_png_fipa)  # save figure
    img.close()

    # get geotiff meta information - image size
    img_w, img_h = img_tag_dict['ImageWidth'][0], img_tag_dict['ImageLength'][0]

    # get geotiff meta information - bounding box coordinates
    dim_lon = img_tag_dict['ModelPixelScaleTag'][0]
    dim_lat = img_tag_dict['ModelPixelScaleTag'][1]
    min_lon = img_tag_dict['ModelTiepointTag'][3]
    max_lat = img_tag_dict['ModelTiepointTag'][4]
    max_lon, min_lat = min_lon + (dim_lon * img_w), max_lat - (dim_lat * img_h)
    del dim_lon, dim_lat

    # coordinate system
    coord_system = img_tag_dict['GeoAsciiParamsTag'][0]

    # build output obj
    meta_dict = {
        "image_w": img_w,
        "image_h": img_h,
        "lon_min": min_lon, 
        "lon_max": max_lon,
        "lat_min": min_lat,
        "lat_max": max_lat,
        "coord_system": coord_system
    }

    # write json file
    with open(out_jsn_fipa, "w") as w_file:
        json.dump(meta_dict, w_file)
    print("Wrote: %s" % out_jsn_fipa)

    return None


# ## MAIN ###################################################################################### ##

if __name__ == "__main__":

    # get args
    _args = get_arguments()

    # list tif files
    if not os.path.exists(_args.input_path):
        print("Not found: %s" % _args.input_path)
        sys.exit(1)
    elif os.path.isdir(_args.input_path):
        _glob_regex = os.path.join(_args.input_path, "*.%s" % _args.input_filename_ext)
        _all_tifs_fipas = glob.glob(_glob_regex)
    else:
        _all_tifs_fipas = [_args.input_path, ]
    print("Provided %d TIF files." % len(_all_tifs_fipas))

    # convert all TIF into PNG files
    [convert_tif_to_png(_cur_fipa, _args.output_folder_path) for _cur_fipa in _all_tifs_fipas]

    print("Done.")
