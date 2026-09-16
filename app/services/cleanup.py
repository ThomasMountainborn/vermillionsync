from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from pathlib import Path
from app.db import get_db
from app.models.file import UploadedFile
from fastapi import Depends

def cleanUp(db: Session = Depends(get_db)):
    stmnt = select(UploadedFile).where(
        UploadedFile.expires_at < datetime.now(UTC)
    )
    
    result = db.execute(stmnt).scalars().all()

    for file in result:
        db.delete(file)
    
    upload_dir = Path("./data/uploads")

    for file in result:
        # complete filename on disk
        name = file.original_filename
        file_path = upload_dir / name
        # no need to wrap in try block as it is safe automatically
        file_path.unlink(missing_ok=True)

    db.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(cleanUp, "interval", minutes=1)