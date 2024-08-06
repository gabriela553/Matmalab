from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from matmalab_app import config
from matmalab_app.tables.questions import Base, MathProblemInDB

app = FastAPI()


class MathProblem(BaseModel):
    id: int | None = None
    question: str
    answer: str

    @staticmethod
    def from_math_problem_in_db(math_problem_in_db: MathProblemInDB):
        math_problem = MathProblem(id=math_problem_in_db.id, question=math_problem_in_db.question, answer=math_problem_in_db.answer)
        return math_problem

    def to_math_problem_in_db(self):
        math_problem = MathProblemInDB(id=self.id, question=self.question, answer=self.answer)
        return math_problem


async def get_db():
    engine = create_engine(config.CONNECTION_STRING, echo=True)
    db = Session(engine)
    Base.metadata.create_all(engine)
    try:
        yield db
    finally:
        db.close()


@app.post("/matmalab")
async def add_question(math_problem: MathProblem, db=Depends(get_db)):
    math_problem = math_problem.to_math_problem_in_db()
    db.add(math_problem)
    db.commit()
    return math_problem


@app.delete("/matmalab")
async def delete_question(db=Depends(get_db)):
    questions = db.query(MathProblemInDB).all()
    for question in questions:
        db.delete(question)
    db.commit()


@app.get("/matmalab")
async def fetch_questions(db=Depends(get_db)):
    questions = []
    results = db.query(MathProblemInDB).all()
    if not results:
        raise HTTPException(status_code=400, detail="Questions not found")
    for result in results:
        question = MathProblem.from_math_problem_in_db(result)
        questions.append(question)
    return questions

"""
@app.post("/matmalab/")
async def add_result():
    print("Well done")

"""
