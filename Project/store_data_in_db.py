
######## for postgresql database ##########


# import os
# import json
# import pandas as pd
# from datetime import datetime
# from sqlalchemy import create_engine, text

# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL is not set")

# engine = create_engine(DATABASE_URL, pool_pre_ping=True)



# def safe_json(value):
#     if value is None:
#         return None
#     if isinstance(value, (dict, list)):
#         return json.dumps(value)
#     return str(value)


# def create_results_table():
#     with engine.begin() as conn:
#         conn.execute(text("""
#             CREATE TABLE IF NOT EXISTS test_results (
#                 id SERIAL PRIMARY KEY,
#                 client_id TEXT,
#                 project_id INTEGER,
#                 test_id TEXT,
#                 description TEXT,
#                 request_body JSONB,
#                 response JSONB,
#                 expected_results JSONB,
#                 status_code INTEGER,
#                 result TEXT,
#                 assertion_result TEXT,
#                 taking_time_seconds REAL,
#                 requestid_response JSONB,
#                 requestid_assertions JSONB,
#                 e2e_results TEXT,
#                 uploaded_at TIMESTAMP,
#                 UNIQUE (client_id, project_id, test_id)
#             )
#         """))




# def save_results_to_db(df, client_id, project_id):
#     if df.empty:
#         return

#     create_results_table()
#     uploaded_at = datetime.now()

#     insert_sql = text("""
#         INSERT INTO test_results (
#             client_id,
#             project_id,
#             test_id,
#             description,
#             request_body,
#             response,
#             expected_results,
#             status_code,
#             result,
#             assertion_result,
#             taking_time_seconds,
#             requestid_response,
#             requestid_assertions,
#             e2e_results,
#             uploaded_at
#         )
#         VALUES (
#             :client_id, :project_id, :test_id, :description,
#             :request_body, :response, :expected_results, :status_code,
#             :result, :assertion_result, :taking_time_seconds,
#             :requestid_response, :requestid_assertions, :e2e_results,
#             :uploaded_at
#         )
#         ON CONFLICT (client_id, project_id, test_id)
#         DO UPDATE SET
#             uploaded_at = EXCLUDED.uploaded_at,
#             result = EXCLUDED.result,
#             assertion_result = EXCLUDED.assertion_result,
#             response = EXCLUDED.response
#     """)

#     with engine.begin() as conn:
#         for _, row in df.iterrows():
#             conn.execute(insert_sql, {
#                 "client_id": client_id,
#                 "project_id": project_id,
#                 "test_id": row["test_id"],
#                 "description": row["description"],
#                 "request_body": safe_json(row["request_body"]),
#                 "response": safe_json(row["response"]),
#                 "expected_results": safe_json(row["expected_results"]),
#                 "status_code": row.get("status_code"),
#                 "result": row["result"],
#                 "assertion_result": row["assertion_result"],
#                 "taking_time_seconds": row["Taking_time(seconds)"],
#                 "requestid_response": safe_json(row["requestID_response"]),
#                 "requestid_assertions": safe_json(row["requestID_assertions"]),
#                 "e2e_results": row["E2E_results"],
#                 "uploaded_at": uploaded_at
#             })



# def create_upload_metadata_table():
#     with engine.begin() as conn:
#         conn.execute(text("""
#             CREATE TABLE IF NOT EXISTS upload_metadata (
#                 id SERIAL PRIMARY KEY,
#                 client_id TEXT,
#                 project_id INTEGER,
#                 username TEXT,
#                 uploaded_file_name TEXT,
#                 uploaded_at TIMESTAMP,
#                 UNIQUE (client_id, project_id, username, uploaded_file_name)
#             )
#         """))




# def save_upload_metadata(
#     client_id,
#     project_id,
#     username,
#     uploaded_file_name
# ):
#     create_upload_metadata_table()
#     uploaded_at = datetime.now()

#     with engine.begin() as conn:
#         conn.execute(text("""
#             INSERT INTO upload_metadata (
#                 client_id,
#                 project_id,
#                 username,
#                 uploaded_file_name,
#                 uploaded_at
#             )
#             VALUES (:client_id, :project_id, :username, :uploaded_file_name, :uploaded_at)
#             ON CONFLICT (client_id, project_id, username, uploaded_file_name)
#             DO UPDATE SET
#                 uploaded_at = EXCLUDED.uploaded_at
#         """), {
#             "client_id": client_id,
#             "project_id": project_id,
#             "username": username,
#             "uploaded_file_name": uploaded_file_name,
#             "uploaded_at": uploaded_at
#         })


# def fetch_results_from_db(client_id, project_id):
#     query = text("""
#         SELECT *
#         FROM test_results
#         WHERE client_id = :client_id
#           AND project_id = :project_id
#         ORDER BY uploaded_at DESC
#     """)
#     return pd.read_sql(query, engine, params={
#         "client_id": client_id,
#         "project_id": project_id
#     })


# def fetch_upload_metadata():
#     query = "SELECT client_id, project_id, username, uploaded_file_name, uploaded_at FROM upload_metadata"
#     return pd.read_sql(query, engine)



















import sqlite3
import json
import streamlit as st
import pandas as pd
from datetime import datetime

def safe_json(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)



def get_table_name(client_id, project_id):
    return f"results_client_{client_id}_project_{project_id}"


def save_results_to_db(df, client_id, project_id, db_path="test_results.db"):
    if df.empty:
        return

    table_name = get_table_name(client_id, project_id)

    uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            test_id TEXT PRIMARY KEY,
            description TEXT,
            request_body TEXT,
            response TEXT,
            expected_results TEXT,
            status_code INTEGER,
            result TEXT,
            assertion_result TEXT,
            Taking_time_seconds REAL,
            requestID_response TEXT,
            requestID_assertions TEXT,
            "E2E_results" TEXT ,
            "uploaded_at" TEXT 
        )
    """)

    for _, row in df.iterrows():
        cursor.execute(
            f"""
            INSERT OR IGNORE INTO {table_name}
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                safe_json(row["test_id"]),
                safe_json(row["description"]),
                safe_json(row["request_body"]),          # ✅ FIXED
                safe_json(row["response"]),
                safe_json(row["expected_results"]),      # ✅ FIXED
                int(row["status_code"]) if row.get("status_code") is not None else None,
                safe_json(row["result"]),
                safe_json(row["assertion_result"]),
                float(row["Taking_time(seconds)"]),
                safe_json(row["requestID_response"]),
                safe_json(row["requestID_assertions"]),
                safe_json(row["E2E_results"]),
                uploaded_at
            )
        )

    conn.commit()
    conn.close()







####### CREATE METADATA TABLE (AUTO / SAFE)#######


from datetime import datetime
import sqlite3


import sqlite3

def create_upload_metadata_table(db_path="test_results.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS upload_metadata (
            client_id TEXT,
            project_id INTEGER,
            username TEXT,
            uploaded_file_name TEXT,
            uploaded_at TEXT,
            UNIQUE (client_id, project_id, username, uploaded_file_name)
        )
    """)

    conn.commit()
    conn.close()




def save_upload_metadata(
    client_id,
    project_id,
    username,
    uploaded_file_name,
    db_path="test_results.db"
):
    create_upload_metadata_table(db_path)

    uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO upload_metadata (
            client_id,
            project_id,
            username,
            uploaded_file_name,
            uploaded_at
        )
        VALUES (?,?,?,?,?)
        ON CONFLICT(client_id, project_id, username, uploaded_file_name)
        DO UPDATE SET
            uploaded_at = excluded.uploaded_at
    """, (
        client_id,
        project_id,
        username,
        uploaded_file_name,
        uploaded_at
    ))

    conn.commit()
    conn.close()

   

############# show meta data ###############

def fetch_upload_metadata(db_path="test_results.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT client_id, project_id, username, uploaded_file_name, uploaded_at FROM upload_metadata",
        conn
    )
    conn.close()
    return df





# ---------- FETCH RESULTS ----------
def fetch_results_from_db(client_id, project_id, db_path="test_results.db"):
    table_name = f"results_client_{client_id}_project_{project_id}"

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        conn
    )
    conn.close()
    return df


