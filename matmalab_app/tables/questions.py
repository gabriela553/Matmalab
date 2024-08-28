from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MathProblemInDB(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    question: Mapped[str] = mapped_column(String(300))
    answer: Mapped[str]

    def __repr__(self) -> str:
        return f"MathProblem(question={self.question!r}, answer={self.answer!r})"
