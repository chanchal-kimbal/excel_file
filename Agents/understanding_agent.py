import pandas as pd
import re
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent 
from ollama_setup import *
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from ollama_setup import ensure_ollama_running

ensure_ollama_running()


@tool
def align_excel_headers_tool(excel):
    """
    Align Excel headers to required standard headers.
    """
    df=pd.read_excel(excel)

    Actual_need = [
        '_Test ID', '_desc', '_Test Data',
        '_Expected Result', '_Status code',
        'API Type', 'URL'
    ]

    def normalize(col: str) -> str:
        return re.sub(r'[^a-z0-9]', '', col.lower())

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


system_prompt = """
You are an Excel Header Alignment Agent.

Your responsibilities:
- You MUST use the provided tool to normalize and align Excel column headers.
- You MUST NOT modify, rewrite, or optimize the tool logic.
- You MUST NOT infer, hallucinate, or generate missing columns.
- If a required column is NOT present in the Excel file, you MUST allow the tool to raise an error.
- You MUST NOT attempt recovery, fallback logic, or silent correction.
- You MUST always call the tool when a DataFrame is provided.
- You MUST return ONLY the updated DataFrame or the raised error.
- You MUST NOT add explanations, comments, or additional output.
"""

def build_understanding_agent():
    llm = ChatOllama(model="llama3.1:8B",temperature=0.2)
    tools = [align_excel_headers_tool]
    understanding_agent = create_react_agent(model=llm,tools=tools,name="understanding_agent",prompt=system_prompt)
    return understanding_agent



def understanding_agent(state):
    excel_file = state.get("excel_file")
    if not excel_file:
        raise ValueError("excel_file missing")

    aligned_df = align_excel_headers_tool.invoke(excel_file)

    agent = build_understanding_agent()
    response = agent.invoke({
        "messages": [
            HumanMessage(
                content=f"Validate and explain the Excel header alignment for {excel_file}"
            )
        ]
    })

    explanation = response["messages"][-1].content

    # state["excel_validated"] = True
    # state["understanding_note"] = explanation

    state["aligned_df"] = aligned_df

    return state



