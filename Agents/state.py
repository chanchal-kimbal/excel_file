
from typing import TypedDict, List, Optional
import pandas as pd

class GraphState(TypedDict, total=False):
    # inputs
    excel_file: str
    projectid: str
    client_id: str
    username: str
    password: str

    # understanding agent
    excel_validated: bool
    aligned_df: pd.DataFrame
    understanding_note: str

    # data_fetching agent
    meter_ids: Optional[List[str]]
    communication_dates: Optional[List[str]]

    # planning agent
    # planned_tests: List[dict]
    execution_result: str 

    # execution agent
    final_results_df: pd.DataFrame

    # 🔴 ADD FOR REPORT AGENT
    report_metrics: dict

