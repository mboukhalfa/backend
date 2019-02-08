from rest_framework import serializers

from mirai.models import IaaSConsumption, IaaS, Container, Log
import uuid
from mirai_project import tasks


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


class ContainerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Container
        fields = ('__all__')

    def create(self, validated_data):
        print(self.context['request'])
        print(validated_data)
        uid = str(uuid.uuid4())
        print(uid)
        
        
        return Container.objects.create(**validated_data)
