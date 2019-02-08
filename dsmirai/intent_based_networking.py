import dsmirai.onos_helpers as onos_helpers
import dsmirai.utils as system_driver


class IntentBasedNetworking:

    def __init__(self):
        self.onos_helpers = onos_helpers.OnosHelpers()





    def initial_network_path(self, ip_sdn_controller, container_name, client):
        client_device, client_port_number, client_ip_address, ip_vm_client = self.onos_helpers.sdn_host_information(
            ip_sdn_controller, client)
        print("the device source is: {}".format(client_device))
        print("the port number source is: {}".format(client_port_number))
        print("the ip address source is: {}".format(client_ip_address))

        server_device, server_port_number, server_ip_address, ip_vm_server = self.onos_helpers.sdn_host_information(
            ip_sdn_controller, container_name)
        print("the device destination is: {}".format(server_device))
        print("the port number destination is: {}".format(server_port_number))
        print("the ip address destination is: {}".format(server_ip_address))

        list_of_links = self.onos_helpers.get_all_inter_ovs_links(ip_sdn_controller)
        print("the list of the link is: {}".format(list_of_links))
        for i in range(0, int(len(list_of_links))):
            device_source = list_of_links[i]['devicesrc']
            device_destination = list_of_links[i]['devicedst']
            if client_device == device_source and server_device == device_destination:
                middle_port_1 = list_of_links[i]['portsrc']
                middle_port_2 = list_of_links[i]['portdst']

                self.onos_helpers.complex_intent(str(ip_sdn_controller), client_device, client_port_number,
                                                 client_device, middle_port_1, 100, 2048, server_ip_address)
                self.onos_helpers.complex_intent(str(ip_sdn_controller), server_device, middle_port_2, server_device,
                                                 server_port_number, 100, 2048, server_ip_address)
                self.onos_helpers.complex_intent(str(ip_sdn_controller), server_device, server_port_number,
                                                 server_device, middle_port_2, 300, 2048, client_ip_address)
                self.onos_helpers.complex_intent(str(ip_sdn_controller), client_device, middle_port_1, client_device,
                                                 client_port_number, 300, 2048, client_ip_address)
        return server_ip_address


    def network_redirection_1(self, ip_sdn_controller, client_device, mac_ovs_destination, client_port_number,
                              server_port_number, vxlan_port, client_ip_address, server_ip_address, priority):

        self.onos_helpers.complex_intent(str(ip_sdn_controller), mac_ovs_destination, vxlan_port, mac_ovs_destination,
                                         server_port_number, int(priority), 2048, server_ip_address)
        self.onos_helpers.complex_intent(str(ip_sdn_controller), mac_ovs_destination, server_port_number,
                                         mac_ovs_destination, vxlan_port, int(priority) + 200, 2048, client_ip_address)
        self.onos_helpers.complex_intent(str(ip_sdn_controller), client_device, vxlan_port, client_device,
                                         client_port_number, int(priority) + 200, 2048, client_ip_address)

    def network_redirection_2(self, ip_sdn_controller, client_device, client_port_number, vxlan_port,
                              server_ip_address, priority):
        self.onos_helpers.complex_intent(str(ip_sdn_controller), client_device, client_port_number, client_device,
                                         vxlan_port, int(priority), 2048, server_ip_address)

    @staticmethod
    def overlay_network(ip_source, ip_destination, ovs_source, ovs_destination, interface_name, vxlan_port):

        cmd = []
        ip = []

        cmd1 = 'ovs-vsctl add-port ' + str(ovs_source) + '  ' + str(interface_name) + \
               ' -- set interface ' + str(interface_name) + ' type=' + 'vxlan' + ' options:remote_ip=' \
               + str(ip_destination) + ' ofport_request=' + str(vxlan_port)
        cmd.append(cmd1)
        ip.append(ip_source)

        cmd2 = 'ovs-vsctl add-port ' + str(ovs_destination) + '  ' + str(interface_name) \
               + ' -- set interface ' + str(interface_name) + ' type=' + 'vxlan' + \
               ' options:remote_ip=' + str(ip_source) + ' ofport_request=' \
               + str(vxlan_port)
        cmd.append(cmd2)
        ip.append(ip_destination)

        for i in range(len(cmd)):
            a, b, c = system_driver.ssh_query(cmd[i], ip[i], True)


    @staticmethod
    def target_container_bridge_ovs(container_name, ip_destination, ovs_destination, server_port_number):
        basic_cmd = 'ip link add name veth{0}Ovs type veth peer name vethOvs{0}'.format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "ip link set vethOvs{} up".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "ip link set veth{}Ovs up".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "brctl addbr br{}".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "ifconfig br{} up".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "brctl addif br{0} veth{0}Ovs".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "sudo ovs-vsctl add-port {2} vethOvs{0} -- set Interface vethOvs{0} ofport_request={1}".format(
            container_name, server_port_number, ovs_destination)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)


    @staticmethod
    def clean_container_bridge_ovs(container_name, ip_destination, ovs_source):
        basic_cmd = "brctl delif br{0} veth{0}Ovs".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "ovs-vsctl del-port {} vethOvs{}".format(ovs_source, container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "ip link del dev veth{}Ovs".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "ifconfig br{} down".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)

        basic_cmd = "brctl delbr br{}".format(container_name)
        a, b, c = system_driver.ssh_query(basic_cmd, ip_destination, True)