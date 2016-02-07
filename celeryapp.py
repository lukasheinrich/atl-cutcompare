from celery import Celery
app = Celery('dockercompare')
app.config_from_object('celeryconfig')
