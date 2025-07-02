from celery import Celery
from omniparse import load_omnimodel


load_omnimodel(load_documents=True, load_media= False, load_web=False)

celery_app = Celery(
    "worker",
    # broker="pyamqp://guest:guest@localhost:5673//",
    # backend="rpc://"
    broker="redis://localhost:6380/0",
    backend="redis://localhost:6380/0",

)

celery_app.autodiscover_tasks(['omniparse.task'])

# 👇 force import to ensure task registration
from omniparse.task import parse_doc
