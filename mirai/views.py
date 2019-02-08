from dsmirai.persistent_model import dashboard_helper

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from mirai_project import tasks

from mirai.permissions import IsOwner
from mirai.models import IaaS, IaaSConsumption, Container, Log # TODO

from mirai.serializers import (IaaSSerializer,
                               EnvStatusSerializer,
                               IaasResourceConsumptionSerializer,
                               ContainerSerializer)


class Test(APIView):

    def get(self, request, format=None):
        # Log.objects.create(server_name = "fayrouz",result = "test",code = "test",client_name = "test",token = "test",usage = "test")
        tasks.lxc_creation.delay()
        return Response({"status": "success"})
    

class EnvStatus(APIView):
    """
    The dashboard page where various information on the infrastructure are displayed
    """

    def get_object(self):

        env_status = {
            "online_iaas": dashboard_helper.get_online_iaas(),
            "total_iaas": dashboard_helper.get_total_iaas(),
            "online_container": dashboard_helper.get_online_container(),
        }

        # TODO delete this when the env worked
        env_status = {
            "online_iaas": 3,
            "total_iaas": 3,
            "online_container": 3,
        }
        return env_status

    def get(self, request, format=None):
        env_status = self.get_object()
        serializer = EnvStatusSerializer(env_status)
        return Response(serializer.data)


class IaasResourceConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    The resource consumption of an IaaS
    """

    def get_queryset(self):
        return IaaSConsumption.objects.filter(iaas__iaas_owner=self.request.user, iaas=self.kwargs['iaas_pk'])
    queryset = IaaSConsumption.objects.none()
    serializer_class = IaasResourceConsumptionSerializer


class IaasViewSet(viewsets.ModelViewSet):
    """
    CRUD IaaS
    """
    def get_queryset(self):
        return IaaS.objects.filter(iaas_owner=self.request.user)
    queryset = IaaS.objects.none()
    serializer_class = IaaSSerializer
    permission_classes = (IsOwner,)

    def perform_create(self, serializer):
        serializer.save(iaas_owner=self.request.user)


class ContainerViewSet(viewsets.ModelViewSet):
    """
    CRUD Container
    """
    def get_queryset(self):
        return Container.objects.filter(iaas_name__iaas_owner=self.request.user)#, iaas=self.kwargs['iaas_pk'])
    queryset = Container.objects.none()
    serializer_class = ContainerSerializer
