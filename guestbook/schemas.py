"""Pydantic-схемы гостевой книги."""

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    # Автоматически обрезает пробелы по краям; строки из одних пробелов станут ""
    # и не пройдут проверку min_length=1.
    model_config = ConfigDict(str_strip_whitespace=True)

    author: str = Field(min_length=1, max_length=60)
    text: str = Field(min_length=1, max_length=500)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author: str
    text: str