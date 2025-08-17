import sqlite3

def init_db():
    # 경량화 DB 설정
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cot_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        cot TEXT,
        model_id int,
        prompt_id int
        )
    """
    )

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS llm_model_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model VARCHAR(100) UNIQUE
        )
    """
    )

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompt_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT UNIQUE
        )
    """
    )

    # 샘플 프롬프트
    sample_prompt = '''
당신은 Chain of Thought 라벨링 전문가입니다.
주어진 질문과 답변을 보고 답변에 필요한 Chain of Thought을 JSON 구조로 단계별로 작성해주세요.

다음 질문에 대해 Chain-of-Thought 단계를 JSON 형식으로 작성해 주세요.
JSON 구조:
{
  "steps": [
    {"step": 1, "description": "설명 내용"},
    {"step": 2, "description": "설명 내용"}
  ],
  "summary": "최종 결론"
}

질문: {question}
답변: {answer}

주의:
- JSON 외 다른 텍스트 출력하지 마세요.
- steps 배열과 summary 필드를 반드시 포함하세요.
'''

    # 샘플 프롬프트 저장
    cursor.execute('''
        INSERT OR IGNORE INTO prompt_list (prompt)
        VALUES (?)
    ''', (sample_prompt,))

    # 샘플 모델 저장
    cursor.execute('INSERT OR IGNORE INTO llm_model_list (model) VALUES (?)',('openai/gpt-oss-120b',))

    conn.commit()
    conn.close()

if __name__=='__main__':
    init_db()