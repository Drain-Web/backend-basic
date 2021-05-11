from rest_framework import serializers
from crud.models import Boundary, DatetimeDefinition, Filter, Location, Map, MapExtent, Region, SystemInformation

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
