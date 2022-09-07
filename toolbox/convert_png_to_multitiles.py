import subprocess
import argparse
import glob
import json
import sys
import os


# ## CONS ######################################################################################### #

DEFAULT_PNG_FILE_EXT = "png"
VRF_FILE_EXT = "vrf"
COORDINATE_SYSTEMS_EPSG = {
    "WGS 84|": 4326
}
SUCCESS_MULTITILE_MESSAGE_INI = "CompletedProcess"


# ## DEFS - ARGS ################################################################################ #

def get_arguments() -> dict:
    """
    
    """

    parser = argparse.ArgumentParser(description='Converts GEOTIFF file(s) into PNG file(s).')
    parser.add_argument('-input_path_png', metavar='"input_file_png" or "input_folder/"', type=str,
                        required=True, help='Path for a png file or for a folder with png files.')
    parser.add_argument('-input_filename_ext', metavar='*.png$', type=str, required=False, 
                        default=DEFAULT_PNG_FILE_EXT,
                        help='Extension of the png files in "input_path" if "input_path" is a ' +
                             'folder.')
    parser.add_argument('-output_folder_path', metavar='output_folder/', type=str,
                        required=True, help='Path for the folder in which the output files will ' +
                                            'be written')

    # input_path_png, input_path_meta, output_folder_path
    return parser.parse_args()


# ## DEFS ####################################################################################### #

def _get_epsg(desc: str) -> int:
    """
    
    :param desc:
    :return:
    """

    try:
        epsg = int(desc)
    except ValueError as ve:
        epsg = COORDINATE_SYSTEMS_EPSG[desc]
    return epsg


def _create_vrf_file(png_file_path: str, metainfo_file_path: str) -> str:
    """
    
    :param png_file_path:
    :param metainfo_file_path:
    :return: 
    """

    # read meta info
    with open(metainfo_file_path, "r") as r_file:
        metainfo = json.load(r_file)

    # define command arguments
    epsg_num = _get_epsg(metainfo["coord_system"])
    min_lon, max_lon = metainfo["lon_min"], metainfo["lon_max"]
    min_lat, max_lat = metainfo["lat_min"], metainfo["lat_max"]
    img_h, img_w = metainfo["image_h"], metainfo["image_w"]
    vrt_file_path = "%s.vrt" % png_file_path[0:-4]

    # build gdal command
    cmd = ("gdal_translate -of VRT "
                 "-a_srs EPSG:%d "
                 "-gcp   0     0   %f %f "
                 "-gcp %d   0   %f %f "
                 "-gcp %d %d %f %f "
                 "%s %s")
    
    # fill gdal command
    cmd = cmd % (epsg_num,
                 min_lon, max_lat,
                 img_w, max_lon, max_lat,
                 img_w, img_h, max_lon, min_lat,
                 png_file_path, vrt_file_path)
    
    # print(" cmd:", cmd)

    # run gdal command and handle success/failure
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)

    # result check
    if not os.path.exists(vrt_file_path):
        print("Did not create .VRF file: %s" % vrt_file_path)
        sys.exit(1)

    return vrt_file_path


def _create_multitiles_files(vrf_file_path: str, out_base_folder_path: str) -> None:
    """
    
    :param vrf_file_path:
    :param out_folder_path:
    :return:
    """

    # define output
    base_file_path = os.path.basename(vrf_file_path)[0:-(len(VRF_FILE_EXT)+1)]
    out_folder_path = os.path.join(out_base_folder_path, base_file_path)

    # create multitiles out of vrt
    cmd = "gdal2tiles.py -p mercator -w none --xyz --no-kml %s %s" % (vrf_file_path, out_folder_path)
    result = str(subprocess.run(cmd, stdout=subprocess.PIPE, shell=True))

    # result check
    if not result.startswith(SUCCESS_MULTITILE_MESSAGE_INI):
        print("Unexpected output: %s" % result)
        sys.exit(1)
    
    print("- Converted: %s" % (base_file_path))

    return None


def convert_png_to_tif(png_file_path: str, metainfo_file_path: str, out_folder_path: str) -> None:
    """
    
    :param png_file_path:
    :param metainfo_file_path:
    :param out_folder_path:
    :return:
    """

    # create VRT out of JSON with metainformation
    vrf_file_path = _create_vrf_file(png_file_path, metainfo_file_path)

    # create multitiles
    _create_multitiles_files(vrf_file_path, out_folder_path)

    return None


# ## MAIN ###################################################################################### ##

if __name__ == "__main__":

    # get args
    _args = get_arguments()

    # list PNG files
    if not os.path.exists(_args.input_path_png):
        print("Not found: %s" % _args.input_path_png)
        sys.exit(1)
    elif os.path.isdir(_args.input_path_png):
        _glob_regex = os.path.join(_args.input_path_png, "*.%s" % _args.input_filename_ext)
        _all_pngs_fipas = glob.glob(_glob_regex)
    else:
        _all_pngs_fipas = [_args.input_path_png, ]
    print("Provided %d PNG files." % len(_all_pngs_fipas))

    # list JSON files
    _all_json_fipas = []
    for _cur_png_fipa in _all_pngs_fipas:
        _cur_json_fipa = "%sjson" % _cur_png_fipa[:-len(_args.input_filename_ext)]
        if not os.path.exists(_cur_json_fipa):
            print("Not found: '%s'. Aborting." % _cur_json_fipa)
            sys.exit(1)
        _all_json_fipas.append(_cur_json_fipa)
        del _cur_png_fipa

    # convert all PMG into TIF files
    [convert_png_to_tif(_cur_png_fipa, _cur_json_fipa, _args.output_folder_path) 
                        for (_cur_png_fipa, _cur_json_fipa) 
                        in zip(_all_pngs_fipas, _all_json_fipas)]

    print("Done.")
