# src/quality/validation.py
import re

import pandas as pd
from great_expectations.core.expectation_suite import ExpectationSuite

def build_patient_expectation_suite() -> ExpectationSuite:
    """
    Tạo expectation suite cho anonymized patient data.
    """
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    return ExpectationSuite(
        name="patient_data_suite",
        expectations=[
            {
                "type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "patient_id"},
            },
            {
                "type": "expect_column_value_lengths_to_equal",
                "kwargs": {"column": "cccd", "value": 12},
            },
            {
                "type": "expect_column_values_to_be_between",
                "kwargs": {
                    "column": "ket_qua_xet_nghiem",
                    "min_value": 0,
                    "max_value": 50,
                },
            },
            {
                "type": "expect_column_values_to_be_in_set",
                "kwargs": {"column": "benh", "value_set": valid_conditions},
            },
            {
                "type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": "email",
                    "regex": r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
                },
            },
            {
                "type": "expect_column_values_to_be_unique",
                "kwargs": {"column": "patient_id"},
            },
        ],
    )


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath, dtype={"cccd": str, "so_dien_thoai": str})
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    def fail(check_name: str):
        results["success"] = False
        results["failed_checks"].append(check_name)

    # Check 1: CCCD sau anonymization vẫn phải đúng định dạng 12 chữ số
    if "cccd" not in df or not df["cccd"].astype(str).str.fullmatch(r"\d{12}").all():
        fail("cccd_format")

    # Check 2: Không có null values trong các cột quan trọng
    required_columns = ["patient_id", "cccd", "so_dien_thoai", "benh", "ket_qua_xet_nghiem"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        fail(f"missing_columns:{','.join(missing_columns)}")
    elif df[required_columns].isnull().any().any():
        fail("null_required_values")

    # Check 3: Số rows phải bằng original
    try:
        original_rows = len(pd.read_csv("data/raw/patients_raw.csv"))
        results["stats"]["original_rows"] = original_rows
        if len(df) != original_rows:
            fail("row_count_mismatch")
    except FileNotFoundError:
        results["stats"]["original_rows"] = None

    if "email" in df and not df["email"].astype(str).map(
        lambda value: bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", value))
    ).all():
        fail("email_format")

    return results
