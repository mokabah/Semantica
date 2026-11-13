"""Result types shared by the verification checks."""

from __future__ import annotations

from dataclasses import dataclass, field

from semantica.core.status import CheckStatus, OverallStatus


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one named check, always accompanied by an explanation."""

    name: str
    status: CheckStatus
    explanation: str
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status.value,
            "explanation": self.explanation,
            "details": self.details,
        }


@dataclass(frozen=True)
class VerificationResult:
    """All checks for one source/candidate pair and the aggregated status."""

    source: str
    candidate: str
    checks: tuple[CheckResult, ...]
    overall: OverallStatus
    explanation: str
    unverified: tuple[str, ...]

    def check(self, name: str) -> CheckResult:
        for result in self.checks:
            if result.name == name:
                return result
        raise KeyError(name)

    def status_of(self, name: str) -> CheckStatus:
        return self.check(name).status
