
import dsmirai.client_broker as client_broker
import dsmirai.intent_based_networking as intent_based_networking
from operator import itemgetter
from dsmirai.persistent_model import helpers
from dsmirai.persistent_model import dashboard_helper

import dsmirai.onos_helpers as onos_helpers



"""
Code communication: migrate = 002

1/-1 = migrate/not migrate
2 = not present
3 = resources not available
4 = race condition

"""




def migrate(container_name, num_iteration, token1, ip_sdn_controller, target_cloud="None"):
    rmq = client_broker.ClientBroker("migration_queue")
    onos = onos_helpers.OnosHelpers()
    intents = intent_based_networking.IntentBasedNetworking()

    print("***********The Global Orchestrator***********")
    print("the server: {}".format(container_name))

    if not helpers.name_control(container_name):
        print("The requested container is already in a another process")
        id_request = helpers.insert_entry(container_name, "4", "002", "model", token1, "0", "None")
        return
    else:
        id_request = helpers.insert_entry(container_name, "None", "002", "model", token1, "1", "None")
        if rmq.verify_unique_name(container_name):
            print("***********The Global Orchestrator***********")
            print("find the container to migrate")
            print("The requested container is not in another process")
            table_statistics = rmq.get_container_resources(container_name)
            container_resources = max(table_statistics, key=itemgetter(1, 2))
            ip_source = container_resources[0]
            cpu = container_resources[1]
            ram = container_resources[2]
            print("***********The Global Orchestrator***********")
            print("the ip address of the source vm is: {}".format(ip_source))
            print("the cpu of the chosen container is: {}".format(cpu))
            print("the ram of the chosen container is: {}".format(ram))
            # verify resources needed and avoid ip_source
            if target_cloud == "None":
                table_statistics = rmq.verify_resource_migration(ip_source)
            else:
                target_ip = helpers.match_iaas_name_ip(target_cloud)
                table_statistics = rmq.verify_resource_directive(target_ip)

            winner_minion = max(table_statistics, key=itemgetter(1, 2, 3))
            print("***************************************************************")
            print(winner_minion[1])
            print(type(winner_minion[1]))

            print(winner_minion[2])
            print(type(winner_minion[2]))

            print(cpu)
            print(type(cpu))

            print(ram)
            print(type(ram))
            print("***************************************************************")
            if winner_minion[1] <= cpu or winner_minion[2] <= ram:
                print("***********The Global Orchestrator***********")
                print("Resources issues, no available resource to host the container in the target destination")
                while helpers.store_db_log(id_request, "3", "None") != "0":
                    print("DB not yet updated")
                return
            ip_destination = winner_minion[0]
            print("***********The Global Orchestrator***********")
            print("we are able to find a vm destination")
            print("the IP address of the chosen node is: {}".format(ip_destination))

            client_device, client_port_number, client_ip_address, ip_vm_client = onos.sdn_host_information(
                ip_sdn_controller, helpers.matching(container_name))
            print("the device source is: {}".format(client_device))
            print("the port number source is: {}".format(client_port_number))
            print("the ip address source is: {}".format(client_ip_address))

            server_device, server_port_number, server_ip_address, ip_vm_server = onos.sdn_host_information(
                ip_sdn_controller, container_name)

            print("the device destination is: {}".format(server_device))
            print("the port number destination is: {}".format(server_port_number))
            print("the ip address destination is: {}".format(server_ip_address))

            ovs_source = onos.friendly_ovs_name(client_device, ip_vm_client)
            print("ovs_source is: {}".format(ovs_source))
            old_ovs_destination = onos.friendly_ovs_name(server_device, ip_source)
            print("old_ovs_destination is: {}".format(old_ovs_destination))

            ovs_destination = onos.get_ovs(0, ip_destination)
            print("ovs_destination is: {}".format(ovs_destination))

            mac_ovs_destination = onos.mac_style_ovs_name(ovs_destination, ip_destination)
            print("mac_ovs_destination is: {}".format(mac_ovs_destination))

            interface_name = ovs_source + ovs_destination
            print("interface_name is: {}".format(interface_name))


            if not onos.verify_links(ip_sdn_controller, client_device, mac_ovs_destination):

                vxlan_port = helpers.add_vxlan_ip_ports(interface_name)
                print("new vxlan_port is: {}".format(vxlan_port))

                print("starting the VxLAN channel")
                intents.overlay_network(ip_vm_client, ip_destination, ovs_source, ovs_destination, interface_name,
                                        vxlan_port)
                print("successful VxLAN creation")


            else:
                if not onos.verify_local_distant_devices(ip_sdn_controller, client_device, mac_ovs_destination):

                    vxlan_port = helpers.get_overlay_port(interface_name)
                    print("existing vxlan_port distant is: {}".format(vxlan_port))


                else:
                    vxlan_port = 1
                    print("existing vxlan_port local is: {}".format(vxlan_port))

            intents.target_container_bridge_ovs(container_name, ip_destination, ovs_destination,
                                                server_port_number)
            print("SDN network established")

            print("Gathering the migration image info")
            LXC_IMAGE = rmq.get_container_image(ip_source, container_name)
            print("***********The Global Orchestrator***********")
            print("searching for a possible partial migration .....")

            result = 0
            if rmq.management_task(ip_source, "migration"):
                if rmq.part_migration_check(LXC_IMAGE, ip_destination, container_name):
                    print("***********The Global Orchestrator***********")
                    print("Para-Migration detected")
                    print("starting the partial migration")
                    result = rmq.part_migration(container_name, ip_destination, num_iteration, ip_source,
                                                client_device, mac_ovs_destination, client_port_number,
                                                server_port_number, vxlan_port, client_ip_address,
                                                server_ip_address, ip_sdn_controller)

                else:
                    print("***********The Global Orchestrator***********")
                    print("Full-Migration action")
                    print("starting a Full-Migration")
                    result = rmq.full_migration(container_name, ip_destination, num_iteration, ip_source,
                                                client_device, mac_ovs_destination, client_port_number,
                                                server_port_number, vxlan_port, client_ip_address,
                                                server_ip_address, ip_sdn_controller)

            iaas_migration = dashboard_helper.get_iaas_ip_match(str(ip_destination))
            print("the iaas for the migration is: {}".format(iaas_migration))



            print("deleting the SDN network in the source host")
            intent_priority = helpers.get_intent_priority(str(container_name))
            intents.network_redirection_1(ip_sdn_controller, client_device, mac_ovs_destination, client_port_number,
                                          server_port_number, vxlan_port, client_ip_address, server_ip_address,
                                          int(intent_priority))
            intents.network_redirection_2(ip_sdn_controller, client_device, client_port_number, vxlan_port,
                                          server_ip_address, int(intent_priority))
            intents.clean_container_bridge_ovs(container_name, ip_source, old_ovs_destination)

            answer = rmq.validate_migration(container_name, ip_destination, client_ip_address)
            if answer != 1:
                print("validate migration failed")
                return "Error"
            while helpers.store_db_log(id_request, str(result), str(iaas_migration)) != "0":
                print("DB not yet updated")
            if result != 1:
                print("system part migration failed")
                return "Error"

            return container_name

        else:
            print("***********The Global Orchestrator***********")
            print("container doesn't exist")

            id_request = helpers.insert_entry(container_name, "2", "002", "model", token1, "0", "None")
            return
