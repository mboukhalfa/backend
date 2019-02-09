
import subprocess
import os
import time
import logging
import linux_container as lxc_driver
my_logger = logging.getLogger('control_log_sdn_container')

NOK = -1
OK = 1
LXC_PATH = '/var/lib/lxc/'


def create(container_name, client, cpu, ram, server_port_number, server_ip_address, client_port_number,
           client_ip_address):
    try:
        print("container server creation :")
        basic_cmd = 'lxc-copy -n nginxBKserver -N {}'.format(container_name)
        os.system(basic_cmd)
        time.sleep(2)
        with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
            my_file.write('\n# hax for criu\n')
            my_file.write('lxc.console = none\n')
            my_file.write('lxc.tty = 0\n')
            my_file.write('lxc.cgroup.devices.deny = c 5:1 rwm\n')
            my_file.write('lxc.mount.entry = /sys/firmware/efi/efivars sys/firmware/efi/efivars none bind,optional 0 0\n')
            my_file.write('lxc.mount.entry = /proc/sys/fs/binfmt_misc proc/sys/fs/binfmt_misc none bind,optional 0 0\n')

        # Custom creation
        modify_cpu(container_name, cpu)
        modify_ram(container_name, ram)

        # SDN fashion
        modify_configuration_bridge(container_name)
        ovs_name = get_ovs(0)
        print("the name of the ovs is: {}".format(ovs_name))
        container_bridge_ovs(container_name, str(ovs_name), str(server_port_number))
        set_ip(container_name, server_ip_address)
        time.sleep(5)
        if not lxc_driver.start_container(container_name):
            return NOK
        time.sleep(2)

        while lxc_driver.get_ip_container(container_name) != str(server_ip_address):
            print("current_ip: {}".format(lxc_driver.get_ip_container(container_name)))
            print("envisaged_ip: {}".format(server_ip_address))
            time.sleep(1)
        response = 0
        while response != 256:
            response = lxc_driver.container_attach(container_name, ["ping", "-c", "1", "172.16.207.90"])
        print("end creation of server")

        print("container client creation :")
        # create the client
        ovs_name = get_ovs(1)
        print("the name of the ovs is: {}".format(ovs_name))

        # TODO: we need to update this 2 urgently
        create_client(client, str(ovs_name), client_ip_address, client_port_number, '2')
        time.sleep(2)
        print("end creation of client")
        update_nginx(client, str(server_ip_address))
        return OK
    except Exception as exception:
        my_logger.critical('ERROR: create():' + str(exception) + '\n')
        print("unable to create server and client ...")


def create_client(container_name, ovs_name, client_ip_address, client_port_number, brb):

    print("client creation: ")

    basic_cmd = 'lxc-copy -n nginxBKclient -N {}'.format(container_name)
    os.system(basic_cmd)

    modify_configuration_bridge(container_name)
    container_bridge_ovs(container_name, ovs_name, client_port_number)
    set_ip(container_name, client_ip_address)

    with open('{}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name), "a") as my_file:
        my_file.write('\nauto vethCltOut{}'.format(client_port_number))
        my_file.write('\niface vethCltOut{} inet static'.format(client_port_number))
        my_file.write('\n    address ')
        my_file.write('192.168.0.{}'.format(client_port_number))
        my_file.write('\n')
        my_file.write('    netmask 255.255.255.0')
        my_file.write('\n')
        my_file.write('    gateway 192.168.0.{}'.format(brb))

    if not lxc_driver.start_container(container_name):
        return NOK
    ####################################################################################
    # ################################# second interface##################################
    ####################################################################################

    basic_cmd = 'ip link add name vethCltOut{0} type veth peer name vethOutClt{0}'.format(client_port_number)
    os.system(basic_cmd)
    basic_cmd = 'ip link set vethCltOut{} up'.format(client_port_number)
    os.system(basic_cmd)
    basic_cmd = 'ip link set vethOutClt{} up'.format(client_port_number)
    os.system(basic_cmd)
    basic_cmd = 'brctl addif brOut vethOutClt{}'.format(client_port_number)
    os.system(basic_cmd)
    basic_cmd = 'ip link set dev vethCltOut' + str(client_port_number) + ' netns '
    basic_cmd = basic_cmd + str(lxc_driver.container_pid(container_name)) + ' name vethCltOut' + str(client_port_number)
    os.system(basic_cmd)

    response = 0
    while response != 256:
        response = lxc_driver.container_attach(container_name, ["ping", "-c", "1", "172.16.207.90"])
    print("end creation of client")
    time.sleep(2)


def modify_cpu(container_name, val):

    i = 0
    for line in open('{}{}/config'.format(LXC_PATH, container_name), "r"):
        if "lxc.cgroup.cpuset.cpus" in line:
            with open('{}{}/config'.format(LXC_PATH, container_name), "r") as input_file:
                with open('{}{}/config2'.format(LXC_PATH, container_name), "wb") as output_file:
                    for line2 in input_file:
                        if line2 != line:
                            output_file.write(line2)
            basic_cmd = 'rm {}{}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
            basic_cmd = 'mv {0}{1}/config2 {0}{1}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
            if val == "1":
                with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
                    my_file.write('\nlxc.cgroup.cpuset.cpus =')
                    my_file.write(' ')
                    my_file.write(str(int(val)-1))
                    my_file.write('\n')
            else:
                with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
                    my_file.write('\nlxc.cgroup.cpuset.cpus =')
                    my_file.write(' 0-')
                    my_file.write(str(int(val)-1))
                    my_file.write('\n')

            i = 1
    if i == 0:
        if val == "1":
            with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
                my_file.write('\nlxc.cgroup.cpuset.cpus =')
                my_file.write(' ')
                my_file.write(str(int(val) - 1))
                my_file.write('\n')
        else:
            with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
                my_file.write('\nlxc.cgroup.cpuset.cpus =')
                my_file.write(' 0-')
                my_file.write(str(int(val) - 1))
                my_file.write('\n')


# customized Memory
def modify_ram(container_name, val):
    i = 0
    for line in open(LXC_PATH + str(container_name) + '/config', "r"):
        if "lxc.cgroup.memory.limit_in_bytes" in line:
            with open(LXC_PATH + str(container_name) + '/config', "r") as input_file:
                with open(LXC_PATH + str(container_name) + '/config2', "wb") as output_file:
                    for line2 in input_file:
                        if line2 != line:
                            output_file.write(line2)

            basic_cmd = 'rm {}{}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
            basic_cmd = 'mv {0}{1}/config2 {0}{1}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)

            with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
                my_file.write('\nlxc.cgroup.memory.limit_in_bytes =')
                my_file.write(' ')
                my_file.write(val)
                my_file.write('\n')

            i = 1
    if i == 0:
        with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
            my_file.write('\nlxc.cgroup.memory.limit_in_bytes =')
            my_file.write(' ')
            my_file.write(val)
            my_file.write('\n')


# bridge creation for each container
def modify_configuration_bridge(container_name):

    for line in open('{}{}/config'.format(LXC_PATH, container_name), "r"):
        if "lxc.network.link" in line:
            with open('{}{}/config'.format(LXC_PATH, container_name), "r") as input_file:
                with open('{}{}/config2'.format(LXC_PATH, container_name), "w") as output_file:
                    for line2 in input_file:
                        if line2 != line:
                            output_file.write(line2)
            basic_cmd = 'rm {}{}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
            basic_cmd = 'mv {0}{1}/config2 {0}{1}/config'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
    with open('{}{}/config'.format(LXC_PATH, container_name), "a") as my_file:
        my_file.write('\nlxc.network.link =')
        my_file.write(' ')
        my_file.write('br{}'.format(container_name))
        my_file.write('\n')


def container_bridge_ovs(container_name, ovs_name, ovs_port):

    basic_cmd = 'ip link add name veth{0}Ovs type veth peer name vethOvs{0}'.format(container_name)
    os.system(basic_cmd)

    basic_cmd = "ip link set vethOvs{} up".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "ip link set veth{}Ovs up".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "brctl addbr br{}".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "ifconfig br{} up".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "brctl addif br{0} veth{0}Ovs".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl add-port {2} vethOvs{0} -- set Interface vethOvs{0} ofport_request={1}".format(
        container_name, ovs_port, ovs_name)
    print(basic_cmd)
    os.system(basic_cmd)


def set_ip(container_name, ip_address):

    for line in open('{}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name), "r"):
        if "iface eth0 inet dhcp" in line:
            with open('{}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name), "r") as input_file:
                with open('{}{}/rootfs/etc/network/interfaces2'.format(LXC_PATH, container_name), "w") as output_file:
                    for line2 in input_file:
                        if line2 != line:
                            output_file.write(line2)

            basic_cmd = 'rm {}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name)
            os.system(basic_cmd)
            basic_cmd = 'mv {0}{1}/rootfs/etc/network/interfaces2 {0}{1}/rootfs/etc/network/interfaces'.format(
                LXC_PATH, container_name)
            os.system(basic_cmd)

            with open('{}{}/rootfs/etc/network/interfaces'.format(LXC_PATH, container_name), "a") as my_file:
                my_file.write('\niface eth0 inet static')
                my_file.write('\n    address ')
                my_file.write(str(ip_address))
                my_file.write('\n')
                my_file.write('    netmask 255.255.255.0')


def update_nginx(container_name, ip_address):
    for line in open(LXC_PATH + str(container_name) + '/rootfs/etc/nginx/sites-available/default', "r"):
        if "proxy_pass" in line:
            with open(LXC_PATH + str(container_name) + '/rootfs/etc/nginx/sites-available/default', "r") as input_file:
                with open(LXC_PATH + str(container_name) + '/rootfs/etc/nginx/sites-available/default2', "w") as \
                        output_file:
                    for line2 in input_file:
                        if line2 != line:
                            output_file.write(line2)
                        else:
                            output_file.write("                ")
                            output_file.write("proxy_pass")
                            output_file.write("      ")
                            output_file.write("http://" + str(ip_address) + "/test.mp4;")
                            output_file.write('\n')

            basic_cmd = 'rm ' + LXC_PATH + str(container_name) + '/rootfs/etc/nginx/sites-available/default'
            os.system(basic_cmd)
            basic_cmd = 'mv ' + LXC_PATH + str(container_name) + '/rootfs/etc/nginx/sites-available/default2 ' \
                        + LXC_PATH + str(container_name) + '/rootfs/etc/nginx/sites-available/default'
            os.system(basic_cmd)
    time.sleep(2)
    lxc_driver.container_attach(container_name, ["/etc/init.d/nginx", "restart"])


def get_ovs(i):
    basic_cmd = 'ovs-vsctl list-br'
    result = subprocess.check_output(basic_cmd, shell=True)
    c = result.decode().split('\n')
    return str(c[i])
