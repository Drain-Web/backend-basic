# Protobuf Server / file_tiles

This folder should hold independent ```protobuf``` folder structures that will be provided by the ```protobufs_server``` app.

For example: suppose out project has 2 independent ```protobuf``` hierarchical file sets identified as *"basin_alfa"* and "sewers_beta", respectivelly. The expected file/folder structure is:

```
file_tiles/
└ basins_alfa/
  └ 1/
    └ 0/
      └ 0.pbf
    └ 1/
      └ 1.pbf
    └ ...
  └ ...
  └ 7/
    └ 30/
      └ 35.pbf
        35.pbf
        ...
    └ ...
└ sewers_beta/
  └ 0/
    └ 0/
      └ 0.pbf
  └ 1/
    └ ...
  └ ...
```

Once the backend is set up and running, these files can be reached from the following example address:

```
    http://<backend_address>/protobuf_server/basins_alfa/7/30/35
```

Note that the extension ```.pbf``` is automatically assumed by the server and all tile files must have this extension.

To generate the ```.pbf``` files out of a regular ```.geojson```, the GDAL command ```ogr2ogr``` can be used as in the following example:

```
    $ ogr2ogr -f MVT trca_tiles10pls splitted_horton_multi04/order05plus.geojson -dsco MINZOOM=1 -dsco MAXZOOM=10 -dsco COMPRESS=NO
```