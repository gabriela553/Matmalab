import json

import requests
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from matmalab_app import config
from matmalab_app.tables.questions import Base, MathProblemInDB

app = FastAPI()

OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_MODEL = "mathstral"
HTTP_OK = 200

class MathProblem(BaseModel):
    id: int | None = None
    question: str
    answer: str

    @staticmethod
    def from_math_problem_in_db(math_problem_in_db: MathProblemInDB):
        return MathProblem(id=math_problem_in_db.id, question=math_problem_in_db.question, answer=math_problem_in_db.answer)

    def to_math_problem_in_db(self):
        return MathProblemInDB(id=self.id, question=self.question, answer=self.answer)


async def get_db():
    engine = create_engine(config.CONNECTION_STRING, echo=True)
    db = Session(engine)
    Base.metadata.create_all(engine)
    try:
        yield db
    finally:
        db.close()


def model_exists(model_name: str):
    response = requests.get(f"{OLLAMA_URL}/models", timeout=30)
    if response.status_code == HTTP_OK:
        models = response.json().get("models", [])
        return model_name in models
    return False


def pull_model(model_name: str):
    if not model_exists(model_name):
        response = requests.post("http://ollama:11434/api/pull",
                                 json={"model": model_name}, timeout=30,
                            )
        if response.status_code != HTTP_OK:
            raise Exception(f"Failed to pull model: {response.text}")


def generate_math_problem():

    prompt = """Generate a basic math problem and return it in a JSON format with these keys: 'question' and 'answer'.
    The 'question' should describe the problem, and 'answer' should be the solution. For example:
{
  "question": "What is 9 divided by 3?",
  "answer": "3"
}
"""
    pull_model("mathstral")
    payload = {
        "model": "mathstral",
        "prompt": prompt,
        "format": "json",
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == HTTP_OK:
            return response.json()["response"]
        raise HTTPException(status_code=404, detail=f"Request failed with status code {response.status_code}")
    except ValueError as ve:
        return {"error": "Failed to parse JSON response", "details": str(ve)}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "details": "The request took too long to complete."}


@app.post("/matmalab")
async def add_question(db: Session = Depends(get_db)):
    math_problem = generate_math_problem()
    while "question" not in math_problem or "answer" not in math_problem:
        math_problem = generate_math_problem()
    math_problem_des = json.loads(math_problem)
    math_problem = MathProblem(question=math_problem_des["question"],
                               answer=math_problem_des["answer"])
    math_problem = math_problem.to_math_problem_in_db()
    db.add(math_problem)
    db.commit()
    return math_problem



@app.delete("/matmalab")
async def delete_question(db: Session = Depends(get_db)):
    questions = db.query(MathProblemInDB).all()
    for question in questions:
        db.delete(question)
    db.commit()


@app.get("/matmalab")
async def fetch_questions(db: Session = Depends(get_db)):
    questions = []
    results = db.query(MathProblemInDB).all()
    if not results:
        raise HTTPException(status_code=400, detail="Questions not found")
    for result in results:
        question = MathProblem.from_math_problem_in_db(result)
        questions.append(question)
    return questions
