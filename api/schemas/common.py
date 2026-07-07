"""Enveloppe de réponse normalisée — cf. L032.1 §6."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Enveloppe(BaseModel, Generic[T]):
    success: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"
    data: T


class ErreurDetail(BaseModel):
    code: str
    message: str


class EnveloppeErreur(BaseModel):
    success: bool = False
    error: ErreurDetail
