import pandas as pd
import numpy as np
import io
import chardet

def read_csv_safely(file_bytes: bytes):

    detected = chardet.detect(file_bytes)
    encoding = detected.get("encoding") or "utf-8"

    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin1")
            encoding = "latin1"
        except Exception:
            text = file_bytes.decode(encoding, errors="replace")
            df = pd.read_csv(io.StringIO(text))
    except Exception:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin1")
        encoding = "latin1"

    return df, encoding



def make_json_safe(data):
    if isinstance(data, (np.int64, np.int32)):
        return int(data)
    elif isinstance(data, (np.float64, np.float32, float)):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    elif isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_safe(v) for v in data]
    elif isinstance(data, (np.bool_)):
        return bool(data)
    elif pd.isna(data):
        return None
    else:
        return data


def analyze_csv(df: pd.DataFrame):

    columns = list(df.columns)
    dtypes = {col: str(df[col].dtype) for col in columns}
    missing_values = {col: int(val) for col, val in df.isnull().sum().to_dict().items()}

    numeric_cols = df.select_dtypes(include='number').columns
    categorical_cols = df.select_dtypes(exclude='number').columns
    bool_cols = df.select_dtypes(include='bool').columns

    summary = {}
    for col in numeric_cols:
        summary[col] = {
            "mean": float(round(df[col].mean(), 2)),
            "median": float(round(df[col].median(), 2)),
            "min": float(round(df[col].min(), 2)),
            "max": float(round(df[col].max(), 2)),
            "std_dev": float(round(df[col].std(), 2))
        }

    outliers = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            outliers[col] = 0
            continue
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        count = ((df[col] < lower) | (df[col] > upper)).sum()
        outliers[col] = int(count)

    distribution = {}
    for col in numeric_cols:
        distribution[col] = {
            "skew": float(round(df[col].skew(), 2)),
            "kurtosis": float(round(df[col].kurtosis(), 2))
        }

    duplicates_count = int(df.duplicated().sum())
    duplicates_percentage = float(round((duplicates_count / len(df)) * 100, 2)) if len(df) else 0

    memory_usage_mb = float(round(df.memory_usage(deep=True).sum() / (1024 ** 2), 5))

    column_summary = {
        "numeric": len(numeric_cols),
        "categorical": len(categorical_cols),
        "boolean": len(bool_cols)
    }

    constant_columns = [col for col in df.columns if df[col].nunique() == 1]
    empty_columns = [col for col in df.columns if df[col].dropna().empty]

    data_quality_issues = []
    for col in numeric_cols:
        if df[col].isnull().any():
            data_quality_issues.append(f"Column '{col}' contains NaN values")

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR != 0:
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            extremes = df[col][(df[col] < lower) | (df[col] > upper)]
            if not extremes.empty:
                data_quality_issues.append(
                    f"Column '{col}' has extreme outlier ({extremes.iloc[0]})"
                )

    corr_matrix = df.corr(numeric_only=True).to_dict()
    corr_matrix = {
        k: {ik: float(iv) for ik, iv in v.items()}
        for k, v in corr_matrix.items()
    }

    dataset_info = {
        "rows": int(len(df)),
        "columns": int(len(columns)),
        "missing_percent": float(round((df.isnull().sum().sum() / (len(df) * len(columns))) * 100, 2))
    }

    report = {
        "dataset_info": dataset_info,
        "columns": columns,
        "dtypes": dtypes,
        "missing_values": missing_values,
        "summary": summary,
        "outliers": outliers,
        "distribution": distribution,
        "duplicates": {"count": duplicates_count, "percentage": duplicates_percentage},
        "memory_usage_mb": memory_usage_mb,
        "column_summary": column_summary,
        "constant_columns": constant_columns,
        "empty_columns": empty_columns,
        "data_quality_issues": data_quality_issues,
        "correlation": corr_matrix
    }
    report = make_json_safe(report)
    return make_json_safe(report)
