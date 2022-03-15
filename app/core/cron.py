from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from app.api.utils import load_curreny


def hello():
    print("hello")


jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
executors = {"default": ThreadPoolExecutor(20)}
job_defaults = {"coalesce": False, "max_instances": 3}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, timezone=utc)
scheduler.add_job(
    load_curreny,
    "cron",
    minute=30,
    id="load_currency",
    replace_existing=True,
    max_instances=1,
    misfire_grace_time=900,
)
