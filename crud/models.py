from djongo import models

# ### Overall notes ################################################################################################## #

# Attributes are named in camelCase by default (following Delft-FEWS pattern).
# When an attribute has a underline, it is expected to be changed in the Serializer.
# e.g. field_someThing = models.IntegerField(...) should be output as field = {someThing: models.IntegerField(...)}


# ### Create your meta models level 1 here ########################################################################### #

# All meta models have the class Meta with the sole attribute abstract = True
# For some reason, the meta models should also have an ID, despite of us not really using them

DEFAULT_GEODATUM = "WGS 1984"
DEFAULT_PROJECTION = "web_mercator"


class Boundary(models.Model):
    id = models.CharField(max_length=10, primary_key=True)  # geoFilterId
    name = models.CharField(max_length=20, null=False)
    geoDatum = models.CharField(max_length=10, default=DEFAULT_GEODATUM)
    projection = models.CharField(max_length=50, default=DEFAULT_PROJECTION)
    polygon = models.JSONField()
    lineColor = models.CharField(max_length=10, default='#333333')
    lineWidth = models.IntegerField(default=1)
    fillColor = models.CharField(max_length=10, default=None, null=True)


class DatetimeDefinition(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    timezone = models.CharField(max_length=3, default="UTC")
    datetimeFormat = models.CharField(max_length=20, default="YYYY-MM-DD HH:mm")


class Parameter(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # T.obs.mean,
    name = models.CharField(max_length=70)


class SystemInformation(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    name = models.CharField(max_length=50, default='DEFAULT TITLE')


class TimeseriesTimestep(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    unit = models.CharField(max_length=30, default='nonequidistant')


class LocationAttribute(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30, null=False)
    number = models.FloatField(null=True)
    text = models.CharField(max_length=100, null=True)


class LocationRelation(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    labelId = models.CharField(max_length=20, null=False,
                               choices=(('UPSTREAM', 'DOWNSTREAM'), 
                                        ('UPSTREAM', 'DOWNSTREAM')))
    relatedLocationId = models.CharField(max_length=100, null=False)


# ### Create your meta models level 2 here ########################################################################### #

class Location(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=70, default='')
    x = models.FloatField()
    y = models.FloatField()
    relations = models.ArrayField(model_container=LocationRelation)
    attributes = models.ArrayField(model_container=LocationAttribute)
    polygon = models.JSONField(null=True)
    polygonDescription = models.CharField(max_length=200, null=True)


class Map(models.Model):
    id = models.CharField(max_length=10, primary_key=True)  # geoFilterId
    geoDatum = models.CharField(max_length=10, default=DEFAULT_GEODATUM, null=True)
    projection = models.CharField(max_length=50, default=DEFAULT_PROJECTION, null=True)

    # defaultExtent: {...} in the Serializer
    defaultExtent_top = models.FloatField(default=180.0, null=True)
    defaultExtent_bottom = models.FloatField(default=-180.0, null=True)
    defaultExtent_left = models.FloatField(default=-180.0, null=True)
    defaultExtent_right = models.FloatField(default=180.0, null=True)


class TimeseriesEvent(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    date = models.CharField(max_length=10, default='YYYY-MM-DD')
    time = models.CharField(max_length=8, default='00:00:00')
    value = models.FloatField()
    flag = models.IntegerField(default=0)


class LevelThresholdValue(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    levelThresholdId = models.CharField(max_length=30, null=False)  # TODO - link it properly
    valueFunction = models.CharField(max_length=30, null=False)


class ThresholdWarningLevel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    color = models.CharField(max_length=10, null=False)
    iconName = models.CharField(max_length=30, null=True)


class ThresholdGroup(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30, null=False)


class ThresholdValueSet(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=30, null=False)
    levelThresholdValues = models.ManyToManyField(LevelThresholdValue)


class LevelThreshold(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30, default=False)
    shortName = models.CharField(max_length=15, default=False)
    upWarningLevelId = models.ForeignKey(to=ThresholdWarningLevel, on_delete=models.CASCADE, null=False)
    # thresholdGroup = models.ForeignKey(to=ThresholdGroup, on_delete=models.CASCADE, null=False)
    thresholdGroup = models.ManyToManyField(ThresholdGroup)


# ### Create your models here ######################################################################################## #

class Filter(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=100, default='')
    map = models.ForeignKey(Map, on_delete=models.CASCADE, null=False)
    boundary = models.ForeignKey(Boundary, on_delete=models.CASCADE, null=False)


class LocationSet(models.Model):
    name = models.CharField(max_length=70, default='')


class ModuleInstance(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)


class Region(models.Model):
    # derived from SystemConfigFiles/Explorer.xml
    systemInformation = models.EmbeddedField(model_container=SystemInformation)
    datetime = models.EmbeddedField(model_container=DatetimeDefinition)
    map = models.ForeignKey(Map, on_delete=models.SET_NULL, null=True)
    defaultFilter = models.ForeignKey(Filter, on_delete=models.SET_NULL, null=True)


class ParameterGroup(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    parameterType = models.CharField(
        max_length=20,
        choices=(('accumulative', 'Accumulative'),
                 ('instantaneous', 'Instantaneous')))
    unit = models.CharField(max_length=30, default='dimensionless')
    displayUnit = models.CharField(max_length=10, default='')
    valueResolution = models.FloatField()
    usesDatum = models.BooleanField(default=False)


class TimeseriesParameter(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100, default='')
    shortName = models.CharField(max_length=50, default='')
    parameterGroup = models.ForeignKey(ParameterGroup, on_delete=models.CASCADE, null=False)


class Timeseries(models.Model):
    id = models.AutoField(primary_key=True)

    # header: {...} in the Serializer
    header_units = models.CharField(max_length=10, default='')
    header_missVal = models.FloatField()
    header_type = models.CharField(max_length=20, default='')
    header_moduleInstanceId = models.CharField(max_length=50, default='')
    header_parameterId = models.ForeignKey(TimeseriesParameter, on_delete=models.CASCADE, null=True)
    header_stationName = models.CharField(max_length=20, default='')
    header_location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    header_timeStep_unit = models.CharField(max_length=10, default='')

    # external references
    events = models.ArrayField(model_container=TimeseriesEvent)
    filter_set = models.ManyToManyField(Filter)
    thresholdValueSets = models.ManyToManyField(ThresholdValueSet)
