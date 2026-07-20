from __future__ import annotations

import hashlib


def stable_id(prefix: str, *parts: object, length: int = 16) -> str:
    if not prefix:
        raise ValueError("prefix is required")
    payload = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{digest}"

