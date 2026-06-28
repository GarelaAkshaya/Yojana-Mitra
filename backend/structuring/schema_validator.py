from __future__ import annotations

from backend.schemas.scheme import Scheme


def validate_scheme(payload: Scheme | dict) -> Scheme:
    if isinstance(payload, Scheme):
        return payload
    return Scheme.model_validate(payload)
