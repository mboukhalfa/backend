from mirai.models import Log
from mirai.models import Triggers
from mirai.models import IaaS
from mirai.models import IaaSConsumption
import time
import dsmirai.client_broker as client_broker
import random
import numpy as np
import datetime


orchestrator_ip = "195.148.125.104"


def get_online_iaas():
    online_iaas = 0
    for entry in IaaS.objects.all():
        if entry.iaas_state == "UP" and entry.iaas_configuration == "UP":
            online_iaas += 1
    return online_iaas


def get_total_iaas():
    return len(IaaS.objects.all())


def get_online_container():
    online_container = 0
    for entry in Log.objects.all():
        if entry.code == "001":
            online_container += 1
    return online_container


def get_containers_by_iaas(iaas_name=None):
    containers_list = []
    for entry in Log.objects.all():
        if Log.objects.filter(server_name=entry.server_name).last().pk == entry.pk:
            if iaas_name is None:
                containers_list.append(entry)
            if entry.iaas == iaas_name:
                containers_list.append(entry.server_name)
    return containers_list


def get_iaas_information(iaas_name, iaas_owner):
    iaas_information = {}
    for entry in IaaS.objects.all():
        if entry.iaas_name == iaas_name:
            iaas_information['IaaS name'] = iaas_name
            iaas_information['IaaS ip'] = entry.iaas_ip
            x, y = get_iaas_resources(entry.iaas_name, "cpu", iaas_owner)
            iaas_information['graphCPU'] = [{'x': x, 'y': y[0], 'name': 'CPU'}]
            data = []
            x, y = get_iaas_resources(entry.iaas_name, "ram", iaas_owner)
            data.append({'x': x, 'y': y[0], 'name': 'RAM'})
            x, y = get_iaas_resources(entry.iaas_name, "disk", iaas_owner)
            data.append({'x': x, 'y': y[0], 'name': 'DISK'})
            iaas_information['graphDisk - RAM'] = data
            iaas_information['number of running container'] = len(get_containers_by_iaas(entry.iaas_name))
    return iaas_information


def container_application_type(container_name):
    return Log.objects.filter(server_name=container_name).last().application_type


def container_dashboard_resources(container_name, iaas_name):
    print(random.random)
    rmq = client_broker.ClientBroker("iaas_consumption_queue")
    iaas_ip = IaaS.objects.filter(iaas_name=iaas_name).first().iaas_ip
    return rmq.container_dashboard_resources(container_name, iaas_ip)


def container_video_url(container_name):
    return "http://{}:{}".format(orchestrator_ip, int(IpsPorts.objects.filter(container_name=Log.objects.filter(
        server_name=container_name).first().client_name).first().port) + 1024)


def get_iaas_list():
    iaas_list = []
    for entry in IaaS.objects.all():
        if entry.iaas_state == "UP" and entry.iaas_configuration == "UP":
            iaas_list.append({'id': entry.pk, 'name': entry.iaas_name})
    return iaas_list


def get_trigger_events():
    trigger_events = []
    for entry in Triggers.objects.all():
        trigger_events.append({'id': entry.pk, 'type': entry.trigger_type, 'source_iaas': entry.iaas_name,
                               'date': entry.trigger_time, 'containers': entry.container_name})
    return trigger_events


# Dashboard_Resource_Consumption
def get_iaas_ip_match(ip_address):
    for entry in IaaS.objects.all():
        if entry.iaas_ip == ip_address:
            return entry.iaas_name


def get_iaas_id_match(id_iaas):
    for entry in IaaS.objects.all():
        print(entry.pk)
        print(type(entry.pk))
        print(id_iaas)
        print(type(id_iaas))
        if str(entry.pk) == str(id_iaas):
            return entry.iaas_ip


def insert_entry_iaas_consumption(iaas_name, iaas_cpu, iaas_ram, iaas_disk, iaas_time):
    x = IaaSConsumption(iaas_name=iaas_name, iaas_cpu=iaas_cpu, iaas_ram=iaas_ram, iaas_disk=iaas_disk,
                        iaas_time=iaas_time)
    x.save()
    return x.pk


def iaas_resource_consumption():
    print(random.random)
    queue_name = "iaas_consumption_queue"
    rmq = client_broker.ClientBroker(queue_name)
    while True:
        table_statistics = rmq.verify_resource_creation("star" + queue_name.split['_'][0])
        for i in range(len(table_statistics)):
            iaas_name = get_iaas_ip_match(str(table_statistics[i][0]))
            insert_entry_iaas_consumption(iaas_name, table_statistics[i][1], table_statistics[i][2],
                                          table_statistics[i][3], datetime.datetime.now())
        time.sleep(30)


def get_iaas_resources(iaas_name, resource_type, user_id):
    values_range = []

    if iaas_name != "all":
        values_range.append(list(IaaSConsumption.objects.values_list('iaas_{}'.format(resource_type), flat=True).
                                 filter(iaas_name=iaas_name))[-20:])
        time_range = list(IaaSConsumption.objects.values_list('iaas_time', flat=True).filter(iaas_name=iaas_name))
    else:
        for iaas in IaaS.objects.filter(iaas_owner=user_id):
            values_range.append(list(IaaSConsumption.objects.values_list('iaas_{}'.format(resource_type), flat=True).
                                     filter(iaas_name=iaas.iaas_name))[-20:])
        time_range = list(IaaSConsumption.objects.values_list('iaas_time', flat=True).filter(iaas_name=IaaS.
                                                                                             objects.all().
                                                                                             last().iaas_name))

    for i in range(len(time_range)):
        time_range[i] = "{:02}:{:02}:{:02}".format(time_range[i].hour, time_range[i].minute, time_range[i].second)

    if resource_type != "cpu":
        for i in range(len(values_range)):
            values_range[i] = np.array(values_range[i]) / 1000
            values_range[i] = values_range[i].tolist()

    time_range = time_range[-20:]

    return time_range, values_range


def get_iaas_managment_console(iaas_owner):
    iaas_list = []
    for entry in IaaS.objects.all():
        if entry.iaas_owner == iaas_owner:
            iaas_list.append(entry.iaas_name)
    return iaas_list
