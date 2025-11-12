"""Tests for validators."""

import pytest
from edviz import ExperimentalDesign
from edviz.validators import DesignValidator
from edviz.data_structures import ParsedDesign, Factor, Relationship


class TestDesignValidator:
    """Tests for design validator."""

    def test_valid_design(self) -> None:
        """Test that valid design passes validation."""
        design = ExperimentalDesign.from_grammar("Site(3) > Patient(20) > Cell(1000)")
        issues = design.validate()

        assert len(issues) == 0

    def test_empty_design(self) -> None:
        """Test that empty design is flagged."""
        design = ExperimentalDesign()
        issues = design.validate()

        assert len(issues) > 0
        assert any("no factors" in issue.lower() for issue in issues)

    def test_unknown_factor_in_relationship(self) -> None:
        """Test that unknown factor reference is detected."""
        parsed = ParsedDesign()
        parsed.factors.append(Factor("Site", 3, "factor"))
        parsed.relationships.append(Relationship("Site", "Unknown", "nests"))

        validator = DesignValidator()
        issues = validator.validate(parsed)

        assert len(issues) > 0
        assert any("unknown factor" in issue.lower() for issue in issues)

    def test_cycle_detection(self) -> None:
        """Test that cycles in nesting are detected."""
        # Create a design with a cycle: A > B > C > A
        parsed = ParsedDesign()
        parsed.factors.append(Factor("A", 1, "factor"))
        parsed.factors.append(Factor("B", 2, "factor"))
        parsed.factors.append(Factor("C", 3, "factor"))
        parsed.relationships.append(Relationship("A", "B", "nests"))
        parsed.relationships.append(Relationship("B", "C", "nests"))
        parsed.relationships.append(Relationship("C", "A", "nests"))

        validator = DesignValidator()
        issues = validator.validate(parsed)

        assert len(issues) > 0
        assert any("cycle" in issue.lower() for issue in issues)

    def test_classification_terminal(self) -> None:
        """Test that classification relationships are terminal."""
        # Create design where classified factor has outgoing relationship
        parsed = ParsedDesign()
        parsed.factors.append(Factor("Cell", 1000, "factor"))
        parsed.factors.append(Factor("CellType", 35, "classification"))
        parsed.factors.append(Factor("Other", 5, "factor"))
        parsed.relationships.append(Relationship("Cell", "CellType", "classifies"))
        parsed.relationships.append(Relationship("Cell", "Other", "nests"))

        validator = DesignValidator()
        issues = validator.validate(parsed)

        assert len(issues) > 0
        assert any("terminal" in issue.lower() for issue in issues)

    def test_duplicate_relationships(self) -> None:
        """Test that duplicate relationships are detected."""
        parsed = ParsedDesign()
        parsed.factors.append(Factor("A", 1, "factor"))
        parsed.factors.append(Factor("B", 2, "factor"))
        parsed.relationships.append(Relationship("A", "B", "nests"))
        parsed.relationships.append(Relationship("A", "B", "nests"))  # Duplicate

        validator = DesignValidator()
        issues = validator.validate(parsed)

        assert len(issues) > 0
        assert any("duplicate" in issue.lower() for issue in issues)

    def test_invalid_factor_size_zero(self) -> None:
        """Test that zero factor sizes raise error on construction."""
        with pytest.raises(ValueError, match="must be positive"):
            Factor("Site", 0, "factor")

    def test_invalid_factor_size_negative(self) -> None:
        """Test that negative factor sizes raise error on construction."""
        with pytest.raises(ValueError, match="must be positive"):
            Factor("Site", -5, "factor")

    def test_empty_unbalanced_list(self) -> None:
        """Test that empty unbalanced list is detected."""
        parsed = ParsedDesign()
        parsed.factors.append(Factor("Site", [], "factor"))

        validator = DesignValidator()
        issues = validator.validate(parsed)

        assert len(issues) > 0
        assert any("empty size list" in issue.lower() for issue in issues)

    def test_invalid_approximate_format(self) -> None:
        """Test that invalid approximate format raises error on construction."""
        # Approximate should start with ~
        with pytest.raises(ValueError, match="must start with '~'"):
            Factor("Cell", "5000", "factor")

    def test_valid_approximate_format(self) -> None:
        """Test that valid approximate format passes validation."""
        design = ExperimentalDesign.from_grammar("Cell(~5000)")
        issues = design.validate()

        # Should not have issues about approximate format
        assert not any("invalid approximate" in issue.lower() for issue in issues)

    def test_valid_unbalanced_factor(self) -> None:
        """Test that valid unbalanced factor passes validation."""
        design = ExperimentalDesign.from_grammar("Patient[30|25|18]")
        issues = design.validate()

        # Should have no issues
        assert len(issues) == 0

    def test_complex_valid_design(self) -> None:
        """Test validation of complex but valid design."""
        grammar = """
        {Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) ◊ Treatment(3) > Cell(~5000) : CellType(42)
        """
        design = ExperimentalDesign.from_grammar(grammar)
        issues = design.validate()

        # Should have no structural issues
        assert len(issues) == 0
