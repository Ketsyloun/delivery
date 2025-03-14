import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

app = Celery('tasks', broker=os.getenv("CELERY_BROKER_URL"),
             backend=os.getenv("CELERY_RESULT_BACKEND"))

app.conf.update(
    timezone='Europe/Moscow',
    enable_utc=True,
    worker_concurrency=4,
    worker_class='gevent',
)

app.conf.beat_schedule = {
    'fetch-exchange-rate-every-day': {
        'task': 'delivery.core.celery_tasks.getting_the_dollar_rate',
        'schedule': crontab(hour=20, minute=0),
    },
}