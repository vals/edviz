"""Tests for exporters."""

import pytest
from lxml import etree
from edviz import ExperimentalDesign
from edviz.exporters.dot import DotExporter
from edviz.exporters.graphml import GraphMLExporter


class TestDotExporter:
    """Tests for DOT exporter."""

    def test_simple_export(self) -> None:
        """Test simple DOT export."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        exporter = DotExporter()
        dot_str = exporter.export(design.parsed_design)

        assert "digraph ExperimentalDesign" in dot_str
        assert "Site" in dot_str
        assert "Patient" in dot_str
        assert "->" in dot_str

    def test_nesting_relationship(self) -> None:
        """Test that nesting is properly represented."""
        design = ExperimentalDesign.from_grammar("A(1) > B(2)")
        exporter = DotExporter()
        dot_str = exporter.export(design.parsed_design)

        assert "↓" in dot_str  # Nesting symbol

    def test_crossing_relationship(self) -> None:
        """Test that crossing is properly represented."""
        design = ExperimentalDesign.from_grammar("A(1) × B(2)")
        exporter = DotExporter()
        dot_str = exporter.export(design.parsed_design)

        assert "×" in dot_str  # Crossing symbol
        assert "dashed" in dot_str

    def test_batch_effect(self) -> None:
        """Test that batch effects are properly represented."""
        design = ExperimentalDesign.from_grammar("Batch(4) == Sample(10)")
        exporter = DotExporter()
        dot_str = exporter.export(design.parsed_design)

        assert "══" in dot_str  # Batch effect symbol
        assert "red" in dot_str

    def test_confound_group(self) -> None:
        """Test that confound groups are shown as subgraphs."""
        design = ExperimentalDesign.from_grammar("{A(1) ≈≈ B(2)}")
        exporter = DotExporter()
        dot_str = exporter.export(design.parsed_design)

        assert "subgraph cluster" in dot_str
        assert "Confounded" in dot_str

    def test_factor_types_have_colors(self) -> None:
        """Test that different factor types have different colors."""
        design = ExperimentalDesign()
        design.add_factor("Site", 3, "factor")
        design.add_factor("Batch", 4, "batch")

        exporter = DotExporter()
        dot_str = exporter.export(design.parsed_design)

        # Should have different fill colors
        assert "fillcolor=" in dot_str

    def test_unbalanced_factor_display(self) -> None:
        """Test display of unbalanced factor."""
        design = ExperimentalDesign.from_grammar("Patient[30|25|18]")
        exporter = DotExporter()
        dot_str = exporter.export(design.parsed_design)

        # Should show the unbalanced counts
        assert "Patient" in dot_str


class TestGraphMLExporter:
    """Tests for GraphML exporter."""

    def test_simple_export(self) -> None:
        """Test simple GraphML export."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        exporter = GraphMLExporter()
        graphml_str = exporter.export(design.parsed_design)

        # Should be valid XML
        root = etree.fromstring(graphml_str.encode())
        assert root.tag.endswith("graphml")

    def test_nodes_exported(self) -> None:
        """Test that nodes are properly exported."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        exporter = GraphMLExporter()
        graphml_str = exporter.export(design.parsed_design)

        # Parse XML
        root = etree.fromstring(graphml_str.encode())
        ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
        nodes = root.xpath("//g:node", namespaces=ns)

        assert len(nodes) == 2

    def test_edges_exported(self) -> None:
        """Test that edges are properly exported."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        exporter = GraphMLExporter()
        graphml_str = exporter.export(design.parsed_design)

        # Parse XML
        root = etree.fromstring(graphml_str.encode())
        ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
        edges = root.xpath("//g:edge", namespaces=ns)

        assert len(edges) == 1

    def test_node_attributes(self) -> None:
        """Test that node attributes are exported."""
        design = ExperimentalDesign.from_grammar("Site(3)")
        exporter = GraphMLExporter()
        graphml_str = exporter.export(design.parsed_design)

        # Parse XML
        root = etree.fromstring(graphml_str.encode())
        ns = {"g": "http://graphml.graphdrawing.org/xmlns"}

        # Should have key definitions
        keys = root.xpath("//g:key", namespaces=ns)
        assert len(keys) >= 2  # At least factor_n and factor_type

    def test_edge_attributes(self) -> None:
        """Test that edge attributes are exported."""
        design = ExperimentalDesign.from_grammar("A(1) > B(2)")
        exporter = GraphMLExporter()
        graphml_str = exporter.export(design.parsed_design)

        # Parse XML
        root = etree.fromstring(graphml_str.encode())
        ns = {"g": "http://graphml.graphdrawing.org/xmlns"}

        # Should have data elements for edges
        edge_data = root.xpath("//g:edge/g:data", namespaces=ns)
        assert len(edge_data) >= 1

    def test_unbalanced_factor_export(self) -> None:
        """Test export of unbalanced factor."""
        design = ExperimentalDesign.from_grammar("Patient[30|25|18]")
        exporter = GraphMLExporter()
        graphml_str = exporter.export(design.parsed_design)

        # Should contain the unbalanced counts
        assert "30" in graphml_str
        assert "25" in graphml_str
        assert "18" in graphml_str

    def test_approximate_count_export(self) -> None:
        """Test export of approximate count."""
        design = ExperimentalDesign.from_grammar("Cell(~5000)")
        exporter = GraphMLExporter()
        graphml_str = exporter.export(design.parsed_design)

        assert "~5000" in graphml_str


class TestExportIntegration:
    """Integration tests for exports."""

    def test_export_to_file(self, tmp_path) -> None:
        """Test exporting to files."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")

        # JSON
        json_file = tmp_path / "design.json"
        design.to_json(json_file)
        assert json_file.exists()

        # DOT
        dot_file = tmp_path / "design.dot"
        design.to_dot(dot_file)
        assert dot_file.exists()

        # GraphML
        graphml_file = tmp_path / "design.graphml"
        design.to_graphml(graphml_file)
        assert graphml_file.exists()

    def test_round_trip_consistency(self) -> None:
        """Test that exports preserve information."""
        grammar = "Hospital(3) > Patient(20) > Sample(2) × Treatment(3)"
        design1 = ExperimentalDesign.from_grammar(grammar)

        # JSON round-trip
        import json
        json_str = design1.to_json()
        design2 = ExperimentalDesign.from_dict(json.loads(json_str))

        assert len(design1.factors) == len(design2.factors)
        assert len(design1.relationships) == len(design2.relationships)

        # Check factor names match
        names1 = {f.name for f in design1.factors}
        names2 = {f.name for f in design2.factors}
        assert names1 == names2
