import dsmirai.client_broker as client_broker
import dsmirai.intent_based_networking as intent_based_networking
from operator import itemgetter
from dsmirai.persistent_model import helpers
from dsmirai.persistent_model import dashboard_helper
import dsmirai.video_streaming_handler as vsh
from mirai.models import Log
from django.conf import settings

"""
Code communication:

1/-1 = created/not created
2 = resources not available
3 = race condition
"""
CREATED = 1
NOT_CREATED = -1
RESOURCE_ERR = 2
RACE = 3 

def create(container_name, client, cpu, ram, container_placement="None",
           application_type="video"):

    rmq = client_broker.ClientBroker("creation_queue")
    intents = intent_based_networking.IntentBasedNetworking()
    id_request = helpers.insert_entry(
        container_name, "None", "001", client, token1, "1", "None")

    if container_placement == "None":
        table_statistics = rmq.verify_resource_creation()
    else:
        table_statistics = rmq.verify_resource_directive(ip_address)
    winner_minion = max(table_statistics, key=itemgetter(1, 2, 3))
    # TODO: I think it will be better if we used only M as unit (in interface we can convert)
    if 'M' in ram:
        int_ram = ram.split('M')[0]
    else:
        int_ram = ram.split('G')[0]
    if winner_minion[1] < int(cpu) and winner_minion[2] < int(int_ram):
        print("***********The Global Orchestrator***********")
        print("Resources issues")

        # TODO: Please check this loop !
        while helpers.store_db_log(id_request, "3", "0", "None") != "0":
            print("DB not yet updated")
        return "Error" # TODO: Check Code on top 
    creation_ip_address = winner_minion[0]

    server_port_number, server_ip_address = helpers.add_entry_ip_ports(
        container_name)

    client_port_number, client_ip_address = helpers.add_entry_ip_ports(
        client)
    result = 0
    if rmq.management_task(creation_ip_address, "creation"):

        result = rmq.create_container(container_name, client, cpu, ram, server_port_number,
                                      server_ip_address, client_port_number, client_ip_address,
                                      creation_ip_address)

    iaas_creation = dashboard_helper.get_iaas_ip_match(
        str(creation_ip_address))

    intents.initial_network_path(
        settings.IP_SDN_CONTROLLER, container_name, client)

    if result != 1:
        """create_container failed"""
        return NOT_CREATED

    vsh.enable_remote_video_streaming(creation_ip_address, str(int(client_port_number) + 1024),
                                      client_ip_address)
    # TODO: please check this loop !
    while helpers.store_db_log(id_request, str(result), "0", iaas_creation) != "0":
        print("DB not yet updated")


    return container_name # TODO: Check Code on top 
