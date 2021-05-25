# Fixtures

The ```.json``` files contained in this folder contain mock data to populate the database for development and demonstration purposes.

The data present in the ```.json``` must be compatible with the models defined in *models.py*.

## Files content

### crud\_fixture.json

General records.

### crud\_fixture\_filter1.json

The filter with ID 1. It is separated due to the big size data demanded for the geojson data.

### crud\_fixture\_timeseries.json

General timeseries.

## How to use

To keep the database up to date, it is recommended the execution of the following sequence of commands **after executing** ```makemigrations``` **and** ```migrate``` **:**

    $ python manage.py flush
    $ python manage.py loaddata crud/fixutures/crud_fixture.json
    $ python manage.py loaddata crud/fixtures/crud_fixture_filter1.json
    $ python manage.py loaddata crud/fixtures/crud_fixture_timeseries.json