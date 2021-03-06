#!/usr/bin/env python
import pika
import uuid
import ast
from dsmirai.persistent_model import helpers
import random
import time


class ClientBroker(object):
    def __init__(self, exchange_key='main_queue', ip_mngmt='195.148.125.125', user_name='mqadmin',
                 password='mqadminpassword'):
        """

        :param exchange_key:
        :param ip_mngmt:
        :param user_name:
        :param password:
        """

        self.credentials = pika.PlainCredentials(user_name, password)
        self.parameters = pika.ConnectionParameters(ip_mngmt, 5672, '/', self.credentials)
        self.connection = pika.BlockingConnection(self.parameters)
        self.exchange = exchange_key
        self.corr_id = ""

        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        print("the callback queue is: {}".format(self.callback_queue))
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
        self.response = None
        self.counter = 0
        self.sct = {}
        self.rat = {}
        self.magic = []

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            print("my correlation id in the Client is: {}".format(props.correlation_id))
            self.counter += 1
            print(self.counter)
            self.response = body
            print(self.response)
            print(type(self.response))
            self.magic.append(self.response.decode())

    def management_task(self, ip, action):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        message = "admin#{}".format(action)
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=ip,
                                   properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                   correlation_id=self.corr_id, ),
                                   body=str(message))
        while self.response is None:
            self.connection.process_data_events()
        self.counter = 0
        self.magic = []
        if ast.literal_eval(self.response.decode()) == 1:
            self.response = None
            return True
        return False

    def verify_resource(self, routing_key, type, ip_source="None"):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')

        print("***********The Global Orchestrator Client Broker -- verify_resource --***********")
        if type == "creation":
            message = 'available_resource_creation'
        else:
            message = 'available_resource_migration#{}'.format(ip_source)
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                   correlation_id=self.corr_id, ),
                                   body=str(message))

        table_statistics = []
        if "star" in routing_key:
            while self.counter < helpers.number_minions():
                self.connection.process_data_events()
            print("the main number of -- verify_resource --:")
            print(helpers.number_minions())
            for i in range(len(self.magic)):
                print("The value of the response of -- verify_resource -- is: ")
                print(self.magic[i].split("#"))
                x = self.magic[i].split("#")
                table_statistics.append((x[0], int(x[1]), int(x[2]), float(x[3])))
        else:
            while self.response is None:
                self.connection.process_data_events()
            print("The value of the response of -- verify_resource_directive -- is: ")
            print(self.magic[0].split("#"))
            x = self.magic[0].split("#")
            table_statistics.append((x[0], int(x[1]), int(x[2]), float(x[3])))

        self.magic = []
        self.counter = 0
        print("awesome end of -- verify_resource --")
        return table_statistics

    def create_container(self, container_name, client, cpu, ram, server_port_number, server_ip_address,
                         client_port_number, client_ip_address, creation_ip_address):
        # preparing and sending a request to the Minions
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        print("***********The Global Orchestrator Client Broker -- create_container --***********")
        message = "create#{}#{}#{}#{}#{}#{}#{}#{}#{}".format(container_name, client, cpu, ram, server_port_number,
                                                             server_ip_address, client_port_number,
                                                             client_ip_address, creation_ip_address)
        print("sending ... {}".format(message))
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=creation_ip_address,
                                   properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                   correlation_id=self.corr_id, ),
                                   body=str(message))

        while self.response is None:
            self.connection.process_data_events()
        print("The value of the response of -- create_container -- is {}: ".format(ast.literal_eval(
            self.response.decode())))
        self.counter = 0
        self.magic = []
        print("awesome end of -- create_container --")
        return ast.literal_eval(self.response.decode())

    def get_container_resources(self, container_name, ip_source):

        # preparing and sending a request to the Minions
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')

        print("***********The Global Orchestrator Client Broker -- get_container_resources --***********")
        message = "container_resources#{}".format(container_name)
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=ip_source,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(message))

        # Wait until the answer and execute consuming part (on_response)
        # I should add an iterative number to handle several machine
        table_statistics = []
        while self.response is None:
            self.connection.process_data_events()

        print(self.magic[i].split("#"))
        x = self.magic[i].split("#")
        table_statistics.append((x[0], int(x[1]), int(x[2])))

        self.counter = 0
        self.magic = []
        print("awesome end of -- get_container_resources --")
        return table_statistics

    def get_container_image(self, ip_address, container_name):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        print("***********The Global Orchestrator Client Broker -- get_container_image --***********")
        message = "container_image#{}".format(container_name)
        print("sending ... {}".format(message))
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=ip_address,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(message))

        while self.response is None:
            self.connection.process_data_events()
        self.counter = 0
        self.magic = []
        print("awesome end of -- get_container_image --")
        return self.response.decode()

    def part_migration_check(self, lxc_image, ip_address_destination, container_name):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        print("***********The Global Orchestrator Client Broker -- part_migration_check --***********")

        message = "part_migration_check#{}#{}".format(lxc_image, container_name)
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=ip_address_destination,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(message))

        while self.response is None:
            self.connection.process_data_events()
        self.counter = 0
        self.magic = []
        print("awesome end of -- part_migration_check --")
        return ast.literal_eval(self.response.decode())

    def migration(self, container_name, ip_destination, num_iteration, ip_source):

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        print("***********The Global Orchestrator Client Broker -- part_migration --***********")

        message = "migration#{}#{}#{}".format(container_name, ip_destination, num_iteration)
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=ip_source,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(message))

        while self.response is None:
            self.connection.process_data_events()
        self.counter = 0
        self.magic = []
        print("awesome end of -- part_migration --")
        return ast.literal_eval(self.response.decode())

    def validate_migration(self, container_name, ip_source, ip_client):
        self.response = None
        self.magic = []
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        print("***********The Global Orchestrator Client Broker -- validate_migration --***********")

        message = "validate_migration#{}#{}".format(container_name, ip_client)
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=ip_source,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(message))

        while self.response is None:
            self.connection.process_data_events()
        self.counter = 0
        print("awesome end of -- validate_migration --")
        return ast.literal_eval(self.response.decode())

    def rat_trigger(self, routing_key):
        self.response = None
        self.rat = {}
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')

        print("*********** The Global Orchestrator Client Broker -- rat_trigger --***********")

        message = "rat_trigger"
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(message))

        if "star" in routing_key:
            while self.counter < helpers.number_minions():
                self.connection.process_data_events()
            print("the main number of -- rat_trigger --:")
            print(helpers.number_minions())
            for i in range(len(self.magic)):
                print("The value of the response of -- rat_trigger -- is: ")
                print(self.magic[i])
                self.rat.update(ast.literal_eval(self.magic[i]))
        else:
            while self.response is None:
                self.connection.process_data_events()
            print("The value of the response of -- directive_rat_trigger -- is: ")
            print(self.magic[0])
            self.rat.update(ast.literal_eval(self.magic[0]))
        self.counter = 0
        self.magic = []
        print("awesome end of -- rat_trigger --")
        return self.rat

    def sct_trigger(self, routing_key):
        self.response = None
        self.sct = {}
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')

        print("***********The Global Orchestrator Client Broker -- sct_trigger --***********")

        message = "sct_trigger"
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=str(message))

        if "star" in routing_key:
            while self.counter < helpers.number_minions():
                self.connection.process_data_events()
            print("the main number of -- sct_trigger --:")
            print(helpers.number_minions())
            for i in range(len(self.magic)):
                print("The value of the response of -- sct_trigger -- is: ")
                print(self.magic[i])
                self.sct.update(ast.literal_eval(self.magic[i]))
        else:
            while self.response is None:
                self.connection.process_data_events()
            print("The value of the response of -- directive_sct_trigger -- is: ")
            print(self.magic[0])
            self.sct.update(ast.literal_eval(self.magic[0]))
        self.counter = 0
        self.magic = []
        print("awesome end of -- sct_trigger --")
        return self.sct

    def scale_up(self, container_name, creation_ip_address, type_scale_up, cpu, ram):
        # preparing and sending a request to the Minions
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        print("***********The Global Orchestrator Client Broker -- scale_up --***********")
        message = "{}#{}#{}#{}".format(type_scale_up, container_name, cpu, ram)
        print("sending ... {}".format(message))
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=creation_ip_address,
                                   properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                   correlation_id=self.corr_id, ),
                                   body=str(message))

        while self.response is None:
            self.connection.process_data_events()

        print("The value of the response of -- scale_up -- is {}: ".format(ast.literal_eval(
            self.response.decode())))
        self.counter = 0
        self.magic = []
        print("awesome end of -- scale_up --")
        return ast.literal_eval(self.response.decode())

    def container_dashboard_resources(self, container_name, ip_address):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')

        print("***********The Global Orchestrator Client Broker -- container_dashboard_resources --***********")
        message = 'container_dashboard_resources#{}'.format(container_name)
        print("sending ... {}".format(message))

        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key=ip_address,
                                   properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                   correlation_id=self.corr_id, ),
                                   body=str(message))

        while self.response is None:
            self.connection.process_data_events()
        print("The value of the response of -- container_dashboard_resources -- is: ")
        print(self.magic[0].split("#"))
        x = self.magic[0].split("#")
        self.magic = []
        self.counter = 0
        print("awesome end of -- container_dashboard_resources --")
        return x[0], float(x[1]), float(x[2]), float(x[3])

    def environment_cleaner(self):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.exchange_declare(exchange=self.exchange,
                                      exchange_type='direct')
        message = "environment_cleaner"
        self.channel.basic_publish(exchange=self.exchange,
                                   routing_key='star' + self.exchange.split('_')[0],
                                   properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                   correlation_id=self.corr_id, ),
                                   body=str(message))

        while self.counter < helpers.number_minions():
            self.connection.process_data_events()

        print("the main number of -- environment_cleaner --:")
        print(helpers.number_minions())
        print("The value of the response of -- environment_cleaner -- is: ")
        print(self.magic)
        self.counter = 0
        self.magic = []
        return True
