from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from pydantic import BaseModel
from chain import qa_to_cot
from init_db import init_db
import uvicorn
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
SERVER_API_KEY = os.getenv('SERVER_API_KEY')

app = FastAPI()

class QA(BaseModel):
    question: str
    answer: str
    model_id: Optional[int] = None
    prompt_id: Optional[int] = None

# API 검증 함수
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != SERVER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# 질문과 답변을 주면 COT를 반환
@app.post("/qa2cot")
def qa2cot(data:QA, x_api_key: str = Header(...)):
    # api 검증
    verify_api_key(x_api_key)

    model_id = data.model_id or 1
    prompt_id = data.prompt_id or 1
    try:
        result = qa_to_cot(data.question, data.answer, model_id, prompt_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"ERROR: {e}")

# llm model 목록 불러오기
@app.get("/llm_models")
def get_llm_models( x_api_key: str = Header(...)):
    # api 검증
    verify_api_key(x_api_key)
    try:
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM llm_model_list")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"ERROR: {e}")

# COT 프롬프트 목록 불러오기
@app.get("/prompts")
def get_prompts(x_api_key: str = Header(...)):
    # api 검증
    verify_api_key(x_api_key)
    try:
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM prompt_list")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"ERROR: {e}")
    
# COT 목록 불러오기
@app.get("/cot")
def get_cot_list(x_api_key: str = Header(...)):
    # api 검증
    verify_api_key(x_api_key)
    try:
        with sqlite3.connect('db.sqlite3') as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM cot_list")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"ERROR: {e}")

if __name__=='__main__':
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)