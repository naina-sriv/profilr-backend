## Pipeline Architecture

### Overview
CSV Profiler is a data profiling pipeline that ingests CSV files,
extracts and transforms data, and delivers structured analysis reports.

### Stages

1. Ingest
   - User uploads a CSV file via Streamlit frontend
   - FastAPI backend receives the file at POST /upload-csv/

2. Extract
   - chardet detects file encoding automatically
   - pandas reads the CSV into a DataFrame

3. Transform
   - Missing values, outliers, correlations computed via utils.py
   - Data quality issues flagged automatically

4. Export
   - Structured JSON report returned to frontend
   - Report stored in memory as Active_report

5. Deliver
   - GET /export/ saves report as timestamped JSON to /reports/
   - FileResponse delivers the file to the user for download

### Data Flow
CSV Upload → /upload-csv/ → read_csv_safely() → analyze_csv() → JSON → /export/ → file download

### Tech Stack
- Backend: FastAPI, Uvicorn
- Data Processing: Pandas, NumPy, Chardet
- Frontend: Streamlit