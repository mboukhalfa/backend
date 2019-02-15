from rest_framework import serializers

from mirai.models import IaaSConsumption, IaaS, Container
import uuid
from mirai import tasks


class EnvStatusSerializer(serializers.Serializer):

    online_iaas = serializers.IntegerField(read_only=True)
    total_iaas = serializers.IntegerField(read_only=True)
    online_container = serializers.IntegerField(read_only=True)


class IaasResourceConsumptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = IaaSConsumption
        fields = ('__all__')


class IaaSSerializer(serializers.ModelSerializer):
    iaas_owner = serializers.ReadOnlyField(source='iaas_owner.username')

    class Meta:
        model = IaaS
        fields = ('__all__')
        read_only_fields = ('iaas_state',
                    'iaas_configuration',
                    'iaas_date_discovery',
                    'iaas_date_configuration')
        


class ContainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Container
        fields = ('__all__')
        read_only_fields = ('ip_address','port',)