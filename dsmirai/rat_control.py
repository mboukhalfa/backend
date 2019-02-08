import dsmirai.client_broker as client_broker
import time
import datetime
from dsmirai.persistent_model import helpers
from mirai_project import tasks as trigger
import uuid




"""
0 = start the trigger
1 = successful trigger event
"""


def rat_trigger():
    rmq = client_broker.ClientBroker("rat_queue")
    trigger_type = "rat_trigger"
    ip_sdn_controller = "195.148.125.90"


    while True:
        a = rmq.rat_trigger()
        print("The returned value is {}".format(a))
        ntm = decision_rat(a)

        print(type(ntm))
        print(ntm)
        for key, value in ntm.items():

            if not helpers.name_control(value['container']):
                print("***************************************************************************************")
                print("***************************************************************************************")
                print("container {} is in another action waiting for it to finish".format(value['container']))
                print("***************************************************************************************")
                print("***************************************************************************************")

            else:
                print("the rat_trigger is activated")
                iaas = helpers.match_containers_iaas(value['container'])
                id_request = helpers.insert_entry(value['container'], "None", "003", "RAT", str(uuid.uuid4()), "1",
                                                  str(iaas))
                request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                           "migrate_rat", datetime.datetime.now(), "0")
                print("migrate the container {} localized in {}".format(value['container'], value['VM_ip']))
                while helpers.store_db_log(id_request, "1", str(iaas)) != "0":
                    print("DB not yet updated")
                if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                        value['container']:
                    helpers.update_triggers_entry(request_id, "1")
                else:
                    helpers.update_triggers_entry(request_id, "2")

        time.sleep(50)


def api_rat_trigger(iaas_name="None"):
    rmq = client_broker.ClientBroker("rat_queue")
    trigger_type = "rat_trigger"
    ip_sdn_controller = "195.148.125.90"
    if iaas_name == "None":
        a = rmq.rat_trigger()
    else:
        iaas_ip = helpers.match_iaas_name_ip(iaas_name)
        a = rmq.directive_rat_trigger(iaas_ip)
    print("The returned value is {}".format(a))
    ntm = decision_rat(a)

    print(type(ntm))
    print(ntm)
    for key, value in ntm.items():

        if not helpers.name_control(value['container']):
            print("***************************************************************************************")
            print("***************************************************************************************")
            print("container {} is in another action waiting for it to finish".format(value['container']))
            print("***************************************************************************************")
            print("***************************************************************************************")

        else:
            if iaas_name == "None":
                iaas_name = helpers.match_containers_iaas(value['container'])

            print("the api_rat_trigger is activated")
            id_request = helpers.insert_entry(value['container'], "None", "003", "RAT", str(uuid.uuid4()), "1",
                                              str(iaas_name))
            request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                       "migrate_rat", datetime.datetime.now(), "0")
            print("migrate the container {} localized in {}".format(value['container'], value['VM_ip']))
            while helpers.store_db_log(id_request, "1", str(iaas_name)) != "0":
                print("DB not yet updated")
            if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                    value['container']:
                helpers.update_triggers_entry(request_id, "1")
            else:
                helpers.update_triggers_entry(request_id, "2")






def decision_rat(solver):
    ntm = {}
    i = 0
    print(solver)
    for key, value in solver.items():

        while value['live_disk'] > value['disk'] * 0.8 and bool(solver[key]['containers']):
            print("*********************** DISK Section ***********************")
            disk_max = 0
            disk_key_max = "init"
            for kk, vv in solver[key]['containers'].items():
                if disk_max < vv['disk']:
                    disk_max = vv['disk']
                    disk_key_max = kk
            value['live_disk'] = value['live_disk'] - disk_max
            value['live_ram'] = value['live_ram'] - solver[key]['containers'][disk_key_max]['ram']
            value['live_cpu'] = value['live_cpu'] - solver[key]['containers'][disk_key_max]['cpu']

            ntm['node_to_migrate_{}'.format(i)] = {'VM_ip': key, 'container': disk_key_max}
            i = i + 1
            del solver[key]['containers'][disk_key_max]

        while value['live_ram'] > value['ram'] * 0.8 and bool(solver[key]['containers']):
            print("*********************** RAM Section ***********************")
            ram_max = 0
            ram_key_max = "init"
            for kk, vv in solver[key]['containers'].items():
                if ram_max < vv['ram']:
                    ram_max = vv['ram']
                    ram_key_max = kk
            value['live_ram'] = value['live_ram'] - ram_max
            value['live_disk'] = value['live_disk'] - solver[key]['containers'][ram_key_max]['disk']
            value['live_cpu'] = value['live_cpu'] - solver[key]['containers'][ram_key_max]['cpu']
            ntm['node_to_migrate_{}'.format(i)] = {'VM_ip': key, 'container': ram_key_max}
            i = i + 1

            del solver[key]['containers'][ram_key_max]

        while value['live_cpu'] > value['cpu'] * 0.4 and bool(solver[key]['containers']):
            print("*********************** CPU Section ***********************")
            cpu_max = 0
            cpu_key_max = "init"
            for kk, vv in solver[key]['containers'].items():
                if cpu_max < vv['cpu']:
                    cpu_max = vv['cpu']
                    cpu_key_max = kk
            value['live_cpu'] = value['live_cpu'] - cpu_max
            print(value['live_cpu'])
            value['live_ram'] = value['live_ram'] - solver[key]['containers'][cpu_key_max]['ram']
            print(value['live_ram'])
            value['live_disk'] = value['live_disk'] - solver[key]['containers'][cpu_key_max]['disk']
            print(value['live_disk'])
            ntm['node_to_migrate_{}'.format(i)] = {'VM_ip': key, 'container': cpu_key_max}
            i = i + 1

            del solver[key]['containers'][cpu_key_max]


    return ntm

















