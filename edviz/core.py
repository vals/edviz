"""Core ExperimentalDesign class."""

import json
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
import networkx as nx

from edviz.parser import DesignGrammarParser
from edviz.data_structures import Factor, Relationship, ParsedDesign, FactorType, RelationType
from edviz.validators import DesignValidator


class ExperimentalDesign:
    """Core class representing an experimental design.

    This class provides methods for parsing, validating, and exporting experimental designs.
    """

    def __init__(self) -> None:
        """Initialize an empty experimental design."""
        self.parsed_design = ParsedDesign()
        self._validator = DesignValidator()

    @classmethod
    def from_grammar(cls, grammar_string: str) -> "ExperimentalDesign":
        """Parse grammar string into design object.

        Args:
            grammar_string: The grammar string to parse

        Returns:
            ExperimentalDesign object

        Raises:
            ValueError: If grammar is invalid
        """
        design = cls()
        parser = DesignGrammarParser()
        design.parsed_design = parser.parse(grammar_string)
        return design

    @classmethod
    def from_dict(cls, design_dict: Dict[str, Any]) -> "ExperimentalDesign":
        """Create from dictionary representation.

        Args:
            design_dict: Dictionary representation of the design

        Returns:
            ExperimentalDesign object

        Raises:
            ValueError: If dictionary format is invalid
        """
        design = cls()

        # Parse factors
        if "factors" in design_dict:
            for factor_dict in design_dict["factors"]:
                design.add_factor(
                    factor_dict["name"],
                    factor_dict["n"],
                    factor_dict.get("type", "factor")
                )

        # Parse relationships
        if "relationships" in design_dict:
            for rel_dict in design_dict["relationships"]:
                from_factor = rel_dict["from"]
                to_factor = rel_dict["to"]
                rel_type = rel_dict["type"]

                design.parsed_design.relationships.append(
                    Relationship(from_factor, to_factor, rel_type)
                )

        # Parse metadata
        if "metadata" in design_dict:
            design.parsed_design.metadata = design_dict["metadata"]

        return design

    def add_factor(
        self,
        name: str,
        n: Union[int, List[int], str],
        factor_type: FactorType = "factor"
    ) -> None:
        """Add a factor. n can be: int, list of ints, or string like '~5000'.

        Args:
            name: Factor name
            n: Number of levels (int, list of ints, or approximate string)
            factor_type: Type of factor

        Raises:
            ValueError: If factor already exists
        """
        if self.parsed_design.has_factor(name):
            raise ValueError(f"Factor '{name}' already exists")

        self.parsed_design.factors.append(Factor(name, n, factor_type))

    def add_nesting(self, parent: str, child: str) -> None:
        """Add nesting relationship: parent > child.

        Args:
            parent: Parent factor name
            child: Child factor name

        Raises:
            ValueError: If factors don't exist
        """
        if not self.parsed_design.has_factor(parent):
            raise ValueError(f"Factor '{parent}' does not exist")
        if not self.parsed_design.has_factor(child):
            raise ValueError(f"Factor '{child}' does not exist")

        self.parsed_design.relationships.append(
            Relationship(parent, child, "nests")
        )

    def add_crossing(self, factor1: str, factor2: str, partial: bool = False) -> None:
        """Add crossing: × for full, ◊ for partial.

        Args:
            factor1: First factor name
            factor2: Second factor name
            partial: If True, creates partial crossing

        Raises:
            ValueError: If factors don't exist
        """
        if not self.parsed_design.has_factor(factor1):
            raise ValueError(f"Factor '{factor1}' does not exist")
        if not self.parsed_design.has_factor(factor2):
            raise ValueError(f"Factor '{factor2}' does not exist")

        rel_type: RelationType = "partial_crosses" if partial else "crosses"
        self.parsed_design.relationships.append(
            Relationship(factor1, factor2, rel_type)
        )

    def add_classification(self, factor: str, classifier: str) -> None:
        """Add classification relationship: factor : classifier.

        Args:
            factor: Factor to be classified
            classifier: Classifier factor

        Raises:
            ValueError: If factors don't exist
        """
        if not self.parsed_design.has_factor(factor):
            raise ValueError(f"Factor '{factor}' does not exist")
        if not self.parsed_design.has_factor(classifier):
            raise ValueError(f"Factor '{classifier}' does not exist")

        self.parsed_design.relationships.append(
            Relationship(factor, classifier, "classifies")
        )

        # Mark classifier as classification type
        classifier_factor = self.parsed_design.get_factor(classifier)
        if classifier_factor:
            classifier_factor.type = "classification"

    def add_batch_effect(self, batch_factor: str, affected: List[str]) -> None:
        """Add batch effect: batch == affected_factors.

        Args:
            batch_factor: Batch factor name
            affected: List of affected factor names

        Raises:
            ValueError: If factors don't exist
        """
        if not self.parsed_design.has_factor(batch_factor):
            raise ValueError(f"Factor '{batch_factor}' does not exist")

        batch_f = self.parsed_design.get_factor(batch_factor)
        if batch_f:
            batch_f.type = "batch"

        for affected_factor in affected:
            if not self.parsed_design.has_factor(affected_factor):
                raise ValueError(f"Factor '{affected_factor}' does not exist")

            self.parsed_design.relationships.append(
                Relationship(batch_factor, affected_factor, "batch_effect")
            )

    def add_confound(self, factor1: str, factor2: str) -> None:
        """Add confounding: factor1 ≈≈ factor2.

        Args:
            factor1: First factor name
            factor2: Second factor name

        Raises:
            ValueError: If factors don't exist
        """
        if not self.parsed_design.has_factor(factor1):
            raise ValueError(f"Factor '{factor1}' does not exist")
        if not self.parsed_design.has_factor(factor2):
            raise ValueError(f"Factor '{factor2}' does not exist")

        self.parsed_design.relationships.append(
            Relationship(factor1, factor2, "confounded")
        )

    @property
    def factors(self) -> List[Factor]:
        """Get list of factors."""
        return self.parsed_design.factors

    @property
    def relationships(self) -> List[Relationship]:
        """Get list of relationships."""
        return self.parsed_design.relationships

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary representation.

        Returns:
            Dictionary representation of the design
        """
        return {
            "schema_version": "1.0",
            "factors": [
                {
                    "name": factor.name,
                    "n": factor.n,
                    "type": factor.type,
                }
                for factor in self.parsed_design.factors
            ],
            "relationships": [
                {
                    "from": rel.from_factor,
                    "to": rel.to_factor,
                    "type": rel.rel_type,
                }
                for rel in self.parsed_design.relationships
            ],
            "metadata": self.parsed_design.metadata,
        }

    def to_json(self, filepath: Optional[Union[str, Path]] = None) -> str:
        """Export to JSON string or file.

        Args:
            filepath: Optional path to write JSON file

        Returns:
            JSON string representation
        """
        design_dict = self.to_dict()
        json_str = json.dumps(design_dict, indent=2)

        if filepath:
            path = Path(filepath)
            path.write_text(json_str, encoding="utf-8")

        return json_str

    def to_dot(self, filepath: Optional[Union[str, Path]] = None) -> str:
        """Export to Graphviz DOT format.

        Args:
            filepath: Optional path to write DOT file

        Returns:
            DOT format string
        """
        from edviz.exporters.dot import DotExporter
        exporter = DotExporter()
        dot_str = exporter.export(self.parsed_design)

        if filepath:
            path = Path(filepath)
            path.write_text(dot_str, encoding="utf-8")

        return dot_str

    def to_graphml(self, filepath: Optional[Union[str, Path]] = None) -> str:
        """Export to GraphML format.

        Args:
            filepath: Optional path to write GraphML file

        Returns:
            GraphML format string
        """
        from edviz.exporters.graphml import GraphMLExporter
        exporter = GraphMLExporter()
        graphml_str = exporter.export(self.parsed_design)

        if filepath:
            path = Path(filepath)
            path.write_text(graphml_str, encoding="utf-8")

        return graphml_str

    def to_networkx(self) -> nx.DiGraph:
        """Convert to NetworkX directed graph.

        Returns:
            NetworkX DiGraph object
        """
        graph = nx.DiGraph()

        # Add nodes
        for factor in self.parsed_design.factors:
            graph.add_node(
                factor.name,
                n=factor.n,
                type=factor.type,
            )

        # Add edges
        for rel in self.parsed_design.relationships:
            graph.add_edge(
                rel.from_factor,
                rel.to_factor,
                rel_type=rel.rel_type,
            )

        return graph

    def ascii_diagram(self, width: int = 60) -> str:
        """Generate ASCII box diagram.

        Args:
            width: Width of the diagram

        Returns:
            ASCII diagram string
        """
        from edviz.visualizers.ascii_advanced import AdvancedAsciiVisualizer
        visualizer = AdvancedAsciiVisualizer()
        return visualizer.visualize(self.parsed_design, width)

    def validate(self) -> List[str]:
        """Validate design, return list of issues (empty if valid).

        Returns:
            List of validation error messages
        """
        return self._validator.validate(self.parsed_design)

    def count_observations(self) -> Union[int, str]:
        """Calculate total observation count.

        Returns:
            Total observation count, or string if approximate
        """
        # Build a graph to determine the hierarchical structure
        graph = self.to_networkx()

        # Find root nodes (no incoming nesting edges)
        nesting_parents = {
            rel.from_factor
            for rel in self.parsed_design.relationships
            if rel.rel_type == "nests"
        }
        nesting_children = {
            rel.to_factor
            for rel in self.parsed_design.relationships
            if rel.rel_type == "nests"
        }
        root_factors = nesting_parents - nesting_children

        if not root_factors:
            # No nesting structure, find factors without incoming edges
            root_factors = {
                factor.name
                for factor in self.parsed_design.factors
                if not any(
                    rel.to_factor == factor.name
                    for rel in self.parsed_design.relationships
                )
            }

        if not root_factors:
            # Single factor or no clear hierarchy
            if self.parsed_design.factors:
                return self._get_factor_size(self.parsed_design.factors[0])
            return 0

        # Calculate total by traversing nesting hierarchy
        total = 1
        has_approximate = False

        def traverse(factor_name: str) -> Union[int, str]:
            nonlocal has_approximate
            factor = self.parsed_design.get_factor(factor_name)
            if not factor:
                return 1

            size = self._get_factor_size(factor)
            if isinstance(size, str):
                has_approximate = True
                return size

            # Find nested children
            children = [
                rel.to_factor
                for rel in self.parsed_design.relationships
                if rel.from_factor == factor_name and rel.rel_type == "nests"
            ]

            child_product = 1
            for child in children:
                child_size = traverse(child)
                if isinstance(child_size, str):
                    has_approximate = True
                else:
                    child_product *= child_size

            return size * child_product

        for root in root_factors:
            result = traverse(root)
            if isinstance(result, str):
                has_approximate = True
            else:
                total *= result

        if has_approximate:
            return f"~{total}"
        return total

    def _get_factor_size(self, factor: Factor) -> Union[int, str]:
        """Get the size of a factor.

        Args:
            factor: The factor object

        Returns:
            Size as int or approximate string
        """
        if isinstance(factor.n, str):
            return factor.n
        elif isinstance(factor.n, list):
            return sum(factor.n)
        else:
            return factor.n

    def describe(self) -> str:
        """Generate human-readable description.

        Returns:
            Human-readable description string
        """
        lines = []
        lines.append("Experimental Design Description")
        lines.append("=" * 40)
        lines.append("")

        # Factors
        lines.append(f"Factors ({len(self.parsed_design.factors)}):")
        for factor in self.parsed_design.factors:
            n_str = self._format_factor_size(factor.n)
            lines.append(f"  - {factor.name} ({n_str}): {factor.type}")

        lines.append("")

        # Relationships by type
        rel_by_type: Dict[RelationType, List[Relationship]] = {}
        for rel in self.parsed_design.relationships:
            if rel.rel_type not in rel_by_type:
                rel_by_type[rel.rel_type] = []
            rel_by_type[rel.rel_type].append(rel)

        lines.append(f"Relationships ({len(self.parsed_design.relationships)}):")
        for rel_type, rels in rel_by_type.items():
            lines.append(f"  {rel_type}:")
            for rel in rels:
                lines.append(f"    - {rel.from_factor} → {rel.to_factor}")

        lines.append("")

        # Total observations
        obs_count = self.count_observations()
        lines.append(f"Total observations: {obs_count}")

        return "\n".join(lines)

    def _format_factor_size(self, n: Union[int, List[int], str]) -> str:
        """Format factor size for display.

        Args:
            n: Factor size

        Returns:
            Formatted string
        """
        if isinstance(n, str):
            return n
        elif isinstance(n, list):
            return f"[{' | '.join(map(str, n))}]"
        else:
            return str(n)
