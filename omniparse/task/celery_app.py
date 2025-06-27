from celery import Celery

celery_app = Celery(
    "worker",
    broker="pyamqp://guest:guest@localhost:5673//",
    backend="rpc://"
)

celery_app.autodiscover_tasks(['omniparse.task'])

# 👇 force import to ensure task registration
from omniparse.task import parse_doc
