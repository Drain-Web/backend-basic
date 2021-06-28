# Fixtures

The ```.json``` files contained in this folder contain mock data to populate the database for development and demonstration purposes.

The data present in the ```.json``` must be compatible with the models defined in *models.py*.

## Files content

Each ```.json``` file holds the records for a different collection as specified in the last part of the file name.

Files with intermediate "\_fixture\_" were created manually, while the intermediate "\_fixtureAuto\_" indicates that the file was obtained as an output of a generating or converting script. Generating or converting scripts can be found at ```[ROOT]\toolbox\fixture_(...).py```.

## Database content

The mock database describe the Elkhorn River Basin (the *region*).

A total of four "geo-filters" are present: one for the whole region (*erb\_all*) and 3 subdivisions: Elhorn River Basin North (*erb\_n*), Middle (*erb\_m*) and South (*erb\_s*).

There are 4 high-flow events observed during the years of 2019 and 2020, 2 events per year (*e2019mayMid*, *e2019julIni*, *e2020mayEnd*, *e2020junEnd*).

A total of 16 "geoevent" filters are defined (4 events * 4 geo-filters).

8 USGS stations with observed discharge and water level are present with records for both parameters on all filters, totalizing 64 timeseries.

## How to use

The files in this folder are used as arguments by the ```manage_load_fixtures[.ps1|.sh]``` importing scripts in the root directory of the repository.

The sequence of data load is important to ensure the relationships between the entries are consistent. 