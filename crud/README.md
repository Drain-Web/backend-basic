# CRUD

This is the main and only APP of the Django project. Here is where all the models and endpoints of the API are defined.

Despite of that "CRUD" stands for "Create, Read, Update, Delete", this API only allows the "Reading" component of a database access.

## Subdomains *v1* and *v1dw*

An endpoint in the *v1* subdomain is expected to behave and bring at least the same fields and the ones in the Delft-FEWS interface.

An endpoint in *v1dw* subdomain has specific content of the Drain Web (*dw*) API.

**NOTE:** Please report any incompatibility between the *v1* entrypoints and the documented entrypoints of Delf-FEEWS. 

## Endpoints already implemented

They are defined in the *api_rest/urls.py* file.

### http://.../v1/region

Returns the first Region document. It is supposed to be the only one of the database.

### http://.../v1/locations

Returns all available locations.

An endpoint with additional filters is yet to be implemented.

### http://.../v1/filters

Returns all available filters in the database.

The filters returned don't have geojson polygon data associated to it.

Should be used for listing available options only.

### http://.../v1/filter/*<id\>*

Return the filter with id=*<id\>*.

It contains the geojson polygon data.

### http://.../v1/parameters

List all timeserie parameters and their general information.

### http://.../v1/timeseries

List all timeseries in the database that attend some parameters.

When only the mandatory parameter is given, only the metadata of the timeseries is returned. If additional parameters are given, the inner data is also provided.

Example: ```http://.../v1/timeseries/filter=alpha&location=beta```

Mandatory parameter:

- **filter \*:** Filter Id

Optional parameters:

- **location:** Location Id.