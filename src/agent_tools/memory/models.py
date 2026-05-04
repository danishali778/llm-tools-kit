from datetime import datetime, timezone
from typing import Any

from pydantic import AwareDatetime, BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryNote(BaseModel):
    id: str
    text: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)
