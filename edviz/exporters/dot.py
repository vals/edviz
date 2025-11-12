"""DOT (Graphviz) format exporter."""

from typing import Dict, Set
from edviz.data_structures import ParsedDesign, Factor


class DotExporter:
    """Exporter for Graphviz DOT format."""

    # Symbol mappings for relationship types
    SYMBOLS = {
        "nests": "↓",
        "crosses": "×",
        "partial_crosses": "◊",
        "classifies": ":",
        "batch_effect": "══",
        "confounded": "≈≈",
    }

    # Colors for different factor types
    COLORS = {
        "factor": "#E8F4F8",
        "observation": "#FFF4E6",
        "classification": "#F0E6FF",
        "batch": "#FFE6E6",
    }

    def export(self, design: ParsedDesign) -> str:
        """Export design to DOT format.

        Args:
            design: The parsed design to export

        Returns:
            DOT format string
        """
        lines = []
        lines.append("digraph ExperimentalDesign {")
        lines.append("  rankdir=TB;")
        lines.append('  node [shape=box, style="rounded,filled"];')
        lines.append("")

        # Add factors as nodes
        lines.append("  // Factors")
        for factor in design.factors:
            node_label = self._format_factor_label(factor)
            color = self.COLORS.get(factor.type, "#FFFFFF")
            lines.append(f'  {self._sanitize_name(factor.name)} [label="{node_label}", fillcolor="{color}"];')

        lines.append("")

        # Add relationships as edges
        lines.append("  // Relationships")
        for rel in design.relationships:
            from_node = self._sanitize_name(rel.from_factor)
            to_node = self._sanitize_name(rel.to_factor)
            symbol = self.SYMBOLS.get(rel.rel_type, "")

            # Different edge styles for different relationship types
            if rel.rel_type == "nests":
                lines.append(f'  {from_node} -> {to_node} [label="{symbol}"];')
            elif rel.rel_type in ("crosses", "partial_crosses"):
                lines.append(f'  {from_node} -> {to_node} [label="{symbol}", style=dashed, dir=none];')
            elif rel.rel_type == "classifies":
                lines.append(f'  {from_node} -> {to_node} [label="{symbol}", style=dotted];')
            elif rel.rel_type == "batch_effect":
                lines.append(f'  {from_node} -> {to_node} [label="{symbol}", color=red, style=bold];')
            elif rel.rel_type == "confounded":
                lines.append(f'  {from_node} -> {to_node} [label="{symbol}", color=orange, style=dashed, dir=none];')

        # Add confound groups as subgraphs
        if "confound_groups" in design.metadata:
            lines.append("")
            lines.append("  // Confound groups")
            for i, group in enumerate(design.metadata["confound_groups"]):
                lines.append(f"  subgraph cluster_{i} {{")
                lines.append('    style=dashed;')
                lines.append('    color=orange;')
                lines.append(f'    label="Confounded";')
                for factor_name in group:
                    lines.append(f"    {self._sanitize_name(factor_name)};")
                lines.append("  }")

        lines.append("}")
        return "\n".join(lines)

    def _format_factor_label(self, factor: Factor) -> str:
        """Format factor label for display.

        Args:
            factor: The factor to format

        Returns:
            Formatted label string
        """
        if isinstance(factor.n, str):
            n_str = factor.n
        elif isinstance(factor.n, list):
            n_str = f"[{' | '.join(map(str, factor.n))}]"
        else:
            n_str = str(factor.n)

        return f"{factor.name}({n_str})"

    def _sanitize_name(self, name: str) -> str:
        """Sanitize factor name for DOT format.

        Args:
            name: The factor name

        Returns:
            Sanitized name
        """
        # Replace any non-alphanumeric characters with underscores
        sanitized = "".join(c if c.isalnum() else "_" for c in name)
        return sanitized
