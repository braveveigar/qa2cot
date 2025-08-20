from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import sqlite3
import json
import re

load_dotenv()

GROQ_API_KEY = os.environ['GROQ_API_KEY']

def validate_cot(cot_json):
    """
    cot_json 포맷을 검증하는 함수.

    검증 항목:
    1. cot_json이 dict인지 확인
    2. 'steps'와 'summary' 키 존재 확인
    3. 'steps'가 리스트인지 확인
    4. 각 step이 'step'과 'description' 키를 가지고 있는지 확인
    5. step 번호가 순서대로(1, 2, 3...) 정렬되어 있는지 확인

    Returns:
        is_valid (bool) : 검증 성공 여부
        cot_json (dict) : 원본 또는 보정된 JSON
        error_reason (str or None) : 실패 시 원인 설명, 성공 시 None
    """
    if not isinstance(cot_json, dict):
        return False, cot_json, "Not a dictionary"

    if 'steps' not in cot_json or 'summary' not in cot_json:
        return False, cot_json, "Missing 'steps' or 'summary' keys"

    if not isinstance(cot_json['steps'], list):
        return False, cot_json, "'steps' is not a list"

    for i, step in enumerate(cot_json['steps']):
        if 'step' not in step or 'description' not in step:
            return False, cot_json, f"Missing 'step' or 'description' in step {i+1}"
        if step['step'] != i + 1:
            return False, cot_json, f"'step' number incorrect at step {i+1}"

    return True, cot_json, None

def qa_to_cot(question, answer, model_id, prompt_id):
    '''
    이 함수는 질문과 답변을 주었을 때 LLM 모델이 판단한 Chain of Thought을 반환하는 코드입니다.

    Input : Question(str), Answer(str)
    Output : {q:Question, a: Answer, cot: Chain of Thought} (Dict)
    '''

    # 모델 및 프롬프트를 DB에서 가져오기
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        LLM_MODEL = cursor.execute('SELECT model FROM llm_model_list WHERE id = ?', (model_id,)).fetchone()[0]
        cot_prompt_text = cursor.execute('SELECT prompt FROM prompt_list WHERE id = ?', (prompt_id,)).fetchone()[0]

        if model_id == 1:
            # 모델 설정
            llm = ChatGroq(
                model = LLM_MODEL,
                max_tokens=1024,
                reasoning_format="parsed",
                timeout=None,
                max_retries=2,
                )
            
        elif model_id == 2:
            llm = ChatOpenAI(
                openai_api_base="https://wtvkajelw6gs6j-8000.proxy.runpod.net/v1",
                model="meta-llama/Llama-2-13b-chat-hf",
                openai_api_key="dummy",
                max_tokens=1024,
                timeout=None,
                max_retries=2 
                )

        # 템플릿 생성
        cot_template = PromptTemplate.from_template(cot_prompt_text)
        
        # 프롬프트 채우기
        cot_prompt = cot_template.format(question = question, answer = answer)
        
        # LLM 호출
        response = llm.invoke(cot_prompt)

        # 호출 값 처리 및 검증
        raw_text = response.content if hasattr(response, "content") else response
        raw_text = re.sub(r",\s*}", "}", raw_text)
        raw_text = re.sub(r",\s*]", "]", raw_text)
        try:
            cot_json = json.loads(raw_text)
        except json.JSONDecodeError:
            cot_json = {"steps": [], "error": "JSON parsing error", "content":response.content}

        is_valid, cot_json, failure_detail = validate_cot(cot_json) #json 포맷 검증
        if is_valid: # 검증 성공 시
            # DB 저장용 JSON 문자열
            cot_str = json.dumps(cot_json, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO cot_list (question, answer, cot, model_id, prompt_id)
                VALUES (?,?,?,?,?)""",(question, answer, cot_str, model_id, prompt_id))
        else:
            return {"question":question, "answer":answer, "validation_failure":cot_json, "failure_detail":failure_detail}

    return {"question":question, "answer":answer, "cot" : cot_json}

if __name__=="__main__":
    print(qa_to_cot("고혈압 환자가 아침 운동을 해도 안전한가요?","대부분의 고혈압 환자는 가벼운 아침 운동이 안전하지만, 혈압이 불안정하거나 합병증이 있는 경우는 주치의와 상의해야 합니다.",1,1))