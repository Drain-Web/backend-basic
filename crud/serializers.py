from rest_framework import serializers
from crud.models import Boundary, DatetimeDefinition, Filter, Location, Map, ParameterGroup, Region, SystemInformation
from crud.models import Timeseries, TimeseriesEvent, TimeseriesTimestep, TimeseriesParameter, LocationRelation
from crud.models import ThresholdGroup, ThresholdValueSet, LevelThreshold, LevelThresholdValue, ThresholdWarningLevel
from crud.models import LocationAttribute, ModuleInstance


# ## GENERAL ######################################################################################################### #

class DatetimeDefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DatetimeDefinition
        fields = ('timezone', 'datetimeFormat')


class ModuleInstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModuleInstance
        fields = ('id', 'name', 'description')


# ## LOCATION ######################################################################################################## #

class LocationRelationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_label_id')

    class Meta:
        model = LocationRelation
        fields = ('id', 'relatedLocationId')

    def get_label_id(self, obj):
        return obj["labelId"]


class LocationSerializer(serializers.ModelSerializer):
    locationId = serializers.SerializerMethodField('get_location_id')
    shortName = serializers.SerializerMethodField('get_location_name')
    relations = LocationRelationSerializer(many=True)

    class Meta:
        model = Location
        fields = ('locationId', 'shortName', 'relations', 'x', 'y')

    def get_location_id(self, obj):
        return obj.id

    def get_location_name(self, obj):
        return obj.name


class LocationAttributeSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    name = serializers.CharField()
    text = serializers.CharField()
    number = serializers.CharField()

    class Meta:
        model = LocationAttribute
        fields = ('id', 'name', 'text', 'number')


class LocationWithAttrSerializer(serializers.ModelSerializer):
    locationId = serializers.SerializerMethodField('get_location_id')
    shortName = serializers.SerializerMethodField('get_location_name')
    relations = LocationRelationSerializer(many=True)
    attributes = LocationAttributeSerializer(many=True)

    class Meta:
        model = Location
        fields = ('locationId', 'shortName', 'relations', 'x', 'y', 'attributes')

    def get_location_id(self, obj):
        return obj.id

    def get_location_name(self, obj):
        return obj.name


class LocationDynamicSerializer(serializers.ModelSerializer):
    locationId = serializers.SerializerMethodField('get_location_id')
    shortName = serializers.SerializerMethodField('get_location_name')
    relations = LocationRelationSerializer(many=True)
    attributes = LocationAttributeSerializer(many=True)

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(LocationDynamicSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Location
        fields = '__all__'

    def get_location_id(self, obj):
        return obj.id

    def get_location_name(self, obj):
        return obj.name


# ## BOUNDARY ######################################################################################################## #

class BoundarySerializer(serializers.ModelSerializer):
    polygon = serializers.JSONField()

    class Meta:
        model = Boundary
        fields = ('id', 'polygon', 'geoDatum', 'projection', 'lineColor', 'lineWidth', 'fillColor')


class BoundarySerializerNoId(serializers.ModelSerializer):
    polygon = serializers.JSONField()

    class Meta:
        model = Boundary
        fields = ('polygon', 'geoDatum', 'projection', 'lineColor', 'lineWidth', 'fillColor')


# ## MAP ############################################################################################################# #

class MapSerializer(serializers.ModelSerializer):

    defaultExtent = serializers.SerializerMethodField('get_default_extent')

    class Meta:
        model = Map
        fields = ('id', 'defaultExtent', 'geoDatum', 'projection')

    def get_default_extent(self, obj):
        return {
            "left": obj.defaultExtent_left,
            "right": obj.defaultExtent_right,
            "top": obj.defaultExtent_top,
            "bottom": obj.defaultExtent_bottom
        }


class MapSerializerNoId(serializers.ModelSerializer):

    defaultExtent = serializers.SerializerMethodField('get_default_extent')

    class Meta:
        model = Map
        fields = ('defaultExtent', 'geoDatum', 'projection')

    def get_default_extent(self, obj):
        return {
            "left": obj.defaultExtent_left,
            "right": obj.defaultExtent_right,
            "top": obj.defaultExtent_top,
            "bottom": obj.defaultExtent_bottom
        }


# ## FILTER ########################################################################################################## #

class FilterSerializer(serializers.ModelSerializer):
    """
    Filter element returned by single-element search.
    """

    id = serializers.CharField()
    description = serializers.CharField()
    map = MapSerializerNoId(many=False)
    boundary = BoundarySerializerNoId(many=False)

    class Meta:
        model = Filter
        fields = '__all__'
        fields = ('id', 'description', 'map', 'boundary')


class FilterListItemSerializer(serializers.ModelSerializer):
    """
    Filter element returned by listing of filters.
    Does not hold the large field 'boundary'.
    """

    id = serializers.CharField()
    description = serializers.CharField()
    map = MapSerializerNoId(many=False)

    class Meta:
        model = Filter
        fields = ('id', 'description', 'map')


# ## REGION ########################################################################################################## #

class SystemInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemInformation
        fields = ('name', )


class RegionSerializer(serializers.ModelSerializer):
    systemInformation = SystemInformationSerializer(many=False)
    datetime = DatetimeDefinitionSerializer(many=False)
    map = MapSerializerNoId(many=False)
    defaultFilter = serializers.SerializerMethodField('get_default_filter_id')

    class Meta:
        model = Region
        fields = ("systemInformation", "datetime", "map", "defaultFilter")

    def get_default_filter_id(self, obj):
        return obj.defaultFilter_id


# ## THRESHOLDS ###################################################################################################### #

class ThresholdGroupSerializer(serializers.ModelSerializer):
    """

    """
    id = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = ThresholdGroup
        fields = ("id", "name")


class ThresholdWarningLevelSerializer(serializers.ModelSerializer):
    """
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    color = serializers.CharField()
    iconName = serializers.CharField()

    class Meta:
        model = ThresholdWarningLevel
        fields = ('id', 'name', 'color', 'iconName')


class LevelThresholdSerializer(serializers.ModelSerializer):
    """

    """

    id = serializers.CharField()
    name = serializers.CharField()
    shortName = serializers.CharField()
    upWarningLevelId = ThresholdWarningLevelSerializer(read_only=True, many=False)
    thresholdGroup = ThresholdGroupSerializer(read_only=True, many=True)

    class Meta:
        model = LevelThreshold
        fields = ('id', 'name', 'shortName', 'upWarningLevelId', 'thresholdGroup')



class LevelThresholdValueSerializer(serializers.ModelSerializer):
    """

    """

    levelThresholdId = serializers.CharField()
    valueFunction = serializers.CharField()

    class Meta:
        model = LevelThresholdValue
        fields = ('levelThresholdId', 'valueFunction')


class ThresholdValueSetSerializer(serializers.ModelSerializer):
    """
    """
    id = serializers.CharField()
    name = serializers.CharField()
    levelThresholdValues = LevelThresholdValueSerializer(read_only=True, many=True)

    class Meta:
        model = ThresholdValueSet
        fields = ("id", "name", "levelThresholdValues")


# ## TIMESERIES ###################################################################################################### #

class ParameterGroupSerializer(serializers.ModelSerializer):
    """
    """

    class Meta:
        model = ParameterGroup
        fields = ("id", "parameterType", "unit", "displayUnit", "valueResolution", "usesDatum")


class TimeseriesParameterSerializer(serializers.ModelSerializer):
    """

    """

    id = serializers.CharField()
    name = serializers.CharField()
    shortName = serializers.CharField()
    parameterGroup = serializers.SerializerMethodField('get_parameter_group_id')

    class Meta:
        model = TimeseriesParameter
        fields = ('id', 'name', 'shortName', 'parameterGroup')

    def get_parameter_group_id(self, obj):
        return obj.parameterGroup.id


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
            "parameterId": obj.header_parameterId.id,
            "moduleInstanceId": obj.header_moduleInstanceId,
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
    thresholdValueSets = ThresholdValueSetSerializer(read_only=True, many=True)

    class Meta:
        model = Timeseries
        fields = ('id', 'header', 'thresholdValueSets')


class TimeseriesDatafullSerializer(TimeseriesSerializerBase):
    """
    Both the header and the data of the timeseries. For restricted listing.
    """
    header = serializers.SerializerMethodField('get_header')
    events = TimeseriesEventSerializer(many=True)
    thresholdValueSets = ThresholdValueSetSerializer(read_only=True, many=True)

    class Meta:
        model = Timeseries
        fields = ('id', 'header', 'events', 'thresholdValueSets')


class TimeseriesWithFiltersSerializer(TimeseriesSerializerBase):
    """

    """
    header = serializers.SerializerMethodField('get_header')
    filter_set = FilterListItemSerializer(read_only=True, many=True)

    class Meta:
        model = Timeseries
        fields = ('id', 'header', 'filter_set')
