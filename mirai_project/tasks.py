from mirai_project.celery import app
from dsmirai import iaas_deamon
from dsmirai import rat_control
from dsmirai import sct_control
from dsmirai.persistent_model import dashboard_helper
from dsmirai import linux_container_creation
from dsmirai import linux_container_migration
from dsmirai import onos_cleaner

from mirai.models import Log


@app.task
def iaas_daemon():
    iaas_deamon.iaas_discovery()
    return


@app.task
def rat_daemon():
    rat_control.rat_trigger()
    return


@app.task
def sct_daemon(iaas_name="None"):
    sct_control.sct_trigger(iaas_name)
    return


@app.task
def api_rat(iaas_name="None"):
    rat_control.api_rat_trigger(iaas_name)
    return


@app.task
def api_sct(iaas_name="None"):
    sct_control.api_sct_trigger(iaas_name)
    return


@app.task
def iaas_consumption():
    dashboard_helper.iaas_resource_consumption()
    return


@app.task
def clean_onos_env():
    onos_cleaner.clean_onos()
    return


@app.task
def lxc_creation():
    print('labess 3lik 3omri labesssss')
    # Log.objects.create(server_name = "nonretour",result = "test",code = "test",client_name = "test",token = "test",usage = "test")
    # return linux_container_creation.create()

@app.task
def lxc_migration(container_name, num_iteration, token, ip_sdn_controller, target_cloud="None"):
    return linux_container_migration.migrate(container_name, int(num_iteration), token, ip_sdn_controller, target_cloud)
