import pandas as pd
import numpy as np
import os
import io
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LAST_FILE = {"path": None}


@app.route("/")
def home():
    return render_template("index.html")


def get_column_breakdown(df):
    breakdown = []
    for col in df.columns:
        dtype = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "text"
        missing = int(df[col].isnull().sum())
        breakdown.append({
            "column": col,
            "type": dtype,
            "missing": missing
        })
    return breakdown


def compute_score(rows, cols, missing, duplicates, outliers):
    total_cells = rows * cols if rows * cols > 0 else 1
    penalty = (missing + duplicates + outliers) / total_cells
    return round(max(0, 100 - penalty * 100), 2)


def analyze(df):
    rows = df.shape[0]
    cols = df.shape[1]
    missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())

    outliers = 0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers += int(((df[col] < lower) | (df[col] > upper)).sum())

    score = compute_score(rows, cols, missing, duplicates, outliers)

    recommendations = []
    if missing > 0:
        recommendations.append(
            f"Found {missing} missing values - consider filling them with mean/median (numeric) or mode (categorical)."
        )
    if duplicates > 0:
        recommendations.append(
            f"Found {duplicates} duplicate rows - consider removing them."
        )
    if outliers > 0:
        recommendations.append(
            f"Found {outliers} outliers - consider reviewing or capping extreme values."
        )

    return {
        "score": score,
        "rows": rows,
        "columns": cols,
        "missing_values": missing,
        "duplicate_rows": duplicates,
        "outliers": outliers,
        "recommendations": recommendations,
        "column_breakdown": get_column_breakdown(df)
    }


def clean_dataframe(df):
    df = df.drop_duplicates()

    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            else:
                mode_vals = df[col].mode()
                if len(mode_vals) > 0:
                    df[col] = df[col].fillna(mode_vals[0])
                else:
                    df[col] = df[col].fillna("Unknown")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df[col] = df[col].clip(lower=lower, upper=upper)

    return df


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file selected. Please choose a CSV file."}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Invalid file type. Please upload a .csv file."}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        df = pd.read_csv(filepath)
    except pd.errors.EmptyDataError:
        return jsonify({"error": "The uploaded file is empty."}), 400
    except Exception as e:
        return jsonify({"error": f"Could not read the file. Make sure it's a valid CSV. ({str(e)})"}), 400

    if df.shape[0] == 0:
        return jsonify({"error": "The CSV has no data rows."}), 400

    LAST_FILE["path"] = filepath

    try:
        report = analyze(df)

        # also compute "after cleaning" score preview
        cleaned_df = clean_dataframe(df.copy())
        after_rows = cleaned_df.shape[0]
        after_cols = cleaned_df.shape[1]
        after_missing = int(cleaned_df.isnull().sum().sum())
        after_duplicates = int(cleaned_df.duplicated().sum())
        after_score = compute_score(after_rows, after_cols, after_missing, after_duplicates, 0)
        report["after_score"] = after_score

    except Exception as e:
        return jsonify({"error": f"Error analyzing file: {str(e)}"}), 400

    return jsonify(report)


@app.route("/clean", methods=["POST"])
def clean():
    filepath = LAST_FILE["path"]
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "No uploaded file found. Please upload a CSV first."}), 400

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return jsonify({"error": f"Could not read the file: {str(e)}"}), 400

    df = clean_dataframe(df)

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="cleaned_data.csv"
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)