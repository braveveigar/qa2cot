from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import sqlite3
import json

load_dotenv()

GROQ_API_KEY = os.environ['GROQ_API_KEY']

def qa_to_cot(question, answer, model_id, prompt_id):
    '''
    이 함수는 질문과 답변을 주었을 때 LLM 모델이 판단한 Chain of Thought을 반환하는 코드입니다.

    Input : Question(str), Answer(str)
    Output : {q:Question, a: Answer, cot: Chain of Thought} (Dict)
    '''

    # 1. 모델 및 프롬프트를 DB에서 가져오기
    with sqlite3.connect("db.sqlite3") as conn:
        cursor = conn.cursor()
        LLM_MODEL = cursor.execute('SELECT model FROM llm_model_list WHERE id = ?', (model_id,)).fetchone()[0]
        cot_prompt_text = cursor.execute('SELECT prompt FROM prompt_list WHERE id = ?', (prompt_id,)).fetchone()[0]

        # 2. 모델 설정
        llm = ChatGroq(
            model = LLM_MODEL,
            max_tokens=1024,
            reasoning_format="parsed",
            timeout=None,
            max_retries=2,
            )

        # 3. 템플릿 생성
        cot_template = PromptTemplate.from_template(cot_prompt_text)
        
        # 4. 프롬프트 채우기
        cot_prompt = cot_template.format(question = question, answer = answer)
        
        # 5. LLM 호출
        response = llm.invoke(cot_prompt)

        # JSON 문자열 → dict, 실패하면 빈 dict나 문자열 저장
        try:
            cot_json = json.loads(response.content) if hasattr(response, "content") else json.loads(response)
        except json.JSONDecodeError:
            cot_json = {"steps": [], "summary": str(response)}

        # DB 저장용 JSON 문자열
        cot_str = json.dumps(cot_json, ensure_ascii=False)

        cursor.execute("""
            INSERT INTO cot_list (question, answer, cot, model_id, prompt_id)
            VALUES (?,?,?,?,?)""",(question, answer, cot_str, model_id, prompt_id))

    return {"question":question, "answer":answer, "cot" : cot_json}

if __name__=="__main__":
    print(qa_to_cot("고혈압 환자가 아침 운동을 해도 안전한가요?","대부분의 고혈압 환자는 가벼운 아침 운동이 안전하지만, 혈압이 불안정하거나 합병증이 있는 경우는 주치의와 상의해야 합니다.",1,1))