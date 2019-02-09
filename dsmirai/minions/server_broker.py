#!/usr/bin/env python
import subprocess
import pika
import linux_container as lxc_driver
import virtual_machine as system_driver
import customized_sdn_container as sdn
import core_migration as migration
import Triggers.resource_availability_trigger as rat
import Triggers.service_consumption_trigger as sct
import sys
import scale_up as scale_up


class ServerBroker(object):

    def __init__(self, exchange_key='main_queue', ip_mngmt='195.148.125.125', user_name='mqadmin',
                 password='mqadminpassword'):
        self.credentials = pika.PlainCredentials(user_name, password)
        self.parameters = pika.ConnectionParameters(ip_mngmt, 5672, '/', self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)

        # Prepare the exchange and wait for a request from the client
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange_key, exchange_type='direct')

        result = self.channel.queue_declare(exclusive=True)
        self.channel.queue_declare(queue=str(system_driver.get_ip()) + exchange_key.split('_')[0], durable=True)
        queue1 = 'star' + exchange_key.split('_')[0]
        queue2 = str(system_driver.get_ip())
        self.channel.queue_bind(exchange=exchange_key, queue=str(system_driver.get_ip()) + exchange_key.split('_')[0],
                                routing_key=queue1)
        self.channel.queue_bind(exchange=exchange_key, queue=str(system_driver.get_ip()) + exchange_key.split('_')[0],
                                routing_key=queue2)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=str(system_driver.get_ip()) + exchange_key.split('_')[0])

        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()

    def on_request(self, ch, method, props, body):

        print(" I received: {}".format(body))
        print("my correlation id is: {}".format(props.correlation_id))
        x = body.decode().split("#")
        response = ""
        if x[0] == "admin":
            subprocess.Popen(['python3', '/root/minion/server_broker.py', str(x[1]) + "_queue"], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
            response = 1
            print("The response is equal to: {}".format(response))
        elif x[0] == "available_resource_creation":
            print("***********The Host Node Server Broker -- verify_resource_creation--***********")
            cpu, ram, disk = system_driver.resource_availability()
            response = str(system_driver.get_ip()) + "#" + str(cpu) + "#" + str(ram) + "#" + str(disk)
        elif x[0] == "create":
            print("***********The Host Node Server Broker -- create_container --***********")
            system_driver.default_bridge()
            print("calling the creation library .....")
            response = sdn.create(x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8])
            print("The response is equal to: {}".format(response))
        elif x[0] == "container_resources":
            print("***********The Host Node Server Broker -- get_container_resources --***********")
            print("getting the cpu, ram information .....")
            cpu, ram = lxc_driver.get_container_resources(x[1])
            response = str(system_driver.get_ip()) + "#" + str(cpu) + "#" + str(ram)
            print("The response is equal to: {}".format(response))
        elif x[0] == "available_resource_migration":
            print("***********The Host Node Server Broker -- verify_resource_migration --***********")
            if str(system_driver.get_ip()) != x[1]:
                cpu, ram, disk = system_driver.resource_availability()
                response = str(system_driver.get_ip()) + "#" + str(cpu) + "#" + str(ram) + "#" + str(disk)
            else:
                response = str(system_driver.get_ip()) + "#" + str(0) + "#" + str(0) + "#" + str(0)
        elif x[0] == "container_image":
            print("***********The Host Node Server Broker -- container_image --***********")
            print("getting the image name .....")
            response = migration.container_image(x[1])
        elif x[0] == "part_migration_check":
            print("***********The Host Node Server Broker -- part_migration_check --***********")
            print("searching for partial migration action .....")
            if migration.target_container_image(x[1]):
                response = migration.partial_migration_preparation(x[1], x[2])
        elif x[0] == "migration":
            print("***********The Host Node Server Broker -- full_migration --***********")
            print("Full-Migration Process .....")
            response = migration.migrate(x[1], x[2], x[3])
        elif x[0] == "validate_migration":
            print("***********The Host Node Server Broker -- validate_migration --***********")
            print("Validate-Migration Process .....")
            response = migration.validate_migration(x[1], x[2])
        elif x[0] == "rat_trigger":
            print("***********The Host Node Server Broker -- rat_trigger --***********")
            response = rat.container_list()
        elif x[0] == "directive_rat_trigger":
            print("***********The Host Node Server Broker -- directive_rat_trigger --***********")
            response = rat.container_list()
        elif x[0] == "sct_trigger":
            print("***********The Host Node Server Broker -- sct_trigger --***********")
            response = sct.container_live_resources()
        elif x[0] == "directive_sct_trigger":
            print("***********The Host Node Server Broker -- directive_sct_trigger --***********")
            response = sct.container_live_resources()
        elif x[0] == "scale_up_cpu_ram":
            print("***********The Host Node Server Broker -- scale_up_cpu_ram --***********")
            response = scale_up.scale_up_cpu_ram(x[1], x[2], x[3])
        elif x[0] == "scale_up_cpu":
            print("***********The Host Node Server Broker -- scale_up_cpu --***********")
            response = scale_up.scale_up_cpu_full(x[1], x[2])
        elif x[0] == "scale_up_ram":
            print("***********The Host Node Server Broker -- scale_up_ram --***********")
            response = scale_up.scale_up_ram_full(x[1], x[2])
        elif x[0] == "container_dashboard_resources":
            print("***********The Host Node Server Broker -- container_dashboard_resources --***********")
            container_ip, cpu, ram, disk = lxc_driver.container_dashboard_resources(x[1])
            response = str(container_ip) + "#" + str(cpu) + "#" + str(ram) + "#" + str(disk)
        elif x[0] == "environment_cleaner":
            print("***********The Host Node Server Broker -- environment_cleaner --***********")
            subprocess.Popen(['python3', '/root/minion/environment_cleaner.py'], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
            response = 1

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    c = ServerBroker(sys.argv[1])
