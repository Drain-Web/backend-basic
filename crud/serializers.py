from rest_framework import serializers
from crud.models import Boundary, DatetimeDefinition, Filter, Location, Map, MapExtent, Region, SystemInformation
from crud.models import Timeseries, TimeseriesEvent, TimeseriesTimestep


class BoundarySerializer(serializers.ModelSerializer):
    polygon = serializers.JSONField()

    class Meta:
        model = Boundary
        fields = ('polygon', 'geoDatum', 'projection', 'linecolor', 'lineWidth', 'fillcolor')


class DatetimeDefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DatetimeDefinition
        fields = '__all__'


class MapExtentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MapExtent
        fields = ('name', 'top', 'bottom', 'left', 'right')


class FilterListItemSerializer(serializers.ModelSerializer):
    """
    Filter element returned by listing of filters.
    Does not hold the large field 'boundary'.
    """

    id = serializers.CharField()
    description = serializers.CharField()
    mapExtent = MapExtentSerializer(many=False)

    class Meta:
        model = Filter
        fields = ('id', 'description', 'mapExtent')


class FilterSerializer(serializers.ModelSerializer):
    """
    Filter element returned by single-element search.
    """
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
    """
    Used internally by the TimeseriesDatafullSerializer.
    """
    date = serializers.CharField()
    time = serializers.CharField()
    value = serializers.FloatField()
    flag = serializers.IntegerField()

    class Meta:
        model = TimeseriesEvent
        fields = ('date', 'time', 'value', 'flag')


class TimeseriesSerializerBase(serializers.ModelSerializer):
    """
    Parent class of the serializers effectivelly used.
    """

    def get_header(self, obj):
        return {
            "units": obj.header_units,
            "missVal": obj.header_missVal,
            "type": obj.header_type,
            "parameterId": obj.header_parameterId,
            "stationName": obj.header_stationName,
            "location_id": obj.header_location_id,
            "timeStep": {
                "unit": obj.header_timeStep_unit,
            }
        }


class TimeseriesDatalessSerializer(TimeseriesSerializerBase):
    """
    Only the header of the timeseries. No data. For extensive listing.
    """
    header = serializers.SerializerMethodField('get_header')

    class Meta:
        model = Timeseries
        fields = ('id', 'header')


class TimeseriesDatafullSerializer(TimeseriesSerializerBase):
    """
    Both the header and the data of the timeseries. For restricted listing.
    """
    header = serializers.SerializerMethodField('get_header')
    events = TimeseriesEventSerializer(many=True)

    class Meta:
        model = Timeseries
        fields = ('id', 'header', 'events')
