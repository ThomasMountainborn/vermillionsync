from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, UTC
from pathlib import Path
import os

def cleanUp():
    now = datetime.now(UTC)
    upload_dir = Path("./data/uploads")
    for file in os.scandir(upload_dir):
        if file.is_dir():
            continue
        creationTime = datetime.fromtimestamp(os.path.getctime(file.path), UTC)
        if (now-creationTime).total_seconds() > 90:
            Path(file.path).unlink(missing_ok=True)


scheduler = BackgroundScheduler()
scheduler.add_job(cleanUp, "interval", seconds=10)