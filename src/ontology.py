# Ame-Artificielle/src/ontology.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class DigitEntry:
    """One raw ontology entry."""
    index: int
    digit: int
    analysis: Dict[str, str]


class OntologyError(RuntimeError):
    pass


def invert_digit(d: int) -> int:
    """
    Inversion rule used in the project:
      1 <-> 9, 2 <-> 8, 3 <-> 7, 4 <-> 6, 5 <-> 5, 0 -> 0.
    """
    if d == 0:
        return 0
    if 1 <= d <= 9:
        return 10 - d
    raise ValueError(f"digit out of supported range for inversion: {d}")


class PiOntology:
    """
    Loads pi_ontology.json and provides:
      - access by digit (0..9)
      - optional digit inversion (Pythagorean inverted mapping)
      - merged view (tradition -> text)
      - missing / incomplete detection
      - patching (to fill digit 2 or override traditions)
    """

    def __init__(self, path: str | Path = "data/pi_ontology.json") -> None:
        self.path = Path(path)
        self._entries: List[DigitEntry] = []
        self._by_digit: Dict[int, List[DigitEntry]] = {}
        self._patches: Dict[int, Dict[str, str]] = {}

        raw = self._read_text(self.path)
        data = self._parse_lenient_json(raw)
        self._entries = self._normalize_entries(data)
        self._by_digit = self._index_by_digit(self._entries)

    # ---------- public API ----------

    @property
    def digits_present(self) -> List[int]:
        return sorted(self._by_digit.keys())

    def is_digit_missing_or_incomplete(self, digit: int, *, inverted: bool = False) -> bool:
        d = invert_digit(digit) if inverted else digit
        entries = self._by_digit.get(d, [])
        if not entries:
            return True

        # If every entry only contains "Note" in analysis, treat as incomplete.
        def only_note(e: DigitEntry) -> bool:
            keys = {k.strip().lower() for k in e.analysis.keys()}
            return keys == {"note"} or (len(keys) == 0)

        if all(only_note(e) for e in entries):
            return True

        # If patched, it's not missing.
        if d in self._patches and self._patches[d]:
            return False

        return False

    def get_entries(self, digit: int, *, inverted: bool = False) -> List[DigitEntry]:
        d = invert_digit(digit) if inverted else digit
        return list(self._by_digit.get(d, []))

    def get_analysis(
        self,
        digit: int,
        *,
        inverted: bool = False,
        merged: bool = True,
        merge_policy: str = "last",
    ) -> Dict[str, str] | List[Dict[str, str]]:
        """
        merged=True  -> returns one dict {tradition -> text}
        merged=False -> returns list of analysis dicts (raw)
        merge_policy: "first" | "last" | "concat"
          - first: first seen wins
          - last: last seen wins (default)
          - concat: join duplicates with " / "
        """
        d = invert_digit(digit) if inverted else digit
        entries = self._by_digit.get(d, [])
        raw_list = [dict(e.analysis) for e in entries]

        patch = self._patches.get(d, {})

        if not merged:
            # Apply patch as an extra "virtual" analysis entry at the end (if any).
            if patch:
                raw_list.append(dict(patch))
            return raw_list

        merged_map: Dict[str, str] = {}
        for e in entries:
            for k, v in e.analysis.items():
                merged_map = self._merge_key(merged_map, k, v, merge_policy=merge_policy)

        for k, v in patch.items():
            merged_map = self._merge_key(merged_map, k, v, merge_policy=merge_policy)

        return merged_map

    def get_tradition_text(
        self,
        digit: int,
        tradition: str,
        *,
        inverted: bool = False,
        default: Optional[str] = None,
    ) -> Optional[str]:
        analysis = self.get_analysis(digit, inverted=inverted, merged=True)
        # normalize key match (case-insensitive)
        t = tradition.strip().lower()
        for k, v in analysis.items():
            if k.strip().lower() == t:
                return v
        return default

    def patch_digit(self, digit: int, patch: Dict[str, str], *, inverted: bool = False) -> None:
        """
        Add/override analysis traditions for a digit.
        Useful to fill the missing "2" or to define inverted-specific meanings.
        """
        d = invert_digit(digit) if inverted else digit
        if d not in self._patches:
            self._patches[d] = {}
        for k, v in patch.items():
            self._patches[d][str(k)] = str(v)

    def summarize_digit(
        self,
        digit: int,
        *,
        inverted: bool = False,
        max_items: int = 6,
        merge_policy: str = "last",
    ) -> List[Tuple[str, str]]:
        """
        Returns a short list of (tradition, excerpt) items for display/debug.
        """
        analysis = self.get_analysis(digit, inverted=inverted, merged=True, merge_policy=merge_policy)
        items = sorted(analysis.items(), key=lambda kv: kv[0].lower())
        out: List[Tuple[str, str]] = []
        for k, v in items[:max_items]:
            excerpt = self._excerpt(v, 220)
            out.append((k, excerpt))
        return out

    # ---------- internals ----------

    @staticmethod
    def _read_text(path: Path) -> str:
        if not path.exists():
            raise OntologyError(
                f"Ontology file not found: {path} "
                f"(expected in repo at data/pi_ontology.json)."
            )
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _parse_lenient_json(raw: str) -> Any:
        """
        pi_ontology.json may be malformed (e.g., concatenated arrays: `][`).
        Strategy:
          1) try json.loads
          2) if fails, repair common pattern: `]\s*\[` -> `,`
        """
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            repaired = re.sub(r"\]\s*\[", ",", raw.strip())
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as e2:
                raise OntologyError(
                    "Failed to parse pi_ontology.json even after lenient repair. "
                    "Fix the file or export a valid single JSON array."
                ) from e2

    @staticmethod
    def _normalize_entries(data: Any) -> List[DigitEntry]:
        """
        Expected format: a JSON array of objects {index, digit, analysis}.
        Any object missing required keys is skipped.
        """
        if not isinstance(data, list):
            raise OntologyError("pi_ontology.json root must be a JSON array.")

        entries: List[DigitEntry] = []
        for obj in data:
            if not isinstance(obj, dict):
                continue
            if "digit" not in obj or "analysis" not in obj:
                continue
            digit = obj.get("digit")
            index = obj.get("index", -1)
            analysis = obj.get("analysis", {})
            if not isinstance(digit, int):
                # sometimes digit could be string
                try:
                    digit = int(digit)
                except Exception:
                    continue
            if not isinstance(index, int):
                try:
                    index = int(index)
                except Exception:
                    index = -1
            if not isinstance(analysis, dict):
                continue

            # enforce string->string in analysis
            clean_analysis: Dict[str, str] = {}
            for k, v in analysis.items():
                if v is None:
                    continue
                clean_analysis[str(k)] = str(v)

            entries.append(DigitEntry(index=index, digit=digit, analysis=clean_analysis))

        if not entries:
            raise OntologyError("No usable entries found in pi_ontology.json.")
        return entries

    @staticmethod
    def _index_by_digit(entries: Iterable[DigitEntry]) -> Dict[int, List[DigitEntry]]:
        by: Dict[int, List[DigitEntry]] = {}
        for e in entries:
            by.setdefault(e.digit, []).append(e)
        return by

    @staticmethod
    def _merge_key(
        merged: Dict[str, str],
        key: str,
        value: str,
        *,
        merge_policy: str,
    ) -> Dict[str, str]:
        k = str(key)
        v = str(value)
        if merge_policy not in {"first", "last", "concat"}:
            raise ValueError(f"unknown merge_policy: {merge_policy}")

        if k not in merged:
            merged[k] = v
            return merged

        if merge_policy == "first":
            return merged
        if merge_policy == "last":
            merged[k] = v
            return merged

        # concat
        if merged[k].strip() == v.strip():
            return merged
        merged[k] = f"{merged[k]} / {v}"
        return merged

    @staticmethod
    def _excerpt(text: str, n: int) -> str:
        t = re.sub(r"\s+", " ", text).strip()
        return t if len(t) <= n else (t[: n - 1] + "…")


if __name__ == "__main__":
    # Minimal smoke test (expects repo layout).
    onto = PiOntology("data/pi_ontology.json")
    for d in range(0, 10):
        missing = onto.is_digit_missing_or_incomplete(d)
        inv_missing = onto.is_digit_missing_or_incomplete(d, inverted=True)
        print(f"digit={d} missing={missing} | inverted_digit={invert_digit(d) if d else 0} inv_missing={inv_missing}")
