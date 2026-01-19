import pandas as pd
import re

def normalize(col: str) -> str:
    
    return re.sub(r'[^a-z0-9]', '', col.lower())


def align_excel_headers(df):

    # df = pd.read_excel(excel_file)

    Actual_need = [
    '_Test ID', '_desc', '_Test Data',
    '_Expected Result', '_Status code', 'API Type', 'URL'] 

    excel_cols_normalized = {
        normalize(col): col for col in df.columns
    }

    rename_map = {}

    for required_col in Actual_need:
        norm_required = normalize(required_col)

        if norm_required in excel_cols_normalized:
            actual_excel_col = excel_cols_normalized[norm_required]
            rename_map[actual_excel_col] = required_col
        else:
            raise KeyError(
                f"Required column '{required_col}' not found in Excel file"
            )

    df = df.rename(columns=rename_map)

    return df




# file="demo_output_copy.xlsx"
# file=pd.read_excel(file)
# df = align_excel_headers(file)

# print(df.columns.tolist())










