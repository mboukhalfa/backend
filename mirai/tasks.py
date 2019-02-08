from mirai_project.celery import app
from dsmirai import linux_container_creation

@app.task
def lxc_creation():
    print('ttttttttttttttttttttttttttttttttttttttttttt')
    return linux_container_creation.create()

