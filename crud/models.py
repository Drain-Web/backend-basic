from djongo import models

# ### Create your meta models level 1 here ########################################################################### #
# All meta models have the class Meta with the sole attribute abstract = True
# For some reason, the meta models should also have an ID, despite of us not really using them

isMigrate = False


class Boundary(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    geoDatum = models.CharField(max_length=10, default='WGS 1984')
    projection = models.CharField(max_length=50, default='web_mercator')
    polygon = models.JSONField()
    linecolor = models.CharField(max_length=10, default='#333333')
    lineWidth = models.IntegerField(default=1)
    fillcolor = models.CharField(max_length=10, default='')

    class Meta:
        abstract = isMigrate


class DatetimeDefinition(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    timezone = models.CharField(max_length=3, default="UTC")
    datetimeFormat = models.CharField(max_length=20, default="YYYY-MM-DD HH:mm")

    class Meta:
        abstract = isMigrate


class MapExtent(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    name = models.CharField(max_length=70, null=True)
    top = models.FloatField(default=180.0)
    bottom = models.FloatField(default=-180.0)
    left = models.FloatField(default=-180.0)
    right = models.FloatField(default=180.0)

    class Meta:
        abstract = isMigrate


class Parameter(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # T.obs.mean,
    name = models.CharField(max_length=70)


class SystemInformation(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    name = models.CharField(max_length=50, default='DEFAULT TITLE')

    class Meta:
        abstract = isMigrate


class TimeseriesTimestep(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    unit = models.CharField(max_length=30, default='nonequidistant')

    class Meta:
        abstract = isMigrate


# ### Create your meta models level 2 here ########################################################################### #

class Map(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    # name = models.CharField(max_length=50, null=True)
    geoDatum = models.CharField(max_length=10, default='WGS 1984', null=True)
    projection = models.CharField(max_length=50, default='web_mercator', null=True)
    defaultExtent = models.EmbeddedField(model_container=MapExtent, null=True)

    class Meta:
        abstract = isMigrate


class TimeseriesEvent(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    date = models.CharField(max_length=10, default='YYYY-MM-DD')
    time = models.CharField(max_length=8, default='00:00:00')
    value = models.FloatField()
    flag = models.IntegerField(default=0)

    class Meta:
        abstract = isMigrate


class TimeseriesHeader(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    units = models.CharField(max_length=10, default='')
    missVal = models.FloatField()
    type = models.CharField(max_length=20, default='')
    parameterId = models.CharField(max_length=20, default='')
    stationName = models.CharField(max_length=20, default='')
    timeStep = models.EmbeddedField(model_container=TimeseriesTimestep, null=True)

    class Meta:
        abstract = isMigrate


# ### Create your models here ######################################################################################## #

class Filter(models.Model):
    id = models.IntegerField(default=1, primary_key=True)
    name = models.CharField(max_length=70, default='')
    mapExtent = models.EmbeddedField(model_container=MapExtent)
    boundary = models.EmbeddedField(model_container=Boundary, null=True)


class Location(models.Model):
    name = models.CharField(max_length=70, default='')
    x = models.FloatField()
    y = models.FloatField()


class LocationSets(models.Model):
    name = models.CharField(max_length=70, default='')


class Region(models.Model):
    # name = models.CharField(max_length=70, default='')
    systemInformation = models.EmbeddedField(model_container=SystemInformation)
    datetime = models.EmbeddedField(model_container=DatetimeDefinition)
    map = models.EmbeddedField(model_container=Map, null=True)


class Timeseries(models.Model):
    name = models.CharField(max_length=70, default='')
    header = models.EmbeddedField(model_container=TimeseriesHeader)
    events = models.ArrayField(model_container=TimeseriesEvent)
