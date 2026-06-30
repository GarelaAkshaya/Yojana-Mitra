from __future__ import annotations

import json
from pathlib import Path
from typing import Any, get_origin, get_type_hints

try:
    from pydantic import BaseModel as PydanticBaseModel  # noqa: F401
    from pydantic import Field as PydanticField  # noqa: F401
except ImportError:

    class _FieldInfo:
        def __init__(self, default: Any = None, default_factory: Any = None) -> None:
            self.default = default
            self.default_factory = default_factory

        def value(self) -> Any:
            if self.default_factory is not None:
                return self.default_factory()
            return self.default

    def Field(default: Any = None, default_factory: Any = None, **_: Any) -> Any:
        return _FieldInfo(default=default, default_factory=default_factory)

    class BaseModel:
        def __init__(self, **data: Any) -> None:
            annotations = _all_annotations(type(self))
            for name, annotation in annotations.items():
                default = getattr(type(self), name, None)
                if name in data:
                    value = data[name]
                elif isinstance(default, _FieldInfo):
                    value = default.value()
                elif default is not None:
                    value = default
                else:
                    value = None
                setattr(self, name, _coerce_value(annotation, value))

        @classmethod
        def model_validate(cls, payload: Any) -> Any:
            if isinstance(payload, cls):
                return payload
            return cls(**payload)

        def model_dump(self) -> dict[str, Any]:
            return {
                name: _dump_value(getattr(self, name))
                for name in _all_annotations(type(self))
            }

        def model_dump_json(self) -> str:
            return json.dumps(self.model_dump(), ensure_ascii=False)


def _all_annotations(cls: type) -> dict[str, Any]:
    annotations: dict[str, Any] = {}
    for base in reversed(cls.__mro__):
        try:
            annotations.update(get_type_hints(base))
        except Exception:
            annotations.update(getattr(base, "__annotations__", {}))
    return annotations


def _coerce_value(annotation: Any, value: Any) -> Any:
    if value is None:
        return value
    if annotation is Path and isinstance(value, str):
        return Path(value)
    if (
        isinstance(annotation, type)
        and issubclass(annotation, BaseModel)
        and isinstance(value, dict)
    ):
        return annotation.model_validate(value)
    origin = get_origin(annotation)
    if origin is list and value is None:
        return []
    return value


def _dump_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_dump_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _dump_value(item) for key, item in value.items()}
    return value
