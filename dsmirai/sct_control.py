import dsmirai.client_broker as client_broker
import time
from dsmirai.persistent_model import helpers
import datetime
from mirai_project import tasks as trigger
import uuid


"""
0 = start the trigger
1 = successful trigger event
2 = failure in the trigger event
"""

cpu_threshold = 0.7
ram_threshold = 0.7


def sct_trigger():
    rmq = client_broker.ClientBroker("sct_queue")
    trigger_type = "sct_trigger"
    ip_sdn_controller = "195.148.125.90"

    while True:

        a = rmq.sct_trigger()
        print("The returned value is {}".format(a))
        ntm = decision_sct(a)
        print("the type of the ntm is:")
        print(type(ntm))
        print(ntm)
        for key, value in ntm.items():
            if not helpers.name_control(value['container']):
                print("container {} is in another action waiting for it to finish".format(value['container']))
            else:
                print("the sct_trigger is activated")
                iaas = helpers.match_containers_iaas(value['container'])
                id_request = helpers.insert_entry(value['container'], "None", "003", "SCT", "1",
                                                  str(iaas))
                if 'node_to_migrate_CPU_RAM' in key:

                    request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                               "migrate_cpu_ram", datetime.datetime.now(), "0")
                    print("migrate both of the cpu and the ram")
                    if not rmq.scale_up_cpu_ram(value['container'], value['VM_ip'], value['cpu'], value['ram']):
                        print("Unable to migrate both of the cpu and the ram")
                        helpers.update_triggers_entry(request_id, "2")
                    else:
                        while helpers.store_db_log(id_request, "1", str(iaas)) != "0":
                            print("DB not yet updated")
                        if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                                value['container']:
                            helpers.update_triggers_entry(request_id, "1")
                        else:
                            helpers.update_triggers_entry(request_id, "2")
                elif 'node_to_migrate_CPU' in key:
                    request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                               "migrate_cpu", datetime.datetime.now(), "0")
                    print("migrate the cpu")
                    if not rmq.scale_up_cpu(value['container'], value['VM_ip'], value['cpu']):
                        print("Unable to migrate the cpu")
                        helpers.update_triggers_entry(request_id, "2")
                    else:
                        while helpers.store_db_log(id_request, "1", str(iaas)) != "0":
                            print("DB not yet updated")
                        if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                                value['container']:
                            helpers.update_triggers_entry(request_id, "1")
                        else:
                            helpers.update_triggers_entry(request_id, "2")
                elif 'node_to_migrate_RAM' in key:
                    request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                               "migrate_ram", datetime.datetime.now(), "0")
                    print("migrate the ram")
                    if not rmq.scale_up_ram(value['container'], value['VM_ip'], value['ram']):
                        print("Unable to migrate the ram")
                        helpers.update_triggers_entry(request_id, "2")
                    else:
                        while helpers.store_db_log(id_request, "1", str(iaas)) != "0":
                            print("DB not yet updated")
                        if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                                value['container']:
                            helpers.update_triggers_entry(request_id, "1")
                        else:
                            helpers.update_triggers_entry(request_id, "2")
                elif 'node_to_scaleUp_CPU_RAM' in key:
                    request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                               "create_cpu_ram", datetime.datetime.now(), "0")
                    print("scale up both of the cpu and the ram")
                    if not rmq.scale_up_cpu_ram(value['container'], value['VM_ip'], value['cpu'], value['ram']):
                        print("Unable to scale up both of the cpu and the ram")
                        helpers.update_triggers_entry(request_id, "2")
                    else:
                        helpers.update_triggers_entry(request_id, "1")
                    while helpers.store_db_log(id_request, "1", str(iaas)) != "0":
                        print("DB not yet updated")
                elif 'node_to_scaleUp_CPU' in key:
                    request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                               "scale_cpu", datetime.datetime.now(), "0")
                    print("scale up the cpu")
                    if not rmq.scale_up_cpu(value['container'], value['VM_ip'], value['cpu']):
                        print("Unable to scale ip the cpu")
                        helpers.update_triggers_entry(request_id, "2")
                    else:
                        helpers.update_triggers_entry(request_id, "1")
                    while helpers.store_db_log(id_request, "1", str(iaas)) != "0":
                        print("DB not yet updated")
                elif 'node_to_scaleUp_RAM' in key:
                    request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                               "scale_ram", datetime.datetime.now(), "0")
                    print("scale up the ram")
                    if not rmq.scale_up_ram(value['container'], value['VM_ip'], value['ram']):
                        print("Unable to scale ip the ram")
                        helpers.update_triggers_entry(request_id, "2")
                    else:
                        helpers.update_triggers_entry(request_id, "1")
                    while helpers.store_db_log(id_request, "1", str(iaas)) != "0":
                        print("DB not yet updated")

        time.sleep(50)


def api_sct_trigger(iaas_name="None"):
    rmq = client_broker.ClientBroker("sct_queue")
    trigger_type = "sct_trigger"
    ip_sdn_controller = "195.148.125.90"

    if iaas_name == "None":
        a = rmq.sct_trigger()
    else:
        iaas_ip = helpers.match_iaas_name_ip(iaas_name)
        a = rmq.directive_sct_trigger(iaas_ip)

    print("The returned value is {}".format(a))
    ntm = decision_sct(a)
    print("the type of the ntm is:")
    print(type(ntm))
    print(ntm)
    for key, value in ntm.items():
        if not helpers.name_control(value['container']):
            print("container {} is in another action waiting for it to finish".format(value['container']))
        else:
            print("the sct_trigger is activated")
            if iaas_name == "None":
                iaas_name = helpers.match_containers_iaas(value['container'])
            id_request = helpers.insert_entry(value['container'], "None", "003", "SCT", "1",
                                              str(iaas_name))
            if 'node_to_migrate_CPU_RAM' in key:

                request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                           "migrate_cpu_ram", datetime.datetime.now(), "0")
                print("migrate both of the cpu and the ram")
                if not rmq.scale_up_cpu_ram(value['container'], value['VM_ip'], value['cpu'], value['ram']):
                    print("Unable to migrate both of the cpu and the ram")
                    helpers.update_triggers_entry(request_id, "2")
                else:
                    while helpers.store_db_log(id_request, "1", str(iaas_name)) != "0":
                        print("DB not yet updated")
                    if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                            value['container']:
                        helpers.update_triggers_entry(request_id, "1")
                    else:
                        helpers.update_triggers_entry(request_id, "2")
            elif 'node_to_migrate_CPU' in key:
                request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                           "migrate_cpu", datetime.datetime.now(), "0")
                print("migrate the cpu")
                if not rmq.scale_up_cpu(value['container'], value['VM_ip'], value['cpu']):
                    print("Unable to migrate the cpu")
                    helpers.update_triggers_entry(request_id, "2")
                else:
                    while helpers.store_db_log(id_request, "1", str(iaas_name)) != "0":
                        print("DB not yet updated")
                    if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                            value['container']:
                        helpers.update_triggers_entry(request_id, "1")
                    else:
                        helpers.update_triggers_entry(request_id, "2")
            elif 'node_to_migrate_RAM' in key:
                request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                           "migrate_ram", datetime.datetime.now(), "0")
                print("migrate the ram")
                if not rmq.scale_up_ram(value['container'], value['VM_ip'], value['ram']):
                    print("Unable to migrate the ram")
                    helpers.update_triggers_entry(request_id, "2")
                else:
                    while helpers.store_db_log(id_request, "1", str(iaas_name)) != "0":
                        print("DB not yet updated")
                    if trigger.lxc_migration.delay(value['container'], 3, str(uuid.uuid4()), ip_sdn_controller) == \
                            value['container']:
                        helpers.update_triggers_entry(request_id, "1")
                    else:
                        helpers.update_triggers_entry(request_id, "2")
            elif 'node_to_scaleUp_CPU_RAM' in key:
                request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                           "create_cpu_ram", datetime.datetime.now(), "0")
                print("scale up both of the cpu and the ram")
                if not rmq.scale_up_cpu_ram(value['container'], value['VM_ip'], value['cpu'], value['ram']):
                    print("Unable to scale up both of the cpu and the ram")
                    helpers.update_triggers_entry(request_id, "2")
                else:
                    helpers.update_triggers_entry(request_id, "1")
                while helpers.store_db_log(id_request, "1", str(iaas_name)) != "0":
                    print("DB not yet updated")
            elif 'node_to_scaleUp_CPU' in key:
                request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                           "scale_cpu", datetime.datetime.now(), "0")
                print("scale up the cpu")
                if not rmq.scale_up_cpu(value['container'], value['VM_ip'], value['cpu']):
                    print("Unable to scale ip the cpu")
                    helpers.update_triggers_entry(request_id, "2")
                else:
                    helpers.update_triggers_entry(request_id, "1")
                while helpers.store_db_log(id_request, "1", str(iaas_name)) != "0":
                    print("DB not yet updated")
            elif 'node_to_scaleUp_RAM' in key:
                request_id = helpers.insert_entry_triggers(value['container'], value['VM_ip'], trigger_type,
                                                           "scale_ram", datetime.datetime.now(), "0")
                print("scale up the ram")
                if not rmq.scale_up_ram(value['container'], value['VM_ip'], value['ram']):
                    print("Unable to scale ip the ram")
                    helpers.update_triggers_entry(request_id, "2")
                else:
                    helpers.update_triggers_entry(request_id, "1")
                while helpers.store_db_log(id_request, "1", str(iaas_name)) != "0":
                    print("DB not yet updated")


def decision_sct(solver):
    ntm = {}
    i = 0
    err = 0
    err2 = 0
    ram_cpu = 0
    for key, value in solver.items():
        if bool(solver[key]['containers']):
            for kk, vv in solver[key]['containers'].items():

                # Implementing semaphore logic both the memory and the cpu or nothing
                if vv['live_ram'] > vv['ram'] * ram_threshold:
                    if value['vm_ram'] > 1024:
                        if vv['cpu'] * (vv['live_cpu']) > vv['cpu'] * cpu_threshold:
                            if value['vm_cpu'] > 1:
                                value['vm_ram'] = value['vm_ram'] - 1024
                                value['vm_cpu'] = value['vm_cpu'] - 1
                                ntm['node_to_scaleUp_CPU_RAM_{}'.format(i)] = \
                                    {'VM_ip': key, 'container': kk, 'ram': 1024, 'cpu': 1}
                                err = 1
                                print("SCALE UP BOTH THE MEMORY AND THE CPU")

                            else:
                                err2 = 1
                                ntm['node_to_migrate_CPU_RAM_{}'.format(i)] = \
                                    {'VM_ip': key, 'container': kk, 'cpu': 1, 'ram': 1024}
                                print("Scale up the memory")
                                print("MIGRATE NOT ENOUGH CPU RESOURCES")

                        else:
                            value['vm_ram'] = value['vm_ram'] - 1024
                            ntm['node_to_scaleUp_RAM_{}'.format(i)] = \
                                {'VM_ip': key, 'container': kk, 'ram': 1024}
                            print("SCALE UP THE MEMORY")
                    else:
                        ram_cpu = 1

                if err != 1 and err2 != 1:
                    if vv['cpu'] * (vv['live_cpu']) > vv['cpu'] * cpu_threshold:
                        if value['vm_cpu'] > 1:
                            if vv['live_ram'] > vv['ram'] * ram_threshold:
                                if value['vm_ram'] > 1024:
                                    value['vm_ram'] = value['vm_ram'] - 1024
                                    value['vm_cpu'] = value['vm_cpu'] - 1
                                    print("SCALE UP BOTH THE MEMORY AND THE CPU")
                                else:
                                    ntm['node_to_migrate_CPU_RAM_{}'.format(i)] = \
                                        {'VM_ip': key, 'container': kk, 'ram': 1024, 'cpu': 1}
                                    ram_cpu = 0
                                    print("scale up the cpu")
                                    print("MIGRATE NOT ENOUGH MEMORY RESOURCES")
                            else:
                                value['vm_cpu'] = value['vm_cpu'] - 1
                                ntm['node_to_scaleUp_CPU_{}'.format(i)] = \
                                    {'VM_ip': key, 'container': kk, 'cpu': 1}
                                print("SCALE UP THE CPU")
                        else:
                            if ram_cpu == 1:
                                ntm['node_to_migrate_CPU_RAM_{}'.format(i)] = \
                                    {'VM_ip': key, 'container': kk, 'ram': 1024, 'cpu': 1}
                                ram_cpu = 0
                                print("MIGRATE NOT ENOUGH CPU AND RAM RESOURCES")
                            else:
                                # to be erased
                                ntm['node_to_migrate_CPU_{}'.format(i)] = \
                                    {'VM_ip': key, 'container': kk, 'cpu': 1}
                                print("MIGRATE NOT ENOUGH CPU RESOURCES")
                    else:
                        if ram_cpu == 1:
                            ntm['node_to_migrate_RAM_{}'.format(i)] = \
                                {'VM_ip': key, 'container': kk, 'ram': 1024}
                            ram_cpu = 0
                            print("MIGRATE NOT ENOUGH MEMORY RESOURCES")

                else:
                    err = 0
                    err2 = 0
                i += 1
    return ntm
