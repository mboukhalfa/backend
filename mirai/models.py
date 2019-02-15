from django.db import models
import datetime


class IaaS(models.Model):
    IAAS_STATE_CHOICES = (
        (0, 'off'),
        (1, 'on'),)

    iaas_name = models.TextField(unique=True, max_length=120)
    iaas_ip = models.GenericIPAddressField(unique=True)
    iaas_state = models.IntegerField(null=True, choices=IAAS_STATE_CHOICES)
    iaas_configuration = models.TextField(
        max_length=120, blank=True)
    iaas_date_discovery = models.DateTimeField(default=datetime.datetime.now)
    iaas_date_configuration = models.DateTimeField(
        default=datetime.datetime.now)
    iaas_owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class IaaSConsumption(models.Model):
    iaas = models.ForeignKey(
        IaaS, related_name='consumptions', on_delete=models.CASCADE)
    iaas_ram = models.IntegerField()
    iaas_disk = models.FloatField()
    iaas_cpu = models.IntegerField()
    iaas_time = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        ordering = ['-iaas_time']


class Container(models.Model):
    iaas = models.ForeignKey(IaaS, on_delete=models.CASCADE, null=True)
    container_name = models.TextField(max_length=120)
    cpu = models.TextField(max_length=120, default="1")
    ram = models.TextField(max_length=120, default="512M")
    application_type = models.TextField(max_length=120, default="video")
    ip_address = models.TextField(max_length=120,null=True)
    port = models.IntegerField(null=True)


class Client(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    container_name = models.TextField(max_length=120)
    ip_address = models.TextField(max_length=120)
    port = models.IntegerField()


class Monitoring(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    real_time = models.DateTimeField(default=datetime.datetime.now)
    cpu_data = models.IntegerField()
    ram_data = models.IntegerField()


class Triggers(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    trigger_type = models.TextField(max_length=120)
    trigger_action = models.TextField(max_length=120, default="api_call")
    trigger_time = models.DateTimeField(default=datetime.datetime.now)
    trigger_result = models.TextField(max_length=120, null=True)


class Log(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    result = models.TextField(max_length=50)
    code = models.TextField(max_length=120)
    usage = models.TextField(max_length=120)

    def __str__(self):
        return "container: {} result: {} code: {}  usage: {} ".format(self.container, self.result, self.code, self.usage)
