"""Advanced ASCII diagram visualizer with rich visual connections."""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
import networkx as nx

from edviz.data_structures import ParsedDesign, Factor, Relationship
from edviz.visualizers.canvas import Canvas, LineStyle, Layer


@dataclass
class LayoutNode:
    """Node in the layout with position information."""
    factor: Factor
    x: int  # column position
    y: int  # row position
    width: int = 0  # width of the factor text
    is_branch: bool = False  # True if this is a branched factor
    parent: Optional[str] = None  # parent factor name


@dataclass
class BatchFlowLine:
    """Represents a batch effect flow line."""
    batch_factor: str
    affected_factor: str
    start_y: int
    end_y: int
    x: int  # column where the line runs


class AdvancedAsciiVisualizer:
    """Advanced ASCII visualizer with rich visual connections."""

    # Symbols
    SYMBOLS = {
        "nests": "↓",
        "crosses": "×",
        "partial_crosses": "◊",
        "classifies": ":",
        "confounded": "≈",
    }

    def __init__(self):
        self.canvas: Optional[Canvas] = None
        self.layout: Dict[str, LayoutNode] = {}
        self.batch_lines: List[BatchFlowLine] = []

    def visualize(self, design: ParsedDesign, width: int = 60) -> str:
        """Generate advanced ASCII diagram.

        Args:
            design: The parsed design to visualize
            width: Desired width of diagram

        Returns:
            ASCII diagram string
        """
        if not design.factors:
            return "Empty design"

        # Phase 1: Analyze structure
        self._analyze_structure(design)

        # Phase 2: Compute layout
        self._compute_layout(design, width)

        # Phase 3: Calculate canvas size
        canvas_height = self._calculate_canvas_height()
        self.canvas = Canvas(width, canvas_height)

        # Phase 4: Draw outer box
        self.canvas.draw_box(0, 0, width, canvas_height, LineStyle.SINGLE, "Design Structure")

        # Phase 5: Draw batch effect flow lines
        self._draw_batch_flows(design)

        # Phase 6: Draw main hierarchy
        self._draw_hierarchy(design)

        # Phase 7: Draw confounding
        self._draw_confounding(design)

        # Phase 8: Draw annotations
        self._draw_annotations(design)

        return self.canvas.render()

    def _analyze_structure(self, design: ParsedDesign) -> None:
        """Analyze design structure to understand relationships."""
        # Build graphs for different relationship types
        self.nesting_graph = nx.DiGraph()
        self.crossing_graph = nx.Graph()  # undirected
        self.batch_effects: Dict[str, List[str]] = {}
        self.confound_groups: List[Set[str]] = []

        # Add all factors as nodes
        for factor in design.factors:
            if factor.type != "batch":
                self.nesting_graph.add_node(factor.name)

        # Categorize relationships
        for rel in design.relationships:
            if rel.rel_type == "nests":
                if rel.from_factor in self.nesting_graph and rel.to_factor in self.nesting_graph:
                    self.nesting_graph.add_edge(rel.from_factor, rel.to_factor)
            elif rel.rel_type in ("crosses", "partial_crosses"):
                self.crossing_graph.add_edge(rel.from_factor, rel.to_factor, type=rel.rel_type)
            elif rel.rel_type == "batch_effect":
                if rel.from_factor not in self.batch_effects:
                    self.batch_effects[rel.from_factor] = []
                self.batch_effects[rel.from_factor].append(rel.to_factor)

        # Extract confound groups from metadata
        if "confound_groups" in design.metadata:
            for group in design.metadata["confound_groups"]:
                self.confound_groups.append(set(group))

    def _compute_layout(self, design: ParsedDesign, width: int) -> None:
        """Compute spatial layout for all factors.

        This determines the (x, y) position for each factor in the diagram.
        """
        self.layout = {}
        current_y = 2  # Start below top border

        # Track which factors are already placed
        placed = set()

        # Find root nodes (no incoming nesting edges)
        roots = [
            node for node in self.nesting_graph.nodes()
            if self.nesting_graph.in_degree(node) == 0
        ]

        # Handle batch factors first (they go at the top)
        batch_factors = [f for f in design.factors if f.type == "batch"]
        for batch_factor in batch_factors:
            factor_text = self._format_factor(batch_factor)
            node = LayoutNode(
                factor=batch_factor,
                x=2,
                y=current_y,
                width=len(factor_text)
            )
            self.layout[batch_factor.name] = node
            placed.add(batch_factor.name)
            current_y += 1

            # Add gap for flow line start
            if batch_factor.name in self.batch_effects:
                current_y += 1

        # Add spacing if we had batch factors
        if batch_factors:
            current_y += 1

        # Identify factors that should not appear in main hierarchy
        # (crossed factors that are just crossing targets)
        crossed_only = set()
        for node in self.crossing_graph.nodes():
            # Check if this factor only appears as a crossing target
            # and has no nesting role at this level
            if node not in roots and self.nesting_graph.in_degree(node) == 0:
                # This factor is crossed but not nested from above
                crossed_only.add(node)

        # Handle confounded groups - they should be side-by-side at the same level
        confounded_factors = set()
        for group in self.confound_groups:
            confounded_factors.update(group)
            # Layout confounded factors horizontally
            if len(group) >= 2:
                group_list = sorted(list(group))
                x = 2
                for factor_name in group_list:
                    if factor_name in placed:
                        continue
                    factor = design.get_factor(factor_name)
                    if factor:
                        factor_text = self._format_factor(factor)
                        node = LayoutNode(
                            factor=factor,
                            x=x,
                            y=current_y,
                            width=len(factor_text)
                        )
                        self.layout[factor_name] = node
                        placed.add(factor_name)
                        x += len(factor_text) + 8  # More space for confounding symbol
                current_y += 2  # Move down after confounded group

                # Find common children of confounded factors and place them
                common_children = None
                for factor_name in group_list:
                    children = set(self.nesting_graph.successors(factor_name))
                    if common_children is None:
                        common_children = children
                    else:
                        common_children = common_children & children

                # Layout common children
                if common_children:
                    for child in common_children:
                        if child not in placed:
                            current_y = self._layout_subtree(design, child, 2, current_y, width, placed, crossed_only)
                            current_y += 1  # Gap after each child

        # Filter out confounded factors from roots since they're already placed
        roots = [r for r in roots if r not in confounded_factors or r not in placed]

        # Layout the main hierarchy
        for root in roots:
            if root not in placed:
                current_y = self._layout_subtree(design, root, 2, current_y, width, placed, crossed_only)

        # Handle orphaned factors (not in nesting hierarchy and not crossed-only)
        orphans = set(f.name for f in design.factors if f.type != "batch")
        orphans -= placed
        orphans -= crossed_only

        for orphan in orphans:
            factor = design.get_factor(orphan)
            if factor:
                factor_text = self._format_factor(factor)
                node = LayoutNode(
                    factor=factor,
                    x=2,
                    y=current_y,
                    width=len(factor_text)
                )
                self.layout[orphan] = node
                placed.add(orphan)
                current_y += 2

    def _layout_subtree(
        self,
        design: ParsedDesign,
        factor_name: str,
        x: int,
        y: int,
        max_width: int,
        placed: Set[str],
        crossed_only: Set[str]
    ) -> int:
        """Layout a subtree recursively.

        Args:
            design: The design
            factor_name: Current factor
            x: X position
            y: Y position
            max_width: Maximum width available
            placed: Set of already placed factors
            crossed_only: Set of factors that should only appear as crossing targets

        Returns:
            Next available Y position
        """
        factor = design.get_factor(factor_name)
        if not factor or factor_name in placed or factor_name in crossed_only:
            return y

        factor_text = self._format_factor(factor)

        # Check if this factor has crossings
        crossings = [
            (n, self.crossing_graph[factor_name][n]['type'])
            for n in self.crossing_graph.neighbors(factor_name)
            if n in self.crossing_graph
        ] if factor_name in self.crossing_graph else []

        # Check if this factor is classified
        classifications = [
            rel.to_factor
            for rel in design.relationships
            if rel.from_factor == factor_name and rel.rel_type == "classifies"
        ]

        # Create layout node
        node = LayoutNode(
            factor=factor,
            x=x,
            y=y,
            width=len(factor_text)
        )
        self.layout[factor_name] = node
        placed.add(factor_name)
        current_y = y + 1

        # Handle crossings (they appear on the same line, to the right)
        if crossings:
            current_y += 1  # Space for crossing arrows

        # Add space for nesting arrow
        current_y += 1

        # Handle classifications
        if classifications:
            current_y += 1  # Classification symbol
            for classified_name in classifications:
                classified_factor = design.get_factor(classified_name)
                if classified_factor and classified_name not in placed:
                    classified_text = self._format_factor(classified_factor)
                    classified_node = LayoutNode(
                        factor=classified_factor,
                        x=x,
                        y=current_y,
                        width=len(classified_text)
                    )
                    self.layout[classified_name] = classified_node
                    placed.add(classified_name)
                    current_y += 1
            current_y += 1  # Gap after classifications

        # Layout children (nested factors)
        children = list(self.nesting_graph.successors(factor_name))

        # Check if children should be branched (multiple children)
        if len(children) > 1:
            # Branch layout - put children side by side
            child_x = x
            max_child_y = current_y
            for child in children:
                child_y = self._layout_subtree(design, child, child_x, current_y, max_width, placed, crossed_only)
                max_child_y = max(max_child_y, child_y)
                # Mark as branch
                if child in self.layout:
                    self.layout[child].is_branch = True
                    self.layout[child].parent = factor_name
                child_x += 15  # Space between branches
            current_y = max_child_y
        else:
            # Single child - normal vertical layout
            for child in children:
                current_y = self._layout_subtree(design, child, x, current_y, max_width, placed, crossed_only)

        return current_y

    def _calculate_canvas_height(self) -> int:
        """Calculate required canvas height."""
        if not self.layout:
            return 10

        max_y = max(node.y for node in self.layout.values())
        # Add space for bottom border and annotations
        return max_y + 8

    def _draw_batch_flows(self, design: ParsedDesign) -> None:
        """Draw batch effect flow lines."""
        if not self.batch_effects or not self.canvas:
            return

        # Calculate the x position for the flow column (rightmost area)
        flow_x = self.canvas.width - 5

        # Collect all corners to draw them last (so they overwrite vertical lines)
        corners = []

        # Track which affected factors we've already connected
        # (to avoid duplicates when factors appear multiple times)
        connected_factors = set()

        for batch_name, affected in self.batch_effects.items():
            if batch_name not in self.layout:
                continue

            batch_node = self.layout[batch_name]

            # Draw horizontal line from batch factor to flow column
            start_x = batch_node.x + batch_node.width
            self.canvas.draw_hline(
                start_x,
                flow_x - 1,
                batch_node.y,
                LineStyle.DOUBLE,
                Layer.LINES
            )
            corners.append((flow_x, batch_node.y, "tr"))

            for affected_name in affected:
                # Only connect to first occurrence of each affected factor
                if affected_name in connected_factors:
                    continue

                if affected_name not in self.layout:
                    continue

                connected_factors.add(affected_name)
                affected_node = self.layout[affected_name]

                # Draw vertical line down to affected factor row
                self.canvas.draw_vline(
                    flow_x,
                    batch_node.y + 1,
                    affected_node.y - 1,
                    LineStyle.DOUBLE,
                    Layer.LINES
                )

                # Draw horizontal line from affected factor to corner
                # Start from a bit to the right to avoid crossing symbols
                end_x = affected_node.x + affected_node.width + 1
                self.canvas.draw_hline(
                    end_x,
                    flow_x - 1,
                    affected_node.y,
                    LineStyle.DOUBLE,
                    Layer.LINES
                )

                # Save corner to draw later
                corners.append((flow_x, affected_node.y, "br"))

        # Draw all corners last so they overwrite vertical lines
        for x, y, corner_type in corners:
            self.canvas.draw_corner(
                x,
                y,
                corner_type,
                LineStyle.DOUBLE,
                Layer.ANNOTATIONS  # Use higher layer to ensure they're on top
            )

    def _draw_hierarchy(self, design: ParsedDesign) -> None:
        """Draw the main hierarchical structure."""
        if not self.canvas:
            return

        # Check which factors are in confound groups
        confounded_factor_names = set()
        for group in self.confound_groups:
            confounded_factor_names.update(group)

        # Draw factors in layout order
        for factor_name, node in self.layout.items():
            if node.factor.type == "batch":
                # Batch factors already handled
                factor_text = self._format_factor(node.factor)
                self.canvas.write_text(node.x, node.y, factor_text, Layer.TEXT)
                continue

            # Draw the factor
            factor_text = self._format_factor(node.factor)
            self.canvas.write_text(node.x, node.y, factor_text, Layer.TEXT)

            # Check for crossings
            crossings = [
                (n, self.crossing_graph[factor_name][n]['type'])
                for n in self.crossing_graph.neighbors(factor_name)
                if n in self.crossing_graph and n in self.layout
            ] if factor_name in self.crossing_graph else []

            # Draw crossings on the same line
            if crossings:
                cross_x = node.x + node.width + 1
                for i, (crossed_name, cross_type) in enumerate(crossings):
                    crossed_node = self.layout[crossed_name]
                    crossed_text = self._format_factor(crossed_node.factor)

                    # Draw crossing line
                    symbol = self.SYMBOLS["crosses"] if cross_type == "crosses" else self.SYMBOLS["partial_crosses"]

                    if i == 0:
                        # First crossing - draw on same line as factor
                        self.canvas.write_text(cross_x, node.y, " ────", Layer.LINES)
                        self.canvas.write_text(cross_x + 5, node.y, symbol, Layer.TEXT)
                        self.canvas.write_text(cross_x + 6, node.y, "──── ", Layer.LINES)
                        self.canvas.write_text(cross_x + 11, node.y, crossed_text, Layer.TEXT)
                    else:
                        # Additional crossings - draw below
                        cross_y = node.y + i
                        self.canvas.write_text(cross_x + 5, cross_y, symbol, Layer.TEXT)
                        self.canvas.write_text(cross_x + 11, cross_y, crossed_text, Layer.TEXT)

            # Check for classifications
            classifications = [
                rel.to_factor
                for rel in design.relationships
                if rel.from_factor == factor_name and rel.rel_type == "classifies"
            ]

            if classifications:
                # Draw classification symbol
                symbol_y = node.y + 1
                self.canvas.write_text(node.x + 3, symbol_y, self.SYMBOLS["classifies"], Layer.TEXT)

                # Classifications are already in layout, just draw them
                # (they were positioned in _layout_subtree)
            else:
                # Draw nesting arrow if has children
                children = list(self.nesting_graph.successors(factor_name))
                if children:
                    arrow_y = node.y + 1

                    # Check if children are branches
                    if len(children) > 1:
                        # Multiple arrows for branches
                        for i, child in enumerate(children):
                            if child in self.layout:
                                child_node = self.layout[child]
                                # Draw arrow pointing to child's x position
                                self.canvas.write_text(
                                    child_node.x + 1,
                                    arrow_y,
                                    self.SYMBOLS["nests"],
                                    Layer.TEXT
                                )
                    else:
                        # Single arrow
                        self.canvas.write_text(node.x + 3, arrow_y, self.SYMBOLS["nests"], Layer.TEXT)

    def _draw_confounding(self, design: ParsedDesign) -> None:
        """Draw confounding as visual connections."""
        if not self.canvas or not self.confound_groups:
            return

        for group in self.confound_groups:
            group_list = sorted(list(group))
            if len(group_list) < 2:
                continue

            # Find nodes in layout
            nodes = [(name, self.layout[name]) for name in group_list if name in self.layout]
            if len(nodes) < 2:
                continue

            # Draw confounding line between factors
            # They should be on the same row since we laid them out that way
            node1_name, node1 = nodes[0]
            node2_name, node2 = nodes[1]

            if node1.y == node2.y:
                # Same row - draw horizontal connection
                start_x = node1.x + node1.width + 1
                end_x = node2.x - 1

                # Draw confounding symbols
                confound_str = " " + (self.SYMBOLS["confounded"] * 4) + " "
                self.canvas.write_text(start_x, node1.y, confound_str, Layer.TEXT)
            else:
                # Different rows - draw vertical with corners
                # This shouldn't happen with new layout, but handle it anyway
                line_x = (node1.x + node2.x) // 2
                confound_char = self.SYMBOLS["confounded"]

                # Draw vertical line
                for y in range(min(node1.y, node2.y) + 1, max(node1.y, node2.y)):
                    self.canvas.set(line_x, y, confound_char, Layer.TEXT)

    def _draw_annotations(self, design: ParsedDesign) -> None:
        """Draw annotations and notes."""
        if not self.canvas:
            return

        # Find bottom of diagram
        if not self.layout:
            return

        max_y = max(node.y for node in self.layout.values())
        annotation_y = max_y + 2

        # Add confound notes at bottom if any
        if self.confound_groups:
            for group in self.confound_groups:
                group_str = f"  Confounded: {' ≈≈ '.join(sorted(group))}"
                self.canvas.write_text(2, annotation_y, group_str, Layer.TEXT)
                annotation_y += 1

        # Add batch effect notes
        if self.batch_effects:
            if self.confound_groups:
                annotation_y += 1  # Gap

            for batch_name, affected in self.batch_effects.items():
                affected_str = ", ".join(affected)
                batch_str = f"  Batch: {batch_name} ══ {affected_str}"
                self.canvas.write_text(2, annotation_y, batch_str, Layer.TEXT)
                annotation_y += 1

    def _format_factor(self, factor: Factor) -> str:
        """Format factor for display."""
        if isinstance(factor.n, str):
            n_str = factor.n
            # Shorten approximate k notation
            if n_str.startswith("~") and len(n_str) > 5:
                if "000" in n_str:
                    n_str = "~" + n_str[1:].replace("000", "k")
        elif isinstance(factor.n, list):
            n_str = f"[{' | '.join(map(str, factor.n))}]"
        else:
            # Shorten thousands
            if factor.n >= 1000 and factor.n % 1000 == 0:
                n_str = f"{factor.n // 1000}k"
            else:
                n_str = str(factor.n)

        return f"{factor.name}({n_str})"
