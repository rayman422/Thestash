from __future__ import annotations

from datetime import datetime

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import load_config_from_env
from .main import run_publish


def _job():
	cfg = load_config_from_env()
	# Use configured provider if set in env; default is fallback if no key
	run_publish(cfg, provider=None, model=None, no_ai=False, offline=False)


def start_scheduler() -> None:
	cfg = load_config_from_env()
	tz = pytz.timezone(cfg.site.timezone)
	scheduler = BlockingScheduler(timezone=tz)

	# 4:20 AM and 4:20 PM
	scheduler.add_job(_job, CronTrigger(hour=4, minute=20, timezone=tz), id="stash-0420")
	scheduler.add_job(_job, CronTrigger(hour=16, minute=20, timezone=tz), id="stash-1620")

	print(f"Scheduler starting with timezone {cfg.site.timezone}...")
	try:
		scheduler.start()
	except (KeyboardInterrupt, SystemExit):
		print("Scheduler stopped.")

