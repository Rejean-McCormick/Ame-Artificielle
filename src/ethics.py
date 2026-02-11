# Ame-Artificielle/src/ethics.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

TraitVector = Dict[str, float]


@dataclass(frozen=True)
class EthicsResult:
    score: float
    action: str  # "none" | "soften" | "refuse"
    notes: str = ""


def mediate(
    *,
    text: str,
    stimulus: str,
    trait_vector: TraitVector,
    threshold: float = 0.65,
    context: Dict[str, Any] | None = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Minimal ethics/gating stub.

    Purpose:
    - Provide a consistent interface for "ethical governance" / mediation.
    - Keep it deterministic and lightweight for MVP.
    - Replace later with a real policy layer.

    Returns:
      (final_text, ethics_info)
    """
    if context is None:
        context = {}

    # --- Heuristic scoring (MVP) ---
    # The score here is not "moral truth"; it's a conservative risk estimate.
    risk = _risk_score(stimulus=stimulus, text=text)

    # Optional: allow "compassion" to slightly reduce harshness but not disable gating.
    compassion = float(trait_vector.get("compassion", 0.0))
    risk_adj = max(0.0, min(1.0, risk - 0.05 * max(0.0, compassion)))

    # --- Decide action ---
    if risk_adj < threshold:
        result = EthicsResult(score=risk_adj, action="none", notes="Below threshold.")
        return text, _info(result)

    # Above threshold: decide soften vs refuse
    # If extreme risk, refuse. Else, soften.
    if risk_adj >= min(1.0, threshold + 0.25):
        result = EthicsResult(score=risk_adj, action="refuse", notes="High-risk content.")
        return _refusal_text(), _info(result)

    result = EthicsResult(score=risk_adj, action="soften", notes="Moderate-risk; softened.")
    return _soften_text(text), _info(result)


def _risk_score(*, stimulus: str, text: str) -> float:
    """
    Simple keyword-based heuristic.
    Extend with classifiers/rules later.
    """
    s = (stimulus or "").lower()
    t = (text or "").lower()

    # Very rough buckets (MVP)
    high_risk = [
        "suicide", "kill myself", "self-harm", "bomb", "explosive", "weapon",
        "child sexual", "rape", "genocide", "terrorist",
    ]
    med_risk = [
        "how to hack", "steal", "credit card", "dox", "harm someone",
        "make poison", "meth", "heroin",
    ]

    score = 0.0

    if any(k in s for k in high_risk) or any(k in t for k in high_risk):
        score = max(score, 0.95)
    if any(k in s for k in med_risk) or any(k in t for k in med_risk):
        score = max(score, 0.75)

    # Default low risk
    if score == 0.0:
        score = 0.10

    return score


def _soften_text(text: str) -> str:
    return (
        "Je ne peux pas aider avec des actions nuisibles ou illégales. "
        "Si tu veux, je peux proposer une alternative sûre.\n\n"
        f"{text}"
    )


def _refusal_text() -> str:
    return (
        "Je ne peux pas aider avec cette demande. "
        "Si tu veux, décris ton objectif de manière non-nuisible, et je t’aiderai à trouver une alternative sûre."
    )


def _info(result: EthicsResult) -> Dict[str, Any]:
    return {"enabled": True, "score": result.score, "action": result.action, "notes": result.notes}
