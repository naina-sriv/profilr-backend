# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
import tempfile

from pydantic import BaseModel
from dotenv import load_dotenv
import traceback

from app.utils import read_csv_safely, analyze_csv
from app.config import setup_cors
load_dotenv()

app = FastAPI(
    title="CSV Profiler API",
    description="Upload a CSV file, and analyze it.",
    version="2.0.0"
)
    
@app.get("/")
def home():
    return {"message": "CSV Profiler API is running!"}



@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    global Active_report
    """Upload CSV and return quick profiling info."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        contents = await file.read()

        try:
            df = pd.read_csv(io.BytesIO(contents), encoding_errors="replace")
        except Exception:
            df = pd.read_csv(io.BytesIO(contents), encoding="latin1", errors="replace")

        if df.empty:
            raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")

        df = df.replace({pd.NA: None, float("nan"): None})

        report = analyze_csv(df)
        Active_report=report

        return {"filename": file.filename, "report": report}

    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}\nTraceback:\n{tb}")



