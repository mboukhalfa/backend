
import dsmirai.client_broker as client_broker
import dsmirai.intent_based_networking as intent_based_networking
from operator import itemgetter
from dsmirai.persistent_model import helpers
from dsmirai.persistent_model import dashboard_helper
import dsmirai.video_streaming_handler as vsh

"""
Code communication: create = 001

1/-1 = created/not created
2 = already present
3 = resources not available
4 = race condition
"""

from mirai.models import Log

def create(container_name, client, cpu, ram, ip_sdn_controller, container_placement="None",
           application_type="video"):
    print(container_name)
    """
    :param container_name:
    :param client:
    :param cpu:
    :param ram:
    :param token1:
    :param ip_sdn_controller:
    :param container_placement:
    :param application_type:
    :return:
    """
    rmq = client_broker.ClientBroker("creation_queue")
    intents = intent_based_networking.IntentBasedNetworking()
    print("***********The Global Orchestrator***********")
    print("the server: {}".format(container_name))
    print("the client: {}".format(client))
    print("cpu: {}".format(cpu))
    print("ram: {}".format(ram))
    print("placement: {}".format(container_placement))

    if not helpers.name_control(container_name):
        print("The requested container is already in a another process")
        id_request = helpers.insert_entry(container_name, "4", "001", client, "0", "None")
        return "Error"
    else:
        id_request = helpers.insert_entry(container_name, "None", "001", client, "1", "None")
        if not rmq.verify_unique_name(container_name):
            print("***********The Global Orchestrator***********")
            print("didn't find any container with a similar name in the cluster")
            print("The requested container is not in another process")
            if container_placement == "None":
                table_statistics = rmq.verify_resource_creation()
            else:
                ip_address = helpers.match_iaas_name_ip(container_placement)
                if ip_address == "Error":
                    print("unknown cloud name !!!")
                    return
                table_statistics = rmq.verify_resource_directive(ip_address)
            print(table_statistics)
            print(type(table_statistics))
            winner_minion = max(table_statistics, key=itemgetter(1, 2, 3))
            if 'M' in ram:
                int_ram = ram.split('M')[0]
            else:
                int_ram = ram.split('G')[0]
            if winner_minion[1] < int(cpu) and winner_minion[2] < int(int_ram):
                print("***********The Global Orchestrator***********")
                print("Resources issues")
                while helpers.store_db_log(id_request, "3", "None") != "0":
                    print("DB not yet updated")
                return "Error"
            creation_ip_address = winner_minion[0]
            print("***********The Global Orchestrator***********")
            print("the resources are verified in the cluster")
            print("the IP address of the chosen node is: {}".format(creation_ip_address))

            if application_type != "video":
                # TODO: to be implemented later when adding new VNFs
                pass
            else:
                server_port_number, server_ip_address = helpers.add_entry_ip_ports(container_name)
                print("the port number for the server is: {}".format(server_port_number))
                print("the ip address for the server is: {}".format(server_ip_address))

                client_port_number, client_ip_address = helpers.add_entry_ip_ports(client)
                print("the port number for the client is: {}".format(client_port_number))
                print("the ip address for the client is: {}".format(client_ip_address))

                print("start the creation itself ....")
                result = 0
                if rmq.management_task(creation_ip_address, "creation"):

                    result = rmq.create_container(container_name, client, cpu, ram, server_port_number,
                                                  server_ip_address, client_port_number, client_ip_address,
                                                  creation_ip_address)

                iaas_creation = dashboard_helper.get_iaas_ip_match(str(creation_ip_address))
                print("the iaas for the creation is: {}".format(iaas_creation))

                intents.initial_network_path(ip_sdn_controller, container_name, client)
                print("***********The Global Orchestrator***********")
                print("the result is: {}".format(result))
                if result != 1:
                    print("create_container failed")
                    return
                vsh.enable_remote_video_streaming(creation_ip_address, str(int(client_port_number) + 1024),
                                                  client_ip_address)
                while helpers.store_db_log(id_request, str(result), iaas_creation) != "0":
                    print("DB not yet updated")
            return container_name

        else:
            print("***********The Global Orchestrator***********")
            print("container already exist")

            id_request = helpers.insert_entry(container_name, "2", "001", client, "0", "None")
            return "Error"
