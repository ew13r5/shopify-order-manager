import os

from celery import Celery

celery_app = Celery("worker")

celery_app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    result_expires=3600,
    worker_send_task_events=True,
    task_send_sent_event=True,
)

celery_app.autodiscover_tasks(["tasks"])
