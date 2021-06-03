from rest_framework import serializers
from crud.models import Boundary, DatetimeDefinition, Filter, Location, Map, MapExtent, Region, SystemInformation
from crud.models import Timeseries, TimeseriesEvent, TimeseriesTimestep


class BoundarySerializer(serializers.ModelSerializer):
    polygon = serializers.JSONField()

    class Meta:
        model = Boundary
        fields = '__all__'


class DatetimeDefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DatetimeDefinition
        fields = '__all__'


class MapExtentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MapExtent
        fields = '__all__'


class FilterSerializer(serializers.ModelSerializer):
    mapExtent = MapExtentSerializer(many=False)
    boundary = BoundarySerializer(many=False)

    class Meta:
        model = Filter
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'


class MapSerializer(serializers.ModelSerializer):
    defaultExtent = MapExtentSerializer(many=False)

    class Meta:
        model = Map
        fields = '__all__'


# ## REGION ########################################################################################################## #

class SystemInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemInformation
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    systemInformation = SystemInformationSerializer(many=False)
    datetime = DatetimeDefinitionSerializer(many=False)
    map = MapSerializer(many=False)

    class Meta:
        model = Region
        fields = '__all__'

# ## TIMESERIES ###################################################################################################### #

class TimeseriesEventSerializer(serializers.ModelSerializer):
    date = serializers.CharField()
    time = serializers.CharField()
    value = serializers.FloatField()
    flag = serializers.IntegerField()

    class Meta:
        model = TimeseriesEvent
        fields = ('date', 'time', 'value', 'flag')


class TimeseriesTimestepSerializer(serializers.ModelSerializer):
    unit = serializers.CharField()

    class Meta:
        model = TimeseriesTimestep
        fields = ('unit', )

'''
class TimeseriesHeaderSerializer(serializers.ModelSerializer):
    timeStep = TimeseriesTimestepSerializer(many=False)
    units = serializers.CharField()
    missVal = serializers.FloatField()
    type = serializers.CharField()
    parameterId = serializers.CharField()
    stationName = serializers.CharField()

    class Meta:
        model = TimeseriesHeader
        fields = ('timeStep', 'units', 'missVal', 'type', 'parameterId', 'stationName')
'''


class TimeseriesSerializer(serializers.ModelSerializer):
    # TODO: replace by function
    # TODO: e.g. https://stackoverflow.com/questions/22958058/how-to-change-field-name-in-django-rest-framework
    # header = TimeseriesHeaderSerializer(many=False)

    events = TimeseriesEventSerializer(many=True)

    class Meta:
        model = Timeseries
        fields = '__all__'
