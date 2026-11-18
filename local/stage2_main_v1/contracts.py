"""Boundaries to the future EQGPT and numerical backend; no old code mutation."""
from __future__ import annotations
from typing import Protocol, Any


class InvalidCandidate(ValueError):
    """Expected parser, regression or integration rejection, not a programming bug."""


class Generator(Protocol):
    fields: tuple[str, ...]
    equation_count: int
    spatial_dimensions: int
    def sample(self, seed: int) -> str | None: ...
    def sft(self, texts: list[str], settings: dict) -> dict:
        """Use all fixed epochs, cosine schedule, no early stop or best rollback.
        Return epochs, early_stopping, settings; retain updated weights.
        """
        ...
    def save(self, path: str) -> None:
        """Save model, tokenizer identity and all RNG/optimizer state needed to resume."""
        ...
    def load(self, path: str) -> None: ...


class Numerics(Protocol):
    fields: tuple[str, ...]
    equation_count: int
    spatial_dimensions: int
    term_count_convention: str
    def parse(self, text: str) -> Any:
        """Only task dimensions/counts are prescribed; no imposed NS constraint."""
        ...
    def structure_key(self, system: Any) -> str: ...
    def term_counts(self, system: Any) -> tuple[int, ...]:
        """Canonical algebraic terms per equation, LHS+RHS before stencil expansion.
        Do not count x/y Laplacian components as separate symbolic terms.
        Exact convention must be reviewed with the new equation representation.
        """
        ...
    def fit(self, system: Any, visible: dict, mask: Any) -> tuple[Any, tuple[float, ...]]:
        """Only 20 visible frames; return window coefficients and three fit R².
        Form derivatives before applying mask, with sufficient stencil support.
        No mandatory explicit pressure evolution or imposed incompressibility.
        """
        ...
    def forecast(self, system: Any, coefficients: Any, visible: dict,
                 future_times: Any, mask: Any) -> Any:
        """Return [20,H,W,3]. Never receive future field values.
        Boundary closure, pressure gauge, integrator and implicit-system support
        must be declared and audited by the replacement backend.
        """
        ...


def check_capabilities(generator, numerics, config):
    expected = (tuple(config['fields']), config['equation_count'], config['spatial_dimensions'])
    for name, obj in [('generator', generator), ('numerics', numerics)]:
        actual = (tuple(obj.fields), obj.equation_count, obj.spatial_dimensions)
        if actual != expected:
            raise ValueError(f'{name} capability mismatch: expected {expected}, got {actual}')
    if numerics.term_count_convention != 'canonical_lhs_plus_rhs_before_stencil_expansion':
        raise ValueError('System term-count convention has not been matched')
