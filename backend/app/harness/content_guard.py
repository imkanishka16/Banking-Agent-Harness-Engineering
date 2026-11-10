"""Scan untrusted data (tool outputs) for instruction-like text before the LLM sees it.

Regex is a first line of defence, not a complete one; production systems add a
classifier model. The architectural point is WHERE the check happens: at the
boundary where untrusted data enters the context. And if something gets past it,
the tool policy still blocks the action. That's defense in depth.
"""
import re

REMOVED = "[removed: suspicious content]"

_PATTERNS = {
    "ignore_instructions": r"ignore\s+(all\s+|any\s+)?(previous|prior|above|your)\s+(instructions|rules)",
    "fake_system_message": r"\b(system|developer)\s+(note|message|prompt|instruction)",
    "addresses_the_ai": r"\b(note|message)\s+to\s+(the\s+)?(ai|assistant|llm|agent)\b",
    "mode_switch": r"\b(admin|developer|god|dan)\s+mode\b",
}
_COMPILED = {name: re.compile(p, re.IGNORECASE) for name, p in _PATTERNS.items()}


def scan(text: str) -> list[str]:
    """Return the names of the patterns found in text (empty list = clean)."""
    return [name for name, pattern in _COMPILED.items() if pattern.search(text or "")]


def sanitize_fields(record: dict, fields: list[str]) -> tuple[dict, list[str]]:
    """Replace suspicious free-text fields. Returns (clean_record, findings)."""
    clean = dict(record)
    findings: list[str] = []
    for field in fields:
        hits = scan(str(clean.get(field, "")))
        if hits:
            clean[field] = REMOVED
            findings.extend(f"{field}:{hit}" for hit in hits)
    return clean, findings