from fastapi import FastAPI
from pydantic import BaseModel
from chain import qa_to_cot
import uvicorn

app = FastAPI()

class QA(BaseModel):
    q: str # question string
    a: str # answer string

@app.post("/qa2cot")
def qa2cot(data:QA):
    result = qa_to_cot(data.q, data.a)
    return result

if __name__=='__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)