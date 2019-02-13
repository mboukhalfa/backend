from mirai_project.celery import app
from dsmirai import linux_container_creation, linux_container_migration

@app.task
def lxc_creation():
    return linux_container_creation.create()

@app.task
def lxc_migration(container, iaas):
    return linux_container_migration.migrate(container, int(num_iteration), iaas)
