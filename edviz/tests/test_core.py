"""Tests for core ExperimentalDesign class."""

import json
import pytest
from edviz import ExperimentalDesign
from edviz.data_structures import Factor


class TestExperimentalDesign:
    """Tests for ExperimentalDesign class."""

    def test_empty_design(self) -> None:
        """Test creating empty design."""
        design = ExperimentalDesign()
        assert len(design.factors) == 0
        assert len(design.relationships) == 0

    def test_from_grammar_simple(self) -> None:
        """Test creating design from simple grammar."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")

        assert len(design.factors) == 2
        assert len(design.relationships) == 1

    def test_from_grammar_complex(self) -> None:
        """Test creating design from complex grammar."""
        grammar = "Hospital(3) > Patient(20) > Sample(2) × Treatment(3) > Cell(5000) : CellType(35)"
        design = ExperimentalDesign.from_grammar(grammar)

        assert len(design.factors) >= 5
        assert len(design.relationships) >= 3

    def test_add_factor(self) -> None:
        """Test adding factors programmatically."""
        design = ExperimentalDesign()
        design.add_factor("Site", 3)
        design.add_factor("Patient", 20)

        assert len(design.factors) == 2
        assert design.factors[0].name == "Site"
        assert design.factors[1].name == "Patient"

    def test_add_factor_duplicate(self) -> None:
        """Test that adding duplicate factor raises error."""
        design = ExperimentalDesign()
        design.add_factor("Site", 3)

        with pytest.raises(ValueError, match="already exists"):
            design.add_factor("Site", 5)

    def test_add_nesting(self) -> None:
        """Test adding nesting relationship."""
        design = ExperimentalDesign()
        design.add_factor("Site", 3)
        design.add_factor("Patient", 20)
        design.add_nesting("Site", "Patient")

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "nests"

    def test_add_nesting_unknown_factor(self) -> None:
        """Test that nesting with unknown factor raises error."""
        design = ExperimentalDesign()
        design.add_factor("Site", 3)

        with pytest.raises(ValueError, match="does not exist"):
            design.add_nesting("Site", "Unknown")

    def test_add_crossing(self) -> None:
        """Test adding crossing relationship."""
        design = ExperimentalDesign()
        design.add_factor("Treatment", 2)
        design.add_factor("Timepoint", 4)
        design.add_crossing("Treatment", "Timepoint")

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "crosses"

    def test_add_partial_crossing(self) -> None:
        """Test adding partial crossing relationship."""
        design = ExperimentalDesign()
        design.add_factor("Sample", 3)
        design.add_factor("Treatment", 2)
        design.add_crossing("Sample", "Treatment", partial=True)

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "partial_crosses"

    def test_add_classification(self) -> None:
        """Test adding classification relationship."""
        design = ExperimentalDesign()
        design.add_factor("Cell", 5000)
        design.add_factor("CellType", 35)
        design.add_classification("Cell", "CellType")

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "classifies"

        # CellType should be marked as classification
        celltype = design.parsed_design.get_factor("CellType")
        assert celltype is not None
        assert celltype.type == "classification"

    def test_add_batch_effect(self) -> None:
        """Test adding batch effect."""
        design = ExperimentalDesign()
        design.add_factor("ProcessBatch", 4)
        design.add_factor("Sample", 10)
        design.add_batch_effect("ProcessBatch", ["Sample"])

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "batch_effect"

    def test_add_confound(self) -> None:
        """Test adding confound relationship."""
        design = ExperimentalDesign()
        design.add_factor("Center", 3)
        design.add_factor("Protocol", 2)
        design.add_confound("Center", "Protocol")

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "confounded"

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        design = ExperimentalDesign()
        design.add_factor("Site", 3)
        design.add_factor("Patient", 20)
        design.add_nesting("Site", "Patient")

        design_dict = design.to_dict()

        assert "schema_version" in design_dict
        assert "factors" in design_dict
        assert "relationships" in design_dict
        assert len(design_dict["factors"]) == 2
        assert len(design_dict["relationships"]) == 1

    def test_to_json(self) -> None:
        """Test converting to JSON."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        json_str = design.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "factors" in parsed
        assert len(parsed["factors"]) == 2

    def test_from_dict(self) -> None:
        """Test creating from dictionary."""
        design_dict = {
            "factors": [
                {"name": "Site", "n": 3, "type": "factor"},
                {"name": "Patient", "n": 20, "type": "factor"},
            ],
            "relationships": [
                {"from": "Site", "to": "Patient", "type": "nests"}
            ],
            "metadata": {}
        }

        design = ExperimentalDesign.from_dict(design_dict)

        assert len(design.factors) == 2
        assert len(design.relationships) == 1

    def test_round_trip_json(self) -> None:
        """Test round-trip conversion through JSON."""
        grammar = "Site(3) > Patient(20) > Cell(1000)"
        design1 = ExperimentalDesign.from_grammar(grammar)

        json_str = design1.to_json()
        design_dict = json.loads(json_str)
        design2 = ExperimentalDesign.from_dict(design_dict)

        assert len(design1.factors) == len(design2.factors)
        assert len(design1.relationships) == len(design2.relationships)

    def test_to_networkx(self) -> None:
        """Test converting to NetworkX graph."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20) > Cell(1000)")
        graph = design.to_networkx()

        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 2

        # Check node attributes
        assert "n" in graph.nodes["Site"]
        assert graph.nodes["Site"]["n"] == 3

    def test_count_observations_simple(self) -> None:
        """Test counting observations in simple design."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20) > Cell(1000)")
        count = design.count_observations()

        assert count == 3 * 20 * 1000

    def test_count_observations_crossing(self) -> None:
        """Test counting observations with crossing."""
        design = ExperimentalDesign.from_grammar("Patient(10) > Sample(2) × Treatment(3)")
        count = design.count_observations()

        # Should count nested structure
        assert isinstance(count, int)
        assert count > 0

    def test_count_observations_approximate(self) -> None:
        """Test counting observations with approximate count."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20) > Cell(~5000)")
        count = design.count_observations()

        assert isinstance(count, str)
        assert count.startswith("~")

    def test_count_observations_unbalanced(self) -> None:
        """Test counting observations with unbalanced factor."""
        design = ExperimentalDesign.from_grammar("Site[10|20|30] > Patient(5)")
        count = design.count_observations()

        # Sum of unbalanced factor: 10 + 20 + 30 = 60
        # Multiplied by nested factor: 60 * 5 = 300
        assert count == 60 * 5

    def test_validate_valid_design(self) -> None:
        """Test validating a valid design."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20) > Cell(1000)")
        issues = design.validate()

        assert len(issues) == 0

    def test_describe(self) -> None:
        """Test generating description."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        description = design.describe()

        assert "Site" in description
        assert "Patient" in description
        assert "nests" in description

    def test_ascii_diagram(self) -> None:
        """Test generating ASCII diagram."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20) > Cell(1000)")
        diagram = design.ascii_diagram()

        assert "Site" in diagram
        assert "Patient" in diagram
        assert "Cell" in diagram
        assert "↓" in diagram  # Nesting symbol

    def test_to_dot(self) -> None:
        """Test DOT export."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        dot_str = design.to_dot()

        assert "digraph" in dot_str
        assert "Site" in dot_str
        assert "Patient" in dot_str

    def test_to_graphml(self) -> None:
        """Test GraphML export."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20)")
        graphml_str = design.to_graphml()

        assert "graphml" in graphml_str
        assert "Site" in graphml_str
        assert "Patient" in graphml_str
