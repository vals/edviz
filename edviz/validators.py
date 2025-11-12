"""Validation logic for experimental designs."""

from typing import List, Set, Dict
import networkx as nx

from edviz.data_structures import ParsedDesign, Relationship


class DesignValidator:
    """Validator for experimental designs."""

    def validate(self, design: ParsedDesign) -> List[str]:
        """Validate design, return list of issues (empty if valid).

        Args:
            design: The parsed design to validate

        Returns:
            List of validation error messages
        """
        issues: List[str] = []

        # Check for empty design
        if not design.factors:
            issues.append("Design has no factors")
            return issues

        # Validate factor references
        factor_names = {f.name for f in design.factors}
        for rel in design.relationships:
            if rel.from_factor not in factor_names:
                issues.append(f"Relationship references unknown factor: {rel.from_factor}")
            if rel.to_factor not in factor_names:
                issues.append(f"Relationship references unknown factor: {rel.to_factor}")

        # Validate no cycles in nesting relationships
        cycle_issues = self._check_cycles(design)
        issues.extend(cycle_issues)

        # Validate classification is terminal
        classification_issues = self._check_classification_terminal(design)
        issues.extend(classification_issues)

        # Validate no duplicate relationships
        duplicate_issues = self._check_duplicate_relationships(design)
        issues.extend(duplicate_issues)

        # Validate factor sizes
        size_issues = self._check_factor_sizes(design)
        issues.extend(size_issues)

        return issues

    def _check_cycles(self, design: ParsedDesign) -> List[str]:
        """Check for cycles in nesting relationships.

        Args:
            design: The parsed design

        Returns:
            List of cycle-related error messages
        """
        issues = []

        # Build directed graph of nesting relationships
        graph = nx.DiGraph()
        for factor in design.factors:
            graph.add_node(factor.name)

        for rel in design.relationships:
            if rel.rel_type == "nests":
                graph.add_edge(rel.from_factor, rel.to_factor)

        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                for cycle in cycles:
                    cycle_str = " > ".join(cycle + [cycle[0]])
                    issues.append(f"Cycle detected in nesting: {cycle_str}")
        except Exception:
            pass

        return issues

    def _check_classification_terminal(self, design: ParsedDesign) -> List[str]:
        """Check that classification relationships are terminal.

        Classification relationships should not have other relationships after them.

        Args:
            design: The parsed design

        Returns:
            List of classification-related error messages
        """
        issues = []

        # Find all factors that are classified
        classified_factors = {
            rel.from_factor
            for rel in design.relationships
            if rel.rel_type == "classifies"
        }

        # Check if classified factors have outgoing relationships
        for rel in design.relationships:
            if rel.from_factor in classified_factors and rel.rel_type != "classifies":
                issues.append(
                    f"Factor {rel.from_factor} has classification and should be terminal, "
                    f"but also has {rel.rel_type} relationship"
                )

        return issues

    def _check_duplicate_relationships(self, design: ParsedDesign) -> List[str]:
        """Check for duplicate relationships.

        Args:
            design: The parsed design

        Returns:
            List of duplicate relationship error messages
        """
        issues = []

        seen: Set[tuple] = set()
        for rel in design.relationships:
            key = (rel.from_factor, rel.to_factor, rel.rel_type)
            if key in seen:
                issues.append(
                    f"Duplicate relationship: {rel.from_factor} {rel.rel_type} {rel.to_factor}"
                )
            seen.add(key)

        return issues

    def _check_factor_sizes(self, design: ParsedDesign) -> List[str]:
        """Check that factor sizes are valid.

        Args:
            design: The parsed design

        Returns:
            List of factor size error messages
        """
        issues = []

        for factor in design.factors:
            if isinstance(factor.n, list):
                if len(factor.n) == 0:
                    issues.append(f"Factor {factor.name} has empty size list")
                elif any(n <= 0 for n in factor.n):
                    issues.append(f"Factor {factor.name} has non-positive size in list")
            elif isinstance(factor.n, int):
                if factor.n <= 0:
                    issues.append(f"Factor {factor.name} has non-positive size: {factor.n}")
            elif isinstance(factor.n, str):
                if not factor.n.startswith("~"):
                    issues.append(f"Factor {factor.name} has invalid approximate size: {factor.n}")

        return issues
