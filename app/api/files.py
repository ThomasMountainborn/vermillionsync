import shutil
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.security import get_current_user
from app.db import get_db
from app.models.file import UploadedFile


def get_existing_record(name: str, db: Session):
    statement = select(UploadedFile).where(UploadedFile.original_filename == name)
    result = db.execute(statement).scalar_one_or_none()
    return result

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"ping":"pong"}

@router.post("/upload/")
async def upload(request: Request, file: UploadFile, db: Session = Depends(get_db)):   
    delta = timedelta(minutes=2)
    SIZE_LIMIT = 5*1024*1024
    content_length = request.headers.get("content-length")

    if content_length and int(content_length) > SIZE_LIMIT:
        raise HTTPException(status_code=413, detail="File size limit exceeded.")

    # check if empty file
    if file.size == 0:
        raise HTTPException(status_code=400, detail="Empty file not allowed.")
    
    # check if file is too large (compared in BYTES)
    if file.size > SIZE_LIMIT:
        raise HTTPException(status_code=413, detail="File size limit exceeded.")

    # path to store files at
    upload_dir = Path("./data/uploads")

    try:
        # create dir if it doesnt exist
        upload_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise HTTPException(status_code=500, detail="Failed to prepare upload directory")

    # complete file path(relative) to the file
    destination = upload_dir / f"{file.filename}"
    # Delete the existing file. 
    destination.unlink(missing_ok=True)

    try:
        # copy file data in chunks in bytes so huge data is not loaded into RAM
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    uploaded_file = get_existing_record(file.filename, db)
    createdNewRecord = False
    if uploaded_file is None:
        createdNewRecord = True
        uploaded_file = UploadedFile(
                                original_filename=file.filename,
                                expires_at = datetime.now(UTC) + delta if delta else None,
                                )
    else:
        uploaded_file.expires_at = datetime.now(UTC) + delta if delta else None,

    try:
        if createdNewRecord:
            db.add(uploaded_file)
        db.commit()
    except Exception:
        destination.unlink(missing_ok=True) # remove orphaned file on disk
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to commit to DB.")
    
    return {
        "filename": file.filename,
        "saved_to": str(destination),
        "valid_till": uploaded_file.expires_at,
        "submitted_at": datetime.now(UTC)
    }

@router.get("/download/{code}")
async def download(name: str, db: Session = Depends(get_db)):
    statement = select(UploadedFile).where(UploadedFile.original_filename == name)
    file_record = db.execute(statement).scalar_one_or_none()

    if file_record is None:
        raise HTTPException(status_code=404, detail="File not found")

    if file_record.expires_at and file_record.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=404, detail="File not found")

    extension = Path(file_record.original_filename)

    path= Path("./data/uploads/") / f"{name}"
    filename= file_record.original_filename

    if not path.exists():
        db.delete(file_record)
        db.commit()
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=path,
        filename=filename
    )