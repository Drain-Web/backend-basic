# Multi-tiles Server

This app provides dynamic entry points for *multi-tiles rasters*.

## Generating single PNG raster from single GEOTIFF raster

Given a single-band GEOTIFF raster. We can convert it to a colored PNG file and obtain its geographic metadata needed to "multitile" using the script ```convert_tif_to_png.py``` in ```toolbox/```.

## Generating multitiled PNG raster from single PNG raster

### Shortcut

Use the script ```convert_png_to_multitiles.py``` in ```toolbox/``` for batch processing.

### Full commands

GDal tools are used.

Given a (rectangular) raster PNG image (```<IMAGE_PNG>```) that represents a geographic information.

We need to know in advance:

- its geographic bounding box (```<MIN_LAT>```, ```<MAX_LAT>```, ```<MIN_LON>```, ```<MAX_LON>```);
- its projection system with knwon EPSG code (```<EPSG_#>```);
- its width x heigh dimensions (```<W_#>```, ```<H_#>```).

First it is necessary to create a ```<META_VRT>``` file:

```
$ gdal_translate -of VRT \\
                 -a_srs EPSG:<EPSG_#> \\
                 -gcp   0     0   <MIN_LON> <MAX_LAT> \\
                 -gcp <W_#>   0   <MAX_LON> <MAX_LAT> \\
                 -gcp <W_#> <H_#> <MAX_LON> <MIN_LAT> \\
                 <IMAGE_PNG> <META_VRT>
```
And then use:

```
$ gdal2tiles.py -p mercator -w none --xyz --no-kml <META_VRT> <OUTPUT_FOlDER>
```

It will generate the folder with the basename ```<OUTPUT_FOlDER>```.

E.g.:

```
$ gdal_translate -of VRT -a_srs EPSG:4326 -gcp 0 0 -79.374 43.688 -gcp 802 0 -79.355 43.688 -gcp 802 1000 -79.355 43.666 20130708_2030_rain.png 20130708_2030_rain.vrt
$ gdal2tiles.py -p mercator -w none --xyz --no-kml 20130708_2030_rain.vrt out_fd/
$ cd out_fd/
```
