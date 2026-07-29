import streamlit as st
import requests
import pandas as pd
import json

API_URL = "https://profilr-backend-teal.vercel.app"

st.set_page_config(page_title="CSV Profiler", layout="centered")
st.title("CSV Profiler")
st.write("Upload a CSV file and get instant profiling insights.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    st.success(f"Selected file: **{uploaded_file.name}**")

    try:
        df_preview = pd.read_csv(uploaded_file, nrows=5)
        st.subheader("Data Preview")
        st.dataframe(df_preview)
        uploaded_file.seek(0)
    except Exception as e:
        st.warning(f"Could not load data preview: {e}")

    if st.button("Analyze CSV"):
        with st.spinner("Uploading and analyzing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{API_URL}/upload-csv/", files=files)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis complete!")
                    st.subheader("File")
                    st.write(data["filename"])
                    
                    st.subheader("Report")
                    report = data["report"]
                    
                    st.write("Dataset Info")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Rows", report.get("dataset_info", {}).get("rows", 0))
                    col2.metric("Columns", report.get("dataset_info", {}).get("columns", 0))
                    col3.metric("Missing (%)", report.get("dataset_info", {}).get("missing_percent", 0.0))
                    col4.metric("Memory (MB)", report.get("memory_usage_mb", 0.0))
                    
                    st.write("Column Summary")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Numeric", report.get("column_summary", {}).get("numeric", 0))
                    c2.metric("Categorical", report.get("column_summary", {}).get("categorical", 0))
                    c3.metric("Boolean", report.get("column_summary", {}).get("boolean", 0))
                    
                    st.write("Column Insights & Quality")
                    issues = report.get("data_quality_issues", [])
                    if issues:
                        for issue in issues:
                            st.warning(issue)
                    else:
                        st.info("No major issues found.")
                        
                    const_cols = report.get("constant_columns", [])
                    if const_cols:
                        st.info(f"Constant Columns (single value): {', '.join(const_cols)}")
                    
                    empty_cols = report.get("empty_columns", [])
                    if empty_cols:
                        st.info(f"Empty Columns (all missing): {', '.join(empty_cols)}")
                        
                    st.write("Column Details")
                    col_details = []
                    for col in report.get("columns", []):
                        detail = {
                            "Column": col,
                            "Type": report.get("dtypes", {}).get(col, ""),
                            "Missing Values": report.get("missing_values", {}).get(col, 0)
                        }
                        if "summary" in report and col in report["summary"]:
                            detail.update(report["summary"][col])
                        if "outliers" in report and col in report["outliers"]:
                            detail["Outliers"] = report["outliers"][col]
                        if "distribution" in report and col in report["distribution"]:
                            detail["Skewness"] = report["distribution"][col].get("skew")
                            detail["Kurtosis"] = report["distribution"][col].get("kurtosis")
                        col_details.append(detail)
                        
                    if col_details:
                        st.dataframe(pd.DataFrame(col_details))
                        
                    if report.get("correlation"):
                        st.write("Correlation Matrix")
                        st.dataframe(pd.DataFrame(report["correlation"]))
                    
                    st.write("Duplicates")
                    d1, d2 = st.columns(2)
                    d1.metric("Count", report.get("duplicates", {}).get("count", 0))
                    d2.metric("Percentage", f"{report.get('duplicates', {}).get('percentage', 0)}%")

                    st.subheader("Export Report")
                    st.download_button(
                        label="Download JSON Report",
                        data=json.dumps(data["report"], indent=2),
                        file_name="report.json",
                        mime="application/json"
                    )
                else:
                    st.error("Server returned an error")
                    st.json(response.json())

            except Exception as e:
                st.error("Could not connect to the API")
                st.exception(e)

st.markdown("---")
st.caption("CSV Profiler API • FastAPI + Streamlit")
