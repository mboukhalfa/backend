
import dsmirai.client_broker as client_broker
import dsmirai.intent_based_networking as intent_based_networking
from operator import itemgetter
from dsmirai.persistent_model import helpers
from dsmirai.persistent_model import dashboard_helper
import dsmirai.video_streaming_handler as vsh
from django.conf import settings
from mirai.models import IaaS


"""
Code communication: create = 001

1/-1 = created/not created
2 = already present
3 = resources not available
4 = race condition
"""



def create(container_id):
    """
    :param container_id:
    :return:
    """
    queue_name = "creation_queue"
    rmq = client_broker.ClientBroker(queue_name)
    intents = intent_based_networking.IntentBasedNetworking()
    print("***********The Global Orchestrator***********")
    print("the container_id: {}".format(container_id))
    # TODO: insert in LOG table based on the container_id
    container_name, ram, cpu, container_placement, application_type, server_ip_address, server_port_number = \
        helpers.add_entry_ip_ports(container_id)
    id_request = helpers.insert_entry(container_name, "None", "001", "1")
    client, client_ip_address, client_port_number = helpers.insert_entry_client(container_name)

    print("the server: {}".format(container_name))
    print("the client: {}".format(client))
    print("cpu: {}".format(cpu))
    print("ram: {}".format(ram))
    print("placement id: {}".format(container_placement))
    print("application_type: {}".format(application_type))
    print("the port number for the server is: {}".format(server_port_number))
    print("the ip address for the server is: {}".format(server_ip_address))
    print("the port number for the client is: {}".format(client_port_number))
    print("the ip address for the client is: {}".format(client_ip_address))

    print("***********The Global Orchestrator***********")
    if container_placement is None:
        print("smart creation of containers")
        table_statistics = rmq.verify_resource("star" + queue_name.split('_')[0], "creation")
    else:
        # TODO: I suggest here to do the control of it's the cloud exist or not in the front end part
        print("directive creation of containers")
        ip_address = IaaS.objects.filter(pk=container_placement).iaas_ip
        if ip_address is None:
            print("unknown cloud name !!!")
            return
        print("the ip address of the IAAS is: {}".format(ip_address))
        table_statistics = rmq.verify_resource(ip_address, "creation")
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
        while helpers.store_db_log(id_request, "3") != "0":
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
        print("start the creation itself ....")
        result = 0
        if rmq.management_task(creation_ip_address, "creation"):

            result = rmq.create_container(container_name, client, cpu, ram, server_port_number,
                                          server_ip_address, client_port_number, client_ip_address,
                                          creation_ip_address)

        if container_placement is None:
            container_placement = IaaS.objects.filter(iaas_ip=creation_ip_address).id
            helpers.tracking_iaas_container(container_id, container_placement)
            print("the id of iaas for the creation is: {}".format(container_placement))

        intents.initial_network_path(settings.IP_SDN_CONTROLLER, server_ip_address, client_ip_address)
        print("***********The Global Orchestrator***********")
        print("the result is: {}".format(result))
        if result != 1:
            print("create_container failed")
            return
        vsh.enable_remote_video_streaming(creation_ip_address, str(int(client_port_number) + 1024),
                                          client_ip_address)
        while helpers.store_db_log(id_request, str(result)) != "0":
            print("DB not yet updated")
    return container_name


