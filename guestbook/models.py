"""ORM-модель SQLAlchemy для отзывов в гостевой книге."""

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Review(Base):
    __tablename__ = "review"
    __table_args__ = (
        CheckConstraint("length(author) BETWEEN 1 AND 60", name="review_author_length"),
        CheckConstraint("length(text) BETWEEN 1 AND 500", name="review_text_length"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(60))
    text: Mapped[str] = mapped_column(String(500))