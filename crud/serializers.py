from rest_framework import serializers
from crud.models import Location, Filter, Region, SystemInformation


class FilterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Filter
        fields = ('id', 'name', 'mapExtent', 'boundary')


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ('name', 'x', 'y')


class SystemInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemInformation
        fields = ('name', )


class RegionSerializer(serializers.ModelSerializer):
    # systemInformation = SystemInformationSerializer(many=False)

    class Meta:
        model = Region
        fields = ('systemInformation', 'datetime', 'map')
