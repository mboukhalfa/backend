from mirai.models import Log
from mirai.models import Triggers
from mirai.models import IaaS
from mirai.models import Container
from mirai.models import Client
import datetime
import random
from netaddr import IPNetwork


def get_ip_port_sdn_network():
    ip_list = IPNetwork("172.16.207.0/24")
    ip_iteration = 0
    ip_address = ""
    while ip_iteration == 0:
        ip_list = list(ip_list)
        # first, second and last addresses need to be avoided as the first one is the network address, the second is the
        # Ansible ports and the third is the broadcast address
        ip_list = ip_list[2:-1]
        random.shuffle(ip_list)
        ip_address = random.choice(ip_list).format()
        if Container.objects.filter(ip_address=ip_address).count() == 0:
            ip_iteration = 1
    return ip_address, ip_address.split(".")[3]


def add_entry_ip_ports(container_id):
    ip_address, port_number = get_ip_port_sdn_network()
    process = Container.objects.get(pk=container_id)
    process.ip_address = ip_address
    process.port = port_number
    process.save()
    return process.container_name, process.ram, process.cpu, process.iaas, process.application_type, process.ip_address\
        , process.port


def store_db_log(id, result):
    process = Log.objects.get(pk=id)
    process.result = result
    process.save()
    return process.usage


def tracking_iaas_container(container_id, iaas):
    process = Log.objects.get(pk=container_id)
    process.iaas = iaas
    process.save()
    return process.iaas


def name_control(container_name):
    for entry in Log.objects.all():
        if entry.server_name == container_name and entry.usage == "1":
            return False
    return True


def add_vxlan_ip_ports(container_name):
    ip_address, port_number = get_ip_port_sdn_network()
    x = IpsPorts(ip_address=str(ip_address), container_name=str(
        container_name), port=int(port_number))
    x.save()
    return port_number


def insert_entry_client(container_name):
    ip_address, port_number = get_ip_port_sdn_network()
    x = Client(container=container_name, container_name=container_name + "-client", ip_address=ip_address,
               port=port_number)
    x.save()
    return x.container_name, x.ip_address, x.port


def insert_entry(container_name, result, code, usage):
    x = Log(container=container_name, result=result, code=code, usage=usage)
    x.save()
    return x.pk


def matching(container_name):
    x = Log.objects.filter(server_name=container_name).first()
    return x.client_name


def matching_ip(container_name):
    x = IpsPorts.objects.filter(container_name=container_name).first()
    return x.ip_address


def get_overlay_port(interface_name):
    x = IpsPorts.objects.filter(container_name=interface_name).first()
    return x.port


def get_intent_priority(container_name):
    priority = 200
    for entry in Log.objects.all():
        if entry.server_name == container_name and entry.code == "002":
            priority += 200
    return priority


def match_containers_iaas(container_name):
    x = Log.objects.filter(server_name=container_name).last()
    return x.iaas


'''
helper related to the Triggers
'''


def insert_entry_triggers(container_name, iaas_name, trigger_type, trigger_action, trigger_time, trigger_result):
    x = Triggers(container_name=container_name, iaas_name=iaas_name, trigger_type=trigger_type,
                 trigger_action=trigger_action, trigger_time=trigger_time, trigger_result=trigger_result)
    x.save()
    return x.pk


def update_initial_trigger_entry(container_name, iaas_name, trigger_action, trigger_result):
    process = Triggers.objects.filter(trigger_action="api_call").last()
    process.container_name = container_name
    process.iaas_name = iaas_name
    process.trigger_action = trigger_action
    process.trigger_result = trigger_result
    process.save()


def update_triggers_entry(id, trigger_result):
    process = Triggers.objects.get(pk=id)
    process.trigger_result = trigger_result
    process.save()


'''
helper related to the IaaS discovery
'''


def available_iaas():
    tab = {}
    for entry in IaaS.objects.all():
        if entry.iaas_state == "DOWN" and entry.iaas_configuration == "DOWN":
            tab[entry.id] = entry.iaas_ip
    return tab


def update_after_failure(ip_address, state, configuration):
    for entry in IaaS.objects.all():
        if entry.iaas_ip == ip_address:
            entry.iaas_state = state
            entry.iaas_configuration = configuration
            entry.iaas_date_configuration = datetime.datetime.now()
            entry.save()


def update_state_iaas(ip_address, state):
    for entry in IaaS.objects.all():
        if entry.iaas_ip == ip_address:
            entry.iaas_state = state
            entry.save()


def update_configuration_iaas(ip_address, state):
    for entry in IaaS.objects.all():
        if entry.iaas_ip == ip_address:
            entry.iaas_configuration = state
            entry.save()


def verify_infinite_handler(ip_address):
    for entry in IaaS.objects.all():
        if entry.iaas_ip == ip_address and entry.iaas_state == "DOWN" and entry.iaas_configuration == "DOWN":
            return True
    return False


def number_minions():
    number_minion = 0
    for entry in IaaS.objects.all():
        if entry.iaas_state == "UP" and entry.iaas_configuration == "UP":
            number_minion += 1
    return number_minion


def match_iaas_name_ip(iaas_name):
    for entry in IaaS.objects.all():
        if entry.iaas_name == iaas_name:
            return entry.iaas_ip
    return "Error"
