# Fixtures

The ```.json``` files contained in this folder contain mock data to populate the database for development and demonstration purposes.

The data present in the ```.json``` must be compatible with the models defined in *models.py*.

## Files content

**TODO** - describe each file

## Database content

**TODO** - document imported data (filters, stations, timeseries, parameters, ...)

The mock database describe the Elkhorn River Basin (the *region*).

A total of four "geo-filters" are present: one for the whole region (*erb\_all*) and 3 subdivisions: Elhorn River Basin North (*erb\_n*), Middle (*erb\_m*) and South (*erb\_s*).

There are 4 high-flow events observed during the years of 2019 and 2020, 2 events per year (*e2019mayMid*, *e2019julIni*, *e2020mayEnd*, *e2020junEnd*).

A total of 16 "geoevent" filters are defined (4 events * 4 geo-filters).

## How to use

The files in this folder are used as arguments by the ```manage_load_fixtures[.ps1|.sh]``` importing scripts in the root directory of the repository.