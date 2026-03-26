import streamlit as st
import requests
import pandas as pd
import json

API_URL = "https://profilr-backend-production.up.railway.app"

st.set_page_config(page_title="CSV Profiler", page_icon="📊", layout="centered")
st.title("CSV Profiler")
st.write("Upload a CSV file and get instant profiling insights.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    st.success(f"Selected file: **{uploaded_file.name}**")

    if st.button("Analyze CSV 🚀"):
        with st.spinner("Uploading and analyzing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{API_URL}/upload-csv/", files=files)

                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis complete!")
                    st.subheader("📁 File")
                    st.write(data["filename"])
                    st.subheader("📈 Report")
                    st.json(data["report"])
                    st.subheader("📥 Export Report")
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