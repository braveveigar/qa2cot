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
주어진 질문과 답변을 보고 답변에 필요한 Chain of Thought을 딕셔너리 구조로 단계별로 작성해주세요.
답변은 무조건 주어진 출력 형식에 맞춰주세요

질문: {question}
답변: {answer}

출력 형식:
{{"steps":[{{"step": 1, "description": "..."}},{{"step": 2, "description": "..."}},...],"summary": "..."}}
'''

    # 샘플 프롬프트 저장
    cursor.execute('''
        INSERT OR IGNORE INTO prompt_list (prompt)
        VALUES (?)
    ''', (sample_prompt,))

    # 샘플 모델 저장
    cursor.execute('INSERT OR IGNORE INTO llm_model_list (model) VALUES (?)',('openai/gpt-oss-120b',))
    cursor.execute('INSERT OR IGNORE INTO llm_model_list (model) VALUES (?)',('meta-llama/Llama-2-13b-chat-hf',))

    conn.commit()
    conn.close()

if __name__=='__main__':
    init_db()