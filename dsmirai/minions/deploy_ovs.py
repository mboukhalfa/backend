import os
import netifaces as ni
import virtual_machine as system_driver





def create_ovs_environment(ovs_1):
    basic_cmd = "sudo ovs-vsctl add-br br-{}1".format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl add-br br-{}2".format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = 'sudo ip link add name int{0}1 type veth peer name int{0}2'.format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = "ip link set int{0}1 up".format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = "ip link set int{0}2 up".format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl add-port br-{0}1 int{0}1 -- set Interface int{0}1 ofport_request=1".format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl add-port br-{0}2 int{0}2 -- set Interface int{0}2 ofport_request=1".format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl set-controller br-{}1 tcp:195.148.125.90:6653".format(ovs_1)
    os.system(basic_cmd)

    basic_cmd = "sudo ovs-vsctl set-controller br-{}2 tcp:195.148.125.90:6653".format(ovs_1)
    os.system(basic_cmd)




create_ovs_environment(system_driver.get_ip().split('.')[3])
