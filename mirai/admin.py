from django.contrib import admin
from mirai.models import IaaS, IaaSConsumption

# Register your models here.
admin.site.register(IaaS)
admin.site.register(IaaSConsumption)
