from django.contrib import admin
from django.urls import path, include
from . import tasks


urlpatterns = [
    path('admin/', admin.site.urls),

 
    # url(r'^api/environment_cleaner',            views.environment_cleaner, name="environment_cleaner"),

    # url(r'^api/container_add',                  views.container_add, name="container_add"),
    # url(r'^api/container_delete',               views.container_delete, name="container_delete"),
    # url(r'^api/container_migrate',              views.container_migrate, name="container_migrate"),
    # url(r'^api/container_status',               views.container_status, name="container_stats"),

    # url(r'^api/trigger_status',                 views.trigger_status, name="trigger_stats"),
    # url(r'^api/load_network',                   views.load_network, name="load_network"),
    
    # url(r'^api/get-iaas-information',           views.get_general_info_iaas, name="general_info_iaas"),
    # url(r'^api/get-iaas-container',           views.get_detailed_info_iaas, name="detailed_info_iaas"),
    # url(r'^api/get-container-information',           views.get_general_info_container, name="general_info_container"),



    path('', include('mirai.urls')),


]
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]

# run daemons when django starts

tasks.iaas_daemon.delay()
tasks.iaas_consumption.delay()
