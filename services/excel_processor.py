import pandas as pd
import io
from config.settings import RESULT_COLUMNS, NUMERIC_FIELDS

class ExcelProcessor:
    @staticmethod
    def read_excel(file_bytes: io.BytesIO) -> pd.DataFrame:
        return pd.read_excel(file_bytes)

    @staticmethod
    def create_result_excel(results: list) -> io.BytesIO:
        result_df = pd.DataFrame(results, columns=RESULT_COLUMNS)

        for field in NUMERIC_FIELDS:
            result_df[field] = pd.to_numeric(result_df[field], errors='coerce').fillna(0).round(2)

        output_bytes = io.BytesIO()
        with pd.ExcelWriter(output_bytes, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, float_format="%.2f")

            worksheet = writer.sheets["Sheet1"]
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in column_cells)
                column_letter = column_cells[0].column_letter
                worksheet.column_dimensions[column_letter].width = max_length + 2

        output_bytes.seek(0)
        return output_bytes
