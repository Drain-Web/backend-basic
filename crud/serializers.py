from rest_framework import serializers
from crud.models import Region, SystemInformation

class SystemInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemInformation
        fields = ('name', )
        abstract=True


class RegionSerializer(serializers.ModelSerializer):
    # systemInformation = SystemInformationSerializer(many=False)

    class Meta:
        model = Region
        fields = ('systemInformation',
                  'datetime')
