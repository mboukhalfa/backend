from django.urls import path, include
from mirai import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r'iaas', views.IaasViewSet)
router.register(r'container', views.ContainerViewSet, base_name='iaas-container')

iaas_router = routers.NestedSimpleRouter(router, r'iaas', lookup='iaas')
iaas_router.register(r'resource-consumption', views.IaasResourceConsumptionViewSet, base_name='iaas-resource-consumption')
# iaas_router.register(r'container', views.ContainerViewSet, base_name='iaas-container')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(iaas_router.urls)),
    path('env-status/', views.EnvStatus.as_view(), name="env_status"),
]
