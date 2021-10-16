# CRUD

This is the main and only APP of the Django project. Here is where all the models and endpoints of the API are defined.

Despite of that "CRUD" stands for "Create, Read, Update, Delete", this API only allows the "Reading" component of a database access.

## Subdomains *v1* and *v1dw*

An endpoint in the *v1* subdomain is expected to behave and bring at least the same fields and the ones in the Delft-FEWS interface.

An endpoint in *v1dw* subdomain has specific content of the Drain Web (*dw*) API.

**NOTE:** Please report any incompatibility between the *v1* entrypoints and the documented entrypoints of Delf-FEEWS.

## Endpoints already implemented

They are defined in the *api_rest/urls.py* file.

### https://.../v1/region

Returns the first Region document. It is supposed to be the only one of the database.

### https://.../v1/locations

Returns all available locations.

An endpoint with additional filters is yet to be implemented.

Optional parameter:

- **showAttributes:** Expects "true" or "false" [default].

Example: ```http://.../v1/locations/?showAttributes=true```

### http://.../v1dw/locations?showFilters=true

Returns all available locations, with the particularity of allowing the retrieval of all filters to which the locations are associated.

Optional parameter:

- **showAttributes:** Expects ```true``` or ```false``` [default].
- **showFilters:** Expects ```true``` or ```false``` [default].
- **showPolygons:** Expects ```true``` or ```false``` [default].

The use of ```showFilters=true``` makes the response time longer than without it due to the need of additional queries.

Example: ```http://.../v1dw/locations/?showFilters=true```

### https://.../v1/filters

Returns all available filters in the database.

The filters returned don't have geojson polygon data associated to it.

Should be used for listing available options only.

### https://.../v1dw/filters/

Pretty similar to the aforementioned *http://.../v1/filters*, with the difference that it accepts the following parameters:

- **includePolygon:** Expects ```true``` or ```false``` [default].

Example: ```http://.../v1dw/filters/?includePolygon=true```  

### https://.../v1/filter/*<id\>*

Return the filter with id=*<id\>*.

It contains the geojson polygon data.

### https://.../v1/parameters

List all timeserie parameters and their general information.

### https://.../v1/timeseries

List all timeseries in the database that attend some parameters.

When only the mandatory parameter is given, only the metadata of the timeseries is returned. If additional parameters are given, the inner data is also provided.

Example: ```http://.../v1/timeseries/?filter=alpha&location=beta```

Mandatory parameter:

- **filter:** Filter Id.

Optional parameters:

- **location:** Location Id.

- **showStatistics:**  Expects ```true``` or ```false``` [default].

    - If ```true```, the additional fields ```firstValueTime```, ```lastValueTime```, ```maxValue```, ```minValue```, ```valueCount``` are included in the response data.
    - Ignored if the argument ```location``` is provided.

### https://.../v1dw/boundaries

Lists all filter boundaries with their polygons.

### https://.../v1dw/maps

List all map extents.

### https://.../v1dw/parameter_groups

List all parameter groups.

### https://.../v1dw/threshold_groups

List all threshold groups. It can be used to retrieve the options to be used for display state-dependent icons on maps.

Defining the *filter id* restricts the number of entries returned to only the thresholds that are associated to at least one timeseries.

Optional parameter:

- **filter:** Filter Id

Example: ```https://.../v1dw/threshold_groups?filter=alpha```

### http://.../v1dw/threshold_value_sets

List all sets of values for timeseries thresholds.

Each *value set* has a set of threshold values (*levelThresholdValues*).

Each value set has an id and a value function (*valueFunction*). Value functions have the pattern:

- if is a string surrounded by ```@```:
    - the value is location-dependent;
    - the inner string is the attribute field of the location that holds its value;
    - E.g.: ```"@floodHraw@"``` says that this value is in the location's attribute ```floodHraw```.
- if is a raw number (integer or float):
    - this value is constant for all locations.

### http://.../v1dw/module_instances

List all module instances registered in the system.

### http://.../v1dw/timeseries_calculator

Returns the results of a specified calculation involving two or more groups of timeseries.

All timeseries associated with a filter are compared.

Depending on the types and numbers of the involved timeseries (defined as the HTTP GET arguments), the calculation can be of one of among the following types:

1. *evaluation*: 1 observation x 1 model,
2. *competition*: 1 observation x 2 or more models,
3. *comparison*: 2 or more models.

Mandatory parameters:

- **filter**: single string. Filter Id.
- **calc**: single string. Valid values:
    - **evaluation** / **competition**: "RMSE", "KGE",
    - **comparison**: "PeakValue", "MeanValue".
- **simParameterId**: single string. The ParameterId for the simulation(s).

Optional parameters\*:

- **obsParameterId<sup>1,3</sup>**: single string. The ParameterId for the observation.
- **obsModuleInstanceId<sup>1,3</sup>**: single string.
- **simModuleInstanceId<sup>1</sup>**: single string.
- **simModuleInstanceIds<sup>2,3</sup>**: multiple strings (separated by commas).

\*: The superscripted number indicates the type of the calculation to which the optional argument is mandatory.

Example<sup>1</sup>: ```http://.../v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=KGE&simParameterId=grp&obsParameterId=obsvA&obsModuleInstanceId=obs&simModuleInstanceId=mdl```

Example<sup>2</sup>: ```http://.../v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=KGE&simParameterId=grp&obsParameterId=obsvA&obsModuleInstanceId=obs&simModuleInstanceId=mdlA,mdlB```

Example<sup>3</sup>: ```http://.../v1dw/timeseries_calculator?filter=e2019mayMid.eer&calc=PeakValue&simParameterId=grp&simModuleInstanceIds=mdlA,mdlB```