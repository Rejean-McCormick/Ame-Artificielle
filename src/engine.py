# Ame-Artificielle/src/engine.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


TraitVector = Dict[str, float]


@dataclass(frozen=True)
class EngineConfig:
    """
    Core runtime configuration.

    Notes:
    - inversion_enabled: applies the "Pythagorean inverted" mapping (9->1, 8->2, ..., 1->9; 0 stays 0)
      AFTER standard reduction (see numerology.py).
    - axis_default: initial position on the 1..9 axis used for interpolation/dynamics.
    """
    inversion_enabled: bool = True
    axis_default: int = 5  # neutral midpoint
    memory_max_turns: int = 12

    # Style sliders (0..1), can be overridden per-call
    tone: float = 0.5
    humor: float = 0.2
    complexity: float = 0.5

    # Ethics / safety knobs (placeholder)
    ethics_enabled: bool = True
    ethics_threshold: float = 0.65


@dataclass
class SoulState:
    """
    Runtime state (profile + dynamics).
    """
    # Stable-ish personality
    trait_vector: TraitVector = field(default_factory=dict)
    digit_archetype: Optional[int] = None  # 0..9, after reduction (+ inversion if enabled)

    # Dynamics
    axis_position: int = 5  # 1..9
    mood: Optional[int] = None  # optional 2..8 (intermediate spectrum)

    # Memory (short)
    memory: List[Dict[str, Any]] = field(default_factory=list)

    # Last debug
    last_trace: Dict[str, Any] = field(default_factory=dict)


class ArtificialSoulEngine:
    """
    Minimal orchestration layer:
      numerology -> ontology -> interpolation -> ethics -> response assembly

    This file intentionally keeps the implementation shallow:
    - numerology.py owns the signature derivation + reductions + inversion rules
    - ontology.py owns digit->semantics + digit->trait projection
    - interpolation.py owns axis/mood interpolation shaping
    - ethics.py owns gating/mediation
    """

    def __init__(self, *, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()

        # Lazy imports to keep module boundaries simple
        from . import numerology as _numerology
        from . import ontology as _ontology
        from . import interpolation as _interpolation
        from . import ethics as _ethics

        self._numerology = _numerology
        self._ontology = _ontology
        self._interpolation = _interpolation
        self._ethics = _ethics

    # ----------------------------
    # Profile construction
    # ----------------------------
    def build_state_from_identity(
        self,
        *,
        identity: Dict[str, Any],
        axis_position: Optional[int] = None,
    ) -> SoulState:
        """
        identity: flexible payload (name/date/etc.). numerology.py decides what it supports.

        Returns a SoulState with:
        - digit_archetype set
        - trait_vector computed
        - axis_position set
        """
        # 1) Build signature + reduce
        signature = self._numerology.compute_signature(identity)
        reduced = self._numerology.reduce_signature(signature)

        # 2) Archetype digit (optionally inverted)
        digit_archetype = reduced.get("core_digit")
        if digit_archetype is None:
            raise ValueError("numerology.reduce_signature() must return reduced['core_digit'] (0..9).")

        if self.config.inversion_enabled:
            digit_archetype = self._numerology.invert_digit(digit_archetype)

        # 3) Traits from ontology
        trait_vector = self._ontology.digit_to_traits(digit_archetype)

        # 4) Initialize state
        state = SoulState(
            trait_vector=trait_vector,
            digit_archetype=digit_archetype,
            axis_position=axis_position if axis_position is not None else self._clamp_axis(self.config.axis_default),
            mood=None,
            memory=[],
            last_trace={
                "signature": signature,
                "reduced": reduced,
                "digit_archetype": digit_archetype,
                "inversion_enabled": self.config.inversion_enabled,
            },
        )
        return state

    # ----------------------------
    # Reaction / simulation
    # ----------------------------
    def react(
        self,
        *,
        state: SoulState,
        stimulus: str,
        sliders: Optional[Dict[str, float]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Produces a structured response:
          {
            "text": ...,
            "axis_position": ...,
            "mood": ...,
            "trace": {...},
            "ethics": {...}
          }
        """
        if context is None:
            context = {}

        # Merge sliders (per-call overrides)
        tone = self._pick_slider(sliders, "tone", self.config.tone)
        humor = self._pick_slider(sliders, "humor", self.config.humor)
        complexity = self._pick_slider(sliders, "complexity", self.config.complexity)

        # 1) Update dynamics (axis/mood) from stimulus
        axis_next, mood_next, dyn_trace = self._interpolation.update_dynamics(
            axis_position=state.axis_position,
            trait_vector=state.trait_vector,
            stimulus=stimulus,
            context=context,
        )

        # 2) Generate a draft response (simple, deterministic placeholder)
        draft = self._compose_response_text(
            trait_vector=state.trait_vector,
            axis_position=axis_next,
            mood=mood_next,
            stimulus=stimulus,
            tone=tone,
            humor=humor,
            complexity=complexity,
        )

        # 3) Ethics mediation (optional)
        ethics_info = {"enabled": self.config.ethics_enabled, "action": "none", "score": None}
        final_text = draft
        if self.config.ethics_enabled:
            final_text, ethics_info = self._ethics.mediate(
                text=draft,
                stimulus=stimulus,
                trait_vector=state.trait_vector,
                threshold=self.config.ethics_threshold,
                context=context,
            )

        # 4) Commit state updates + memory
        state.axis_position = axis_next
        state.mood = mood_next
        self._push_memory(state, stimulus=stimulus, response=final_text)

        # 5) Trace
        trace = {
            "digit_archetype": state.digit_archetype,
            "axis_position_before": state.last_trace.get("axis_position", None),
            "axis_position_after": axis_next,
            "mood": mood_next,
            "sliders": {"tone": tone, "humor": humor, "complexity": complexity},
            "dynamics": dyn_trace,
        }
        state.last_trace = {**state.last_trace, "axis_position": axis_next, "mood": mood_next, "react_trace": trace}

        return {
            "text": final_text,
            "axis_position": axis_next,
            "mood": mood_next,
            "trace": trace,
            "ethics": ethics_info,
        }

    # ----------------------------
    # Internals
    # ----------------------------
    def _compose_response_text(
        self,
        *,
        trait_vector: TraitVector,
        axis_position: int,
        mood: Optional[int],
        stimulus: str,
        tone: float,
        humor: float,
        complexity: float,
    ) -> str:
        """
        Placeholder generator.
        Replace with your actual generation stack (LLM or templates) in a higher layer.
        """
        # Extract a few dominant traits (by absolute weight)
        top_traits = sorted(trait_vector.items(), key=lambda kv: abs(kv[1]), reverse=True)[:5]
        traits_str = ", ".join([f"{k}:{v:+.2f}" for k, v in top_traits]) if top_traits else "none"

        # Simple axis shading
        axis_style = self._interpolation.axis_descriptor(axis_position)

        # Light formatting choices based on sliders (still deterministic)
        prefix = "Réponse" if tone >= 0.5 else "Note"
        if humor >= 0.66:
            prefix += " (léger)"
        if complexity >= 0.66:
            detail = f"\n\nContexte interne: axis={axis_position} ({axis_style}), mood={mood}, traits=[{traits_str}]"
        else:
            detail = ""

        return f"{prefix}: {self._interpolation.shape_text(stimulus=stimulus, axis_position=axis_position)}{detail}"

    def _push_memory(self, state: SoulState, *, stimulus: str, response: str) -> None:
        state.memory.append({"stimulus": stimulus, "response": response})
        if len(state.memory) > self.config.memory_max_turns:
            # drop oldest
            state.memory = state.memory[-self.config.memory_max_turns :]

    @staticmethod
    def _pick_slider(sliders: Optional[Dict[str, float]], key: str, default: float) -> float:
        if not sliders or key not in sliders:
            return ArtificialSoulEngine._clamp01(default)
        return ArtificialSoulEngine._clamp01(sliders[key])

    @staticmethod
    def _clamp_axis(x: int) -> int:
        return max(1, min(9, int(x)))

    @staticmethod
    def _clamp01(x: float) -> float:
        try:
            xf = float(x)
        except Exception:
            return 0.5
        return max(0.0, min(1.0, xf))
