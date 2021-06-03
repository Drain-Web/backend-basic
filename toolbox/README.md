# Toolbox

Here there are some standalone scripts for manipulating the dataset.

Probably they will not be part of the final release content.

The following additional packages (i.e. packages not part of the `requirements.txt`) are required to run the scripts wherein:

- pandas 1.2.4
- numpy 1.20.3

The tools available are described as follows.

The expected sequence of runs is given in the end of this page. 

## Available tools

### fixture\_converter\-timeseries\_csv.py

Converts a single or a set of timeseries data in ```.csv``` file format to the ```.json``` format used as fixtures. 

### fixture\_generator\-geoevtfilters.py

Generates the geo-event filters.

It depends on the files created in a run of ```fixture_converter-timeseries_csv.py```.

### fixture\_cleaner\-intermediate\-files.py

Removes temporary files created after a success of ```fixture_converter-timeseries_csv.py``` and ```fixture_generator-geoevtfilters.py``` scripts.

**TODO:** Implement it.

## Expected sequence of calls

### Setting up fixtures from .csv files

*Assumptions:*

1. There is one big ```.csv``` file per station/parameter;
2. Each file has constants *value units* and *datetime format*;
3. Commands are called from ```[root]/backend-basic/``` folder.
 
*Steps:*

1. Create the basic files (manually):
	- ```crud_fixture_region.json```
	- ```crud_fixture_locations.json```
2. Create a ```.json``` file with the geo-filters meta definitions.
	- *E.g.:* ```fixture_converter-timeseries_csv/input/meta/geo-filters.json```
3. Create a ```.json``` instructions for the "csv-to-fixture" conversion.
	- *E.g.:* ```fixture_converter-timeseries_csv/input/meta/import_request.json```
	- Ensure that:
		- all *"geoFilters"* listed in the dictionaries of *"files"* were defined in the file created at step 02;
		- all *"location"*  given in the dictionaries of "files" were defined in the file created at step 00.b;
4. Call ```fixture_converter-timeseries_csv.py``` with the arguments:
	- *-request_filepath*: the ```.json``` instructions file argument (step 3);
5. Ensure that the file given in the *"output_geoevtfilters\_file\_path"* field of the ```.json``` instructions file (step 3) was created and locate it;
6. Call ```fixture_generator-geoevtfilters.py``` with the arguments:
	- *-request\_filepath*: the ```.json``` instructions file (step 3);
	- *-geoevents\_list\_filepath*: the ```.json``` geo-events file located (step 5)
	- *-geofilters\_filepath*: the ```.json``` file with the definitons of the geo-filters (step 2);
	- *-geoevents\_fixture\_filepath*: the path of the output ```.json``` fixture file.
7. Fixtures can now be loaded running (with potential *tweeks* needed):
	-  ```[root]/backend-basic/manage_load_fixtures.ps1``` (Windows 10);
	-  ```[root]/backend-basic/manage_load_fixtures.sh``` (Linux - **TODO**).
8.  Once the fixtures were successfully loaded, intermediate files can be removed by calling ```fixture_clean_intermediate_files.py```.