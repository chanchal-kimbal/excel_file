import os
import pandas as pd
import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent 
from langchain_core.messages import HumanMessage # Ensure HumanMessage is imported here
import time
from Agents.ollama_setup import *

ensure_ollama_running()

VECTOR_DB_PATH = "domain_vectorstores/auth_login"
EXCEL_FILE = "master_file.xlsx"

df = pd.read_excel(EXCEL_FILE)
columns = list(df.columns)

os.makedirs("domain_vectorstores", exist_ok=True)

def load_docs_from_excel(excel_path):
    df = pd.read_excel(excel_path)
    docs = []

    for _, row in df.iterrows():
        text = "\n".join([f"{col}: {row[col]}" for col in df.columns])
        metadata = {col: row[col] for col in df.columns}

        docs.append(
            Document(
                page_content=text,
                metadata=metadata
            )
        )

    return docs



def build_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if not os.path.exists(VECTOR_DB_PATH):
        print(f"📄 Building Vector DB from {EXCEL_FILE}")

        docs = load_docs_from_excel(EXCEL_FILE)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        splits = splitter.split_documents(docs)

        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=VECTOR_DB_PATH,
        )
    else:
        vectordb = Chroma(
            persist_directory=VECTOR_DB_PATH,
            embedding_function=embeddings
        )

    return vectordb


def get_doc_by_test_id(vectordb, test_id):
    """Returns clean JSON-safe records matching exact _Test ID"""
    
    collection = vectordb._collection

    raw = collection.get(where={"_Test ID": str(test_id)})

    ids = raw.get("ids", [])
    if len(ids) == 0:
        return []

    docs = []
    length = len(ids)

    for i in range(length):
        doc = {}
        for key, values in raw.items():
            if isinstance(values, list) and len(values) == length:
                doc[key] = values[i]
        docs.append(doc)

    return docs


@tool
def get_testcase_by_id(test_id: str) -> str:
    """
    Fetch testcase metadata using Test ID.
    Returns JSON string.
    """

    vectordb = build_vectorstore()
    docs = get_doc_by_test_id(vectordb, test_id)

    if len(docs) == 0:
        return json.dumps({"error": "Test ID not found"})

    row = docs[0]
    metadata = row.get("metadatas", {})

    output = {
        "_Test ID": test_id,
        "data": metadata
    }

    return json.dumps(output, indent=4)


system_prompt="""

You are an Excel TestCase Agent.

Your ONLY knowledge source is the vector database built from the Excel sheet.

RULES:
- ALWAYS call the tool `get_testcase_by_id` when the user asks about:
  - Test ID
  - API details
  - Testcase details
  - User story
  - Expected result
  - Actual result
  - Test data
  - Any test-related query
  - You MUST only use the following valid Excel columns:
   {columns}
- NEVER guess or invent information.
- NEVER answer from your own memory.
- NEVER summarize without verifying from the tool.

OUTPUT RULES:
- Final answer must always be in valid JSON.
- If Test ID is not found, respond:
  {
    "error": "Test ID not found"
  }

YOUR BEHAVIOR:
- Determine exactly what Test ID the user is asking for.
- Pass only the Test ID string into the tool.
- After receiving tool output, return the final JSON directly.
- Do not rewrite, modify, or generate new test data.

EXAMPLE INPUTS:
- "Give me data for EHES_LGN_TC_1"
- "What is the expected result of EHES_LGN_TC_10?"
- "Show me the test steps for EHES_ABC_22"

In all above cases, ALWAYS call the tool with the Test ID.

You are accurate, strict, and follow the rules exactly.

"""

def data_extraction():
    llm = ChatOllama(model="llama3.1:8B", temperature=0.0)
    tools = [get_testcase_by_id]
    agent = create_react_agent(
        model=llm,
        tools=tools,
        name="health_agent",
        prompt=system_prompt
    )
    return agent



def stream_text(text: str, delay=0.02):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()




if __name__ == "__main__":
    while True:
        query = input("You: ")
       
        if query.lower() in ["exit", "quit"]:
            break

        agent = data_extraction()

        start = time.time()
        response = agent.invoke({"messages": [HumanMessage(content=query)]})
        elapsed = time.time() - start

        reply = response["messages"][-1].content

        print("\nAgent:")
        print(f"(latency: {elapsed:.2f}s)\n")
        stream_text(reply)
        print()


