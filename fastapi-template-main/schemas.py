"""Pydantic описывает HTTP-данные. ORM-модель находится отдельно в models.py."""

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # В JSON ожидаем true/false. Строку "false" не принимаем за boolean.
    done: bool = Field(strict=True)


class TaskResponse(BaseModel):
    # Позволяет читать поля ответа из атрибутов ORM-объекта Task.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool
