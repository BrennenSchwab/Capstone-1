from apscheduler.schedulers.blocking import BlockingScheduler
from seed import seed_basic_player_info

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon', hour=1)
def scheduled_job():
    seed_basic_player_info()

sched.start()