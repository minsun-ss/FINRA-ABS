from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
import extractMonthlyData
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

sched = BlockingScheduler()
q = Queue(connection=conn)

@sched.scheduled_job('cron', day=5)
def scheduled_job():
    q.enqueue(extractMonthlyData.run_extraction())
    print('This job is run on the 5th of every month.')
    sys.stdout.flush()

sched.start()
