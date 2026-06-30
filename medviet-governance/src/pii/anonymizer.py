# src/pii/anonymizer.py
import pandas as pd
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")

class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        """
        Anonymize text với strategy được chọn.

        Strategies:
        - "mask"    : Nguyen Van A → N****** V** A
        - "replace" : thay bằng fake data (dùng Faker)
        - "hash"    : SHA-256 one-way hash
        - "generalize": chỉ dùng cho tuổi/năm sinh
        """
        text = str(text)
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        operators = {}

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", 
                          {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", 
                                 {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", 
                           {"new_value": fake.numerify(text="############")}),
                "VN_PHONE": OperatorConfig("replace", 
                            {"new_value": "0" + fake.random_element(["3", "5", "7", "8", "9"]) + fake.numerify(text="########")}),
            }
        elif strategy == "mask":
            operators = {
                "DEFAULT": OperatorConfig(
                    "mask",
                    {"masking_char": "*", "chars_to_mask": 100, "from_end": False},
                )
            }
        elif strategy == "hash":
            operators = {
                "DEFAULT": OperatorConfig("hash", {"hash_type": "sha256"})
            }
        else:
            raise ValueError(f"Unsupported anonymization strategy: {strategy}")

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Anonymize toàn bộ DataFrame.
        - Cột text (ho_ten, dia_chi, email): dùng anonymize_text()
        - Cột cccd, so_dien_thoai: replace trực tiếp bằng fake data
        - Cột benh, ket_qua_xet_nghiem: GIỮ NGUYÊN (cần cho model training)
        - Cột patient_id: GIỮ NGUYÊN (pseudonym đã đủ an toàn)
        """
        df_anon = df.copy()

        if "ho_ten" in df_anon:
            df_anon["ho_ten"] = df_anon["ho_ten"].apply(self.anonymize_text)
        if "email" in df_anon:
            df_anon["email"] = df_anon["email"].apply(self.anonymize_text)
        if "dia_chi" in df_anon:
            df_anon["dia_chi"] = df_anon["dia_chi"].apply(self.anonymize_text)
        if "bac_si_phu_trach" in df_anon:
            df_anon["bac_si_phu_trach"] = df_anon["bac_si_phu_trach"].apply(
                self.anonymize_text
            )
        if "cccd" in df_anon:
            df_anon["cccd"] = [fake.numerify(text="############") for _ in df_anon.index]
        if "so_dien_thoai" in df_anon:
            df_anon["so_dien_thoai"] = [
                "0" + fake.random_element(["3", "5", "7", "8", "9"]) + fake.numerify(text="########")
                for _ in df_anon.index
            ]

        return df_anon

    def calculate_detection_rate(self, 
                                  original_df: pd.DataFrame,
                                  pii_columns: list) -> float:
        """
        Tính % PII được detect thành công.
        Mục tiêu: > 95%

        Logic: với mỗi ô trong pii_columns,
               kiểm tra xem detect_pii() có tìm thấy ít nhất 1 entity không.
        """
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].astype(str):
                total += 1
                results = detect_pii(value, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0
