"""Tests for grammar parser."""

import pytest
from edviz.parser import DesignGrammarParser, Token
from edviz.data_structures import Factor, Relationship


class TestTokenization:
    """Tests for tokenization."""

    def test_simple_factor(self) -> None:
        """Test tokenizing a simple factor."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("Site(3)")

        assert len(tokens) == 4
        assert tokens[0].type == "IDENTIFIER"
        assert tokens[0].value == "Site"
        assert tokens[1].type == "LPAREN"
        assert tokens[2].type == "NUMBER"
        assert tokens[2].value == "3"
        assert tokens[3].type == "RPAREN"

    def test_nesting_operator(self) -> None:
        """Test tokenizing nesting operator."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("A(1) > B(2)")

        assert any(t.type == "NESTS" for t in tokens)

    def test_crossing_operators(self) -> None:
        """Test tokenizing crossing operators."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("A(1) × B(2) ◊ C(3)")

        assert any(t.type == "CROSS" for t in tokens)
        assert any(t.type == "PARTIAL_CROSS" for t in tokens)

    def test_comments(self) -> None:
        """Test that comments are ignored."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("# This is a comment\nA(1)")

        # Comments should be filtered out
        assert all(t.type != "COMMENT" for t in tokens)

    def test_approximate_count(self) -> None:
        """Test tokenizing approximate count."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("Cell(~5000)")

        assert any(t.type == "TILDE" for t in tokens)

    def test_unbalanced_factor(self) -> None:
        """Test tokenizing unbalanced factor."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("Patient[30|25|18]")

        assert any(t.type == "LBRACKET" for t in tokens)
        assert any(t.type == "PIPE" for t in tokens)
        assert any(t.type == "RBRACKET" for t in tokens)

    def test_k_suffix(self) -> None:
        """Test tokenizing 'k' suffix for thousands."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("Cell(5k)")

        number_tokens = [t for t in tokens if t.type == "NUMBER"]
        assert len(number_tokens) == 1
        assert number_tokens[0].value == "5k"


class TestParsing:
    """Tests for parsing."""

    def test_simple_nesting(self) -> None:
        """Test parsing simple nesting."""
        parser = DesignGrammarParser()
        design = parser.parse("Site(3) > Patient(20)")

        assert len(design.factors) == 2
        assert design.factors[0].name == "Site"
        assert design.factors[0].n == 3
        assert design.factors[1].name == "Patient"
        assert design.factors[1].n == 20

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "nests"

    def test_multiple_nesting(self) -> None:
        """Test parsing multiple levels of nesting."""
        parser = DesignGrammarParser()
        design = parser.parse("Site(3) > Patient(20) > Cell(1000)")

        assert len(design.factors) == 3
        assert len(design.relationships) == 2
        assert all(r.rel_type == "nests" for r in design.relationships)

    def test_crossing(self) -> None:
        """Test parsing crossing."""
        parser = DesignGrammarParser()
        design = parser.parse("Treatment(2) × Timepoint(4)")

        assert len(design.factors) == 2
        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "crosses"

    def test_partial_crossing(self) -> None:
        """Test parsing partial crossing."""
        parser = DesignGrammarParser()
        design = parser.parse("Sample(3) ◊ Treatment(2)")

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "partial_crosses"

    def test_classification(self) -> None:
        """Test parsing classification."""
        parser = DesignGrammarParser()
        design = parser.parse("Cell(5000) : CellType(35)")

        assert len(design.factors) == 2
        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "classifies"

        # Check that CellType is marked as classification
        celltype = design.get_factor("CellType")
        assert celltype is not None
        assert celltype.type == "classification"

    def test_batch_effect(self) -> None:
        """Test parsing batch effect."""
        parser = DesignGrammarParser()
        design = parser.parse("ProcessBatch(4) == Sample(10)")

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "batch_effect"

    def test_confounding(self) -> None:
        """Test parsing confounding."""
        parser = DesignGrammarParser()
        design = parser.parse("Center(3) ≈≈ Protocol(2)")

        assert len(design.relationships) == 1
        assert design.relationships[0].rel_type == "confounded"

    def test_confound_group(self) -> None:
        """Test parsing confound group."""
        parser = DesignGrammarParser()
        design = parser.parse("{Center(3) ≈≈ Protocol(2)}")

        assert len(design.factors) == 2
        assert "confound_groups" in design.metadata
        assert len(design.metadata["confound_groups"]) == 1
        assert set(design.metadata["confound_groups"][0]) == {"Center", "Protocol"}

    def test_approximate_count(self) -> None:
        """Test parsing approximate count."""
        parser = DesignGrammarParser()
        design = parser.parse("Cell(~5000)")

        assert len(design.factors) == 1
        assert design.factors[0].n == "~5000"

    def test_unbalanced_factor(self) -> None:
        """Test parsing unbalanced factor."""
        parser = DesignGrammarParser()
        design = parser.parse("Patient[30|25|18]")

        assert len(design.factors) == 1
        assert design.factors[0].n == [30, 25, 18]

    def test_k_suffix_parsing(self) -> None:
        """Test parsing 'k' suffix."""
        parser = DesignGrammarParser()
        design = parser.parse("Cell(5k)")

        assert len(design.factors) == 1
        assert design.factors[0].n == 5000

    def test_complex_design(self) -> None:
        """Test parsing complex design."""
        grammar = """
        # Complex design
        {Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) ◊ Treatment(3) > Cell(~5000) : CellType(42)
        """
        parser = DesignGrammarParser()
        design = parser.parse(grammar)

        # Should have multiple factors
        assert len(design.factors) >= 5

        # Should have confound group
        assert "confound_groups" in design.metadata

        # Should have various relationship types
        rel_types = {r.rel_type for r in design.relationships}
        assert "confounded" in rel_types
        assert "nests" in rel_types
        assert "partial_crosses" in rel_types
        assert "classifies" in rel_types

    def test_parentheses(self) -> None:
        """Test parsing with parentheses for grouping."""
        parser = DesignGrammarParser()
        design = parser.parse("(A(1) × B(2)) > C(3)")

        assert len(design.factors) == 3
        # A and B should be crossed
        crossing_rels = [r for r in design.relationships if r.rel_type == "crosses"]
        assert len(crossing_rels) == 1

    def test_invalid_grammar(self) -> None:
        """Test that invalid grammar raises error."""
        parser = DesignGrammarParser()

        with pytest.raises(ValueError):
            parser.parse("Site(3) > ")

        with pytest.raises(ValueError):
            parser.parse("Site")  # Missing size specification


class TestValidation:
    """Tests for syntax validation."""

    def test_matching_braces(self) -> None:
        """Test validation of matching braces."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("{A(1) ≈≈ B(2)}")
        assert parser.validate_syntax(tokens)

    def test_unmatched_braces(self) -> None:
        """Test detection of unmatched braces."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("{A(1)")
        # Should have LBRACE but missing RBRACE
        assert not parser.validate_syntax(tokens)

    def test_matching_parentheses(self) -> None:
        """Test validation of matching parentheses."""
        parser = DesignGrammarParser()
        tokens = parser.tokenize("(A(1) > B(2))")
        assert parser.validate_syntax(tokens)
