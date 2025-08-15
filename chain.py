from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.environ['GROQ_API_KEY']
LLM_MODEL = os.environ['LLM_MODEL']

llm = ChatGroq(
    model = LLM_MODEL,
    max_tokens=1024,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    )

def qa_to_cot(question, answer):

    # 1. 프롬프트 정의
    cot_prompt_text = '''
당신은 Chain of Thought 라벨링 전문가입니다.
주어진 질문과 답변을 보고 답변에 필요한 Chain of Thought을 **JSON 구조**로 단계별로 작성해주세요.

질문: {question}
답변: {answer}

출력 형식:
{{
  "steps": [
    {{"step": 1, "description": "..."}},
    {{"step": 2, "description": "..."}},
    ...
  ],
  "summary": "..."
}}
    '''
    
    # 2. 템플릿 생성
    cot_template = PromptTemplate.from_template(cot_prompt_text)
    
    # 3. 프롬프트 채우기
    cot_prompt = cot_template.format(question = question, answer = answer)
    
    # 4. LLM 호출
    response = llm.invoke(cot_prompt)

    cot_json = response.content if hasattr(response, "content") else response
    return {"q":question, "a":answer, "cot" : cot_json}

if __name__=="__main__":
    print(qa_to_cot("고혈압 환자가 아침 운동을 해도 안전한가요?","대부분의 고혈압 환자는 가벼운 아침 운동이 안전하지만, 혈압이 불안정하거나 합병증이 있는 경우는 주치의와 상의해야 합니다."))

# 예시 2

# 질문: "당뇨병 환자가 단 음식을 먹으면 혈당에 어떤 영향을 주나요?"

# 답변: "단 음식은 혈당을 급격히 상승시키므로, 당뇨병 환자는 적은 양만 섭취하고, 식사 후 혈당을 모니터링하는 것이 중요합니다."

# 예시 3

# 질문: "편두통 예방을 위해 일상생활에서 어떤 습관을 가져야 하나요?"

# 답변: "규칙적인 수면, 스트레스 관리, 카페인 과다 섭취 피하기, 충분한 수분 섭취가 편두통 예방에 도움이 됩니다."