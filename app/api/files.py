import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from app.settings import get_settings
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/upload")
async def upload(secret: str, request: Request, file: UploadFile = File(...)):   
    if secret != get_settings().api_key:
        raise HTTPException(status_code=401)

    SIZE_LIMIT = 10*1024*1024
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
        
    return {
        "filename": file.filename,
        "saved_to": str(destination),
        "valid_till": datetime.now(UTC) + timedelta(seconds=90),
        "submitted_at": datetime.now(UTC)
    }

@router.get("/download/{name}")
async def download(name: str):
    path = Path("./data/uploads/") / f"{name}"
    filename = name

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=path,
        filename=filename
    )
