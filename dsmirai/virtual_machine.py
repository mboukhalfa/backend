import subprocess
import logging
import netifaces as ni
import paramiko
import dsmirai.linux_container as lxc_driver



my_logger = logging.getLogger('control_log_vm')


# Getting the Disk of the VM
def get_vm_disk():
    try:
        cmd = 'df -H /'
        result = subprocess.check_output(cmd, shell=True)
        my_info = result.decode().split('\n')
        vm_status = my_info[1].split()[0:6]
        for i in range(1,  int(len(vm_status[0])+1)):
            if vm_status[3][i-1] == 'M':
                res = vm_status[3].split('M')
                return res[0]
            elif vm_status[3][i-1] == 'G':
                res = vm_status[3].split('G')
                first_number = float(res[0].replace(',', '.'))
                second_number = float(1000.0)
                answer = (first_number * second_number)
                return answer
    except Exception as exception:
        my_logger.critical('ERROR: get_vm_disk():' + str(exception) + '\n')
        print("unable to get disk information from our VM")


# Getting the Memory of the VM
def get_vm_mem():
    try:
        cmd = 'vmstat -s'
        result = subprocess.check_output(cmd, shell=True)
        my_info = result.decode().split('\n')
        free_memory = my_info[0].split()[0:3]
        return int(int(free_memory[0])/1024)
    except Exception as exception:
        my_logger.critical('ERROR: get_vm_mem():' + str(exception) + '\n')
        print("unable to get memory information from our VM ")


# Getting the CPU of the VM
def get_vm_cpu():
    try:
        cmd = 'nproc'
        result = subprocess.check_output(cmd, shell=True)
        return int(result)
    except Exception as exception:
        my_logger.critical('ERROR: get_vm_cpu():' + str(exception) + '\n')
        print("unable to get cpu information from our VM")


# Getting the IP address of the VM
def get_ip():
    ip_list = ni.interfaces()
    indices = [s for i, s in enumerate(ip_list) if 'ens' in s]
    return ni.ifaddresses(str(indices[0]))[ni.AF_INET][0]['addr']


def default_bridge():

    subprocess.Popen(['brctl', 'addbr', 'brOut'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    basi_cmd = 'ifconfig brOut 192.168.0.2 netmask 255.255.255.0 up'
    subprocess.check_output(basi_cmd, shell=True)
    basi_cmd = 'iptables -t nat -A POSTROUTING --out-interface {} -j MASQUERADE'.format(get_ip())
    subprocess.check_output(basi_cmd, shell=True)
    basi_cmd = 'iptables -A FORWARD --in-interface brOut -j ACCEPT'
    subprocess.check_output(basi_cmd, shell=True)



def resource_availability():

    nb_container = lxc_driver.list_containers()
    print(nb_container)
    vm_cpu = get_vm_cpu()
    vm_ram = get_vm_mem()
    vm_disk = get_vm_disk()

    for i in range(len(nb_container)):
        if nb_container[i] != 'nginxBKserver' and nb_container[i] != 'nginxBKclient':
            cpu = lxc_driver.get_cpu(nb_container[i])
            ram = lxc_driver.get_mem(nb_container[i])
            disk = lxc_driver.get_size(nb_container[i])
            vm_cpu = int(vm_cpu) - int(cpu)
            vm_ram = int(vm_ram) - int(ram)
            vm_disk = float(vm_disk) - float(disk)

    return vm_cpu, vm_ram, vm_disk



def ssh_query(cmd, ip_destination, output=False, user_name='root', password='iprotect'):

    """
    in order to run a ssh command easier
    :param cmd:
    :param ip_destination:
    :param user_name:
    :param password:
    :param output:
    """

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(str(ip_destination), username=user_name, password=password)
    if output:
        try:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            return stdin, stdout, stderr
        except subprocess.CalledProcessError:
            out = False
            return out
    if int(ssh.exec_command(cmd)) == 0:
        return True
    else:
        return False
