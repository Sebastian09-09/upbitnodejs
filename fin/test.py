from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

def my_job(index):
    print(f"Job {index} executed at {datetime.datetime.now()}")

# Create an instance of the scheduler
scheduler = BlockingScheduler()

# Add the job to start at the :01 second mark and run every 5 seconds

scheduler.add_job(
my_job,
CronTrigger(second=f'01/5'), 
args=(1,)
)

scheduler.add_job(
my_job,
CronTrigger(second=f'02/5'), 
args=(2,)
)

scheduler.add_job(
my_job,
CronTrigger(second=f'03/5'), 
args=(3,)
)

# Start the scheduler
scheduler.start()