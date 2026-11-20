"""ORM-модель SQLAlchemy описывает таблицу и объекты, связанные с ней."""

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "task"
    __table_args__ = (
        CheckConstraint("length(title) BETWEEN 1 AND 120", name="task_title_length"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    done: Mapped[bool] = mapped_column(default=False)
