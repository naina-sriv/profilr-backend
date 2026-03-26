# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import io
import os
import tempfile
import json
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv
import traceback
from app.utils import read_csv_safely, analyze_csv
from app.config import setup_cors
load_dotenv()
Active_report = None
app = FastAPI(
    title="CSV Profiler API",
    description="Upload a CSV file, and analyze it.",
    version="2.0.0"
)
setup_cors(app)
    
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


@app.get("/export/")
def export_report():
    global Active_report
    if Active_report is None:
        raise HTTPException(status_code=404, detail="No report available. Upload a CSV first.")
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(Active_report, f, indent=2)
    return FileResponse(filename, media_type="application/json", filename="report.json")
