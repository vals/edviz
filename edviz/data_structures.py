"""Core data structures for experimental design representation."""

from dataclasses import dataclass, field
from typing import List, Union, Literal


FactorType = Literal["factor", "observation", "classification", "batch"]
RelationType = Literal[
    "nests",
    "crosses",
    "partial_crosses",
    "classifies",
    "batch_effect",
    "confounded",
]


@dataclass
class Factor:
    """Represents a factor in an experimental design.

    Attributes:
        name: The name of the factor
        n: Number of levels - can be int, list of ints (unbalanced), or string (approximate)
        type: The type of factor
    """
    name: str
    n: Union[int, List[int], str]
    type: FactorType = "factor"

    def __post_init__(self) -> None:
        """Validate factor after initialization."""
        if isinstance(self.n, str):
            if not self.n.startswith("~"):
                raise ValueError(f"String n must start with '~' for approximate counts: {self.n}")
        elif isinstance(self.n, list):
            if not all(isinstance(x, int) and x > 0 for x in self.n):
                raise ValueError(f"List n must contain only positive integers: {self.n}")
        elif isinstance(self.n, int):
            if self.n <= 0:
                raise ValueError(f"Integer n must be positive: {self.n}")
        else:
            raise ValueError(f"n must be int, list of ints, or string: {type(self.n)}")


@dataclass
class Relationship:
    """Represents a relationship between factors.

    Attributes:
        from_factor: Source factor name
        to_factor: Target factor name
        rel_type: Type of relationship
    """
    from_factor: str
    to_factor: str
    rel_type: RelationType

    def __post_init__(self) -> None:
        """Validate relationship after initialization."""
        if not self.from_factor:
            raise ValueError("from_factor cannot be empty")
        if not self.to_factor:
            raise ValueError("to_factor cannot be empty")


@dataclass
class ParsedDesign:
    """Intermediate representation of a parsed experimental design.

    Attributes:
        factors: List of factors in the design
        relationships: List of relationships between factors
        metadata: Additional metadata about the design
    """
    factors: List[Factor] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def get_factor(self, name: str) -> Union[Factor, None]:
        """Get a factor by name.

        Args:
            name: The factor name to search for

        Returns:
            The Factor object if found, None otherwise
        """
        for factor in self.factors:
            if factor.name == name:
                return factor
        return None

    def has_factor(self, name: str) -> bool:
        """Check if a factor exists by name.

        Args:
            name: The factor name to check

        Returns:
            True if factor exists, False otherwise
        """
        return self.get_factor(name) is not None
