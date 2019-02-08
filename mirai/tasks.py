from mirai_project.celery import app
from mirai.models import Log

@app.task
def test():
    Log.objects.create(server_name = "cheikh",result = "test",code = "test",client_name = "test",token = "test",usage = "test")
    print('labess 3lik 3omri labesssss')
    return 