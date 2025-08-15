FROM python:3.10-slim

WORKDIR /app

# 빌드 캐시 활용 위해 requirements 먼저 복사
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 복사
COPY . .

# 서버 실행
CMD ["python3", "server.py"]