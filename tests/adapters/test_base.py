import pytest

from src.adapters.base import SourceAdapter


def test_source_adapter_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        SourceAdapter()


def test_source_adapter_requires_fetch_candidates_implementation():
    class Incomplete(SourceAdapter):
        pass

    with pytest.raises(TypeError):
        Incomplete()
