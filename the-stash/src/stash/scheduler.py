from __future__ import annotations

import logging
from datetime import datetime

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from .main import publish_once

LOGGER = logging.getLogger(__name__)


def start_scheduler(timezone_name: str = "America/Los_Angeles") -> None:
	"""Run a scheduler that triggers publish at 4:20 AM and 4:20 PM."""
	scheduler = BlockingScheduler(timezone=pytz.timezone(timezone_name))

	def _job():
		LOGGER.info("Scheduler triggering publish at %s", datetime.now())
		publish_once()

	# 4:20 AM and 4:20 PM local time
	scheduler.add_job(_job, "cron", hour=4, minute=20, id="four_twenty_am", replace_existing=True)
	scheduler.add_job(_job, "cron", hour=16, minute=20, id="four_twenty_pm", replace_existing=True)

	LOGGER.info("Starting scheduler for 4:20 AM/PM jobs")
	scheduler.start()

