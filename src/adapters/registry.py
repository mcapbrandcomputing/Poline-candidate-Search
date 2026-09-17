"""Source adapter registry (S1T2). The single point where adapters are registered/looked up —
CR-9 requires this to be the only place a new adapter needs to be wired in."""
from __future__ import annotations

from src.adapters.base import SourceAdapter
from src.adapters.mock_adapter import MockSourceAdapter

_REGISTRY: dict[str, SourceAdapter] = {
    "mock": MockSourceAdapter(),
}


def register_linkedin_adapter() -> None:
    """Lazily registers the real LinkedIn adapter. Not registered by default at import time --
    constructing LinkedInAdapter() eagerly would otherwise require session credentials to be
    present just to import this module. Call this explicitly once credentials are configured
    (see docs/linkedin_adapter_setup.md)."""
    from src.adapters.linkedin_adapter import LinkedInAdapter

    register("linkedin", LinkedInAdapter())


def register(name: str, adapter: SourceAdapter) -> None:
    _REGISTRY[name] = adapter


def get(name: str) -> SourceAdapter:
    if name not in _REGISTRY:
        raise KeyError(f"No source adapter registered under {name!r}")
    return _REGISTRY[name]


def all_names() -> list[str]:
    return list(_REGISTRY.keys())
