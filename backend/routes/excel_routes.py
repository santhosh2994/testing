from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
import pandas as pd
import numpy as np
import hashlib
from pathlib import Path

from database.connection import SessionLocal
from database.models import Title, BulkUploadRun
from backend.services.excel_deduper import dedupe_excel
from backend.services.embedding_service import get_embedding

router = APIRouter(prefix="/excel", tags=["Excel"])

TEMP_DIR = Path(__file__).parent.parent.parent / "temp" / "uploads"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def process_file_bulk_bg(file_path: str, filename: str):
    db = SessionLocal()
    try:
        file_hash = hash_file(file_path)

        existing_run = (
            db.query(BulkUploadRun)
            .filter(BulkUploadRun.file_hash == file_hash)
            .first()
        )

        if existing_run:
            print("Duplicate file upload skipped:", filename)
            return

        df = pd.read_excel(file_path)
        
        # Get first column and remove NaN/empty values
        first_col = df.columns[0]
        df = df[[first_col]].dropna()
        df = df[df[first_col].astype(str).str.strip() != '']
        df = df[df[first_col].astype(str).str.lower() != 'nan']

        unique_df, clusters = dedupe_excel(
            df,
            column=None,
            ignore_numbers=True
        )

        existing_norms = {
            r[0] for r in db.query(Title.normalized_title).all()
        }

        saved = 0

        for _, row in unique_df.iterrows():
            normalized = row["normalized"]
            
            # Skip empty or nan normalized values
            if not normalized or normalized == 'nan' or pd.isna(normalized):
                continue

            if normalized in existing_norms:
                continue

            vec = get_embedding(normalized)
            vec_bytes = np.array(vec, dtype=np.float32).tobytes()

            db.add(
                Title(
                    title=row[first_col],
                    normalized_title=normalized,
                    embedding=vec_bytes,
                    is_duplicate=0
                )
            )

            existing_norms.add(normalized)
            saved += 1

        run = BulkUploadRun(
            filename=filename,
            file_hash=file_hash,
            processed=len(df),
            saved=saved,
            duplicates=len(df) - saved,
        )

        db.add(run)
        db.commit()

        print({
            "file": filename,
            "processed": len(df),
            "saved": saved,
            "duplicates": len(df) - saved,
            "clusters": {k: v for k, v in clusters.items() if len(v) > 1}
        })

    finally:
        db.close()


@router.post("/bulk-upload")
async def bulk_upload(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )

    temp_path = TEMP_DIR / file.filename

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    background_tasks.add_task(
        process_file_bulk_bg,
        str(temp_path),
        file.filename
    )

    return {
        "status": "processing",
        "filename": file.filename
    }
