import subprocess
from dsmirai.persistent_model import helpers
from dsmirai.persistent_model import dashboard_helper
import time



def iaas_discovery():
    #helpers.initialize_iaas_table()

    while True:
        ping_count = 4
        print(ping_count)
        print("iaas discovery deamon activated")
        ip_addresses = helpers.available_iaas()
        for key, value in ip_addresses.items():
            process = subprocess.Popen(['ping', value, '-c', str(ping_count)],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            return_code = process.wait()
            print('ping returned {0}'.format(return_code))
            print(process.stdout.read())
            if return_code == 0:
                print(value + " available")

                helpers.update_state_iaas(value, "UP")
                # call Ansible right here
                with open('/root/PycharmProjects/mirai_project/dsmirai/IaaS_Discovery/hosts', "w") as my_file:
                    my_file.write(value)
                    my_file.close()
                time.sleep(5)

                process = subprocess.Popen(['ansible-playbook', 'playbook.yml'],
                                           cwd='/root/PycharmProjects/mirai_project/dsmirai/IaaS_Discovery/',
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)
                return_code = process.wait()
                print('ansible returned {0}'.format(return_code))
                print(process.stdout.read())

                helpers.update_configuration_iaas(value, "UP")

        time.sleep(20)

