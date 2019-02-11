import virtual_machine as system_driver
import linux_container as lxc_driver
import os


def container_list():
    nb_container = lxc_driver.list_containers()
    deleted_container = []
    for i in range(len(nb_container)):
        if nb_container[i] != 'nginxBKserver' and nb_container[i] != 'nginxBKclient':
            deleted_container.append(nb_container[i])
    return deleted_container


def clean_container_bridge_ovs(container_name, ovs_source):
    basic_cmd = "brctl delif br{0} veth{0}Ovs".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "ovs-vsctl del-port {} vethOvs{}".format(ovs_source, container_name)
    os.system(basic_cmd)

    basic_cmd = "ip link del dev veth{}Ovs".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "ifconfig br{} down".format(container_name)
    os.system(basic_cmd)

    basic_cmd = "brctl delbr br{}".format(container_name)
    os.system(basic_cmd)


def clean_ovs_bridges():
    basic_cmd = "ovs-vsctl del-br br-{}1".format(system_driver.get_ip().split(".")[3])
    os.system(basic_cmd)
    basic_cmd = "ovs-vsctl del-br br-{}2".format(system_driver.get_ip().split(".")[3])
    os.system(basic_cmd)


def kill_python_process():
    basic_cmd = "killall python3"
    os.system(basic_cmd)


def core_cleaner():
    container_to_delete = container_list()
    for i in range(len(container_to_delete)):
        clean_container_bridge_ovs(container_to_delete[i], "br-{}1".format(system_driver.get_ip().split(".")[3]))
        clean_container_bridge_ovs(container_to_delete[i], "br-{}2".format(system_driver.get_ip().split(".")[3]))
        lxc_driver.delete_container(container_to_delete[i])
    clean_ovs_bridges()


core_cleaner()
