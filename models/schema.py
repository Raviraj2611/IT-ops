from dataclasses import dataclass


@dataclass
class ConfidenceResult:
    score: float
    decision: str
    signals: dict