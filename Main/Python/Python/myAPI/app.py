# FastAPI ETL Data Ingestion API

# Overview:
# This script defines a FastAPI application that acts as a lightweight ETL
# ingestion service. It provides endpoints for receiving ETL payloads,
# storing raw records in a Supabase database, and maintaining ingestion
# metadata logs for monitoring and auditing purposes.

# Usage:
# - POST /etl-data:
#   Accepts ETL payloads containing target system metadata (host, database,
#   and table), source identifiers, timestamps, and a list of data records.
#   Each request generates a unique batch ID and inserts the raw records
#   into the "etl_raw_records" table. The API also logs ingestion metadata
#   such as the number of records inserted, HTTP response status, and
#   processing latency into the "etl_ingestion_logs" table.

# - GET /etl-data:
#   Retrieves previously ingested records from the raw data table based on
#   host, database, table name, and a specified date range. The query allows
#   limiting the number of returned records to prevent large responses.

# - Authentication:
#   All endpoints require HTTP Basic Authentication. Credentials are validated
#   using secure string comparison before allowing access to the API.

# Features:
# - Pydantic models for strict request validation and schema definition
#   (DataTarget, POST_ETLData, GET_ETLData, ETLIngestionLog).
# - Automatic generation of batch identifiers to track ingestion events.
# - Automatic timestamp assignment for createdDate and lastModifiedDate.
# - Custom validation to enforce valid date ranges for GET queries.
# - Integration with Supabase REST API for persistent storage of raw ETL data
#   and ingestion logs.
# - Latency tracking to measure API processing time for ingestion requests.
# - Logging of HTTP response codes for observability and debugging.
# - Error handling using HTTPException to surface database and request failures.
# - Environment variable support for secure configuration of Supabase
#   connection credentials.


from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import time
import secrets
import requests
import os
from dotenv import load_dotenv

# =====
# LOAD ENVIRONMENT VARIABLES
# =====

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# =====
# HARD CODED TABLES
# =====

RAW_DATA_TABLE = "etl_raw_records"
LOG_TABLE = "etl_ingestion_logs"

# =====
# BASIC AUTH
# =====

BASIC_AUTH_USERNAME = "admin"
BASIC_AUTH_PASSWORD = "password123"

security = HTTPBasic()

# =====
# MODELS
# =====

class DataTarget(BaseModel):
    host: str
    database: str
    table: str


class POST_ETLData(BaseModel):
    target: DataTarget
    createdDate: datetime = Field(default_factory=datetime.utcnow)
    lastModifiedDate: datetime = Field(default_factory=datetime.utcnow)
    source: str
    timestamp: datetime | None = None
    etldata: list[Dict[str, Any]]


class GET_ETLData(BaseModel):

    host: str
    database: str
    table: str
    startDate: datetime
    endDate: datetime
    limit: int = 100

    @model_validator(mode="after")
    def validate_dates(self):

        if self.startDate > self.endDate:
            raise ValueError("startDate cannot be greater than endDate")

        if (self.endDate - self.startDate).days > 365:
            raise ValueError("Date range cannot exceed 365 days")

        return self
    
class ETLIngestionLog(BaseModel):
    batch_id: str
    #pipeline_name: str
    host: str
    database: str
    table_name: str
    source: str
    records_inserted: int
    createddate: datetime
    lastmodifieddate: datetime
    timestamp: datetime
    #raw_insert_status: int
    latency_ms: Optional[int] = None
    #api_status: int
    http_code: str


# =====
# AUTH VALIDATION
# =====

def validate_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):

    username_correct = secrets.compare_digest(
        credentials.username, BASIC_AUTH_USERNAME
    )

    password_correct = secrets.compare_digest(
        credentials.password, BASIC_AUTH_PASSWORD
    )

    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


# =====
# PROCESSORS
# =====

def process_post_etldata(data: POST_ETLData):


    try:

        latency_ms: Optional[int] = None
        batch_id = str(uuid.uuid4())
        #pipeline_name = "etl_data_ingestion_api"
        start_time = time.time()

        raw_table_url = f"{SUPABASE_URL}/rest/v1/{RAW_DATA_TABLE}"
        log_table_url = f"{SUPABASE_URL}/rest/v1/{LOG_TABLE}"

        # ==========================
        # INSERT RAW DATA
        # ==========================

        raw_records = []

        for row in data.etldata:
            raw_records.append({
                "batch_id": batch_id,
                #"pipeline_name": pipeline_name,
                "table_name": data.target.table,
                "source": data.source,
                "data": row
            })
        
        #print("RAW INSERT PAYLOAD:", raw_records)

        raw_response = requests.post(
            raw_table_url,
            json=raw_records,
            headers=SUPABASE_HEADERS
        )

        http_code = f"{raw_response.status_code} {raw_response.reason}"


        if raw_response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500,
                detail=f"Supabase insert failed: {raw_response.text}"
            )
            
        # ==========================
        # INSERT INGESTION LOG
        # ==========================
        
        latency_ms = int((time.time() - start_time) * 1000)

        log_record = ETLIngestionLog(
            batch_id=batch_id,
            #pipeline_name=pipeline_name,
            host=data.target.host,
            database=data.target.database,
            table_name=data.target.table,
            source=data.source,
            records_inserted=len(raw_records),
            createddate=data.createdDate,
            lastmodifieddate=data.lastModifiedDate,
            timestamp=data.timestamp or datetime.utcnow(),
            #raw_insert_status=raw_response.status_code,
            #api_status=raw_response.status_code,
            http_code= http_code,
            latency_ms=latency_ms
        )

        #print("LOG INSERT PAYLOAD:", log_record.model_dump(mode="json"))


        log_response = requests.post(
            log_table_url,
            json=log_record.model_dump(mode="json"),
            headers=SUPABASE_HEADERS
        )
        
        if log_response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=500,
                detail=f"Log insert failed: {log_response.text}"
            )

        return {
            "recordsInserted": len(raw_records),
            "rawTable": RAW_DATA_TABLE,
            "logTable": LOG_TABLE
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


def process_get_etldata(data: GET_ETLData):

    try:

        url = (
            f"{SUPABASE_URL}/rest/v1/{RAW_DATA_TABLE}"
            f"?ingested_at=gte.{data.startDate.isoformat()}"
            f"&ingested_at=lte.{data.endDate.isoformat()}"
            f"&limit={data.limit}"
        )

        response = requests.get(
            url,
            headers=SUPABASE_HEADERS
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Supabase query failed: {response.text}"
            )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


# =====
# FASTAPI APP
# =====

app = FastAPI(
    title="ETL Data Ingestion API",
    description="API for ingesting ETL data and storing metadata logs.",
    version="1.0.0"
)

# =====
# ENDPOINTS
# =====

@app.post("/etl-data")
def post_etldata(
    data: POST_ETLData,
    auth=Depends(validate_basic_auth)
):

    result = process_post_etldata(data)

    return {
        "status": "inserted",
        "data": result
    }


@app.get("/etl-data")
def get_etldata(
    auth=Depends(validate_basic_auth),
    host: str = Query(...),
    database: str = Query(...),
    table: str = Query(...),
    startDate: datetime = Query(...),
    endDate: datetime = Query(...),
    limit: int = Query(100)
):

    query = GET_ETLData(
        host=host,
        database=database,
        table=table,
        startDate=startDate,
        endDate=endDate,
        limit=limit
    )

    result = process_get_etldata(query)

    return {"records": result}
