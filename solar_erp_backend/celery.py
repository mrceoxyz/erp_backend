import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_erp_backend.settings')

app = Celery('solar_erp_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-overdue-invoices-daily': {
        'task': 'invoices.tasks.check_overdue_invoices',
        'schedule': crontab(hour=9, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# solar_erp/__init__.py
from .celery import app as celery_app

