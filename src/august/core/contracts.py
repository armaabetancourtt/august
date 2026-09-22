from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class DataClassification(StrEnum):
    REAL_PUBLIC = "real_public"
    SYNTHETIC = "synthetic"
    DERIVED = "derived"


class Provenance(BaseModel):
    classification: DataClassification
    source: str
    source_url: str | None = None
    generated_by: str | None = None
    notes: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    label: str
    value: float | str
    direction: str | None = None
    method: str
    confidence: float | None = Field(default=None, ge=0, le=1)


class DecisionEnvelope(BaseModel):
    decision: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence]
    assumptions: list[str]
    limitations: list[str]
    provenance: list[Provenance]
    metadata: dict[str, Any] = Field(default_factory=dict)
