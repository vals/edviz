"""Biological experimental design examples."""

from edviz import ExperimentalDesign


def simple_hierarchical() -> ExperimentalDesign:
    """Create a simple hierarchical design.

    Design: Site(3) > Patient(20) > Sample(2) > Cell(5000) : CellType(35)

    This represents:
    - 3 sites
    - 20 patients per site
    - 2 samples per patient
    - 5000 cells per sample
    - Cells classified into 35 cell types

    Returns:
        ExperimentalDesign object
    """
    grammar = "Site(3) > Patient(20) > Sample(2) > Cell(5000) : CellType(35)"
    return ExperimentalDesign.from_grammar(grammar)


def crossed_design() -> ExperimentalDesign:
    """Create a crossed factorial design.

    Design: Hospital(4) > Patient(15) × Treatment(2) > Sample(3) × Timepoint(4) > Cell(~8000)

    This represents:
    - 4 hospitals
    - 15 patients per hospital, crossed with 2 treatments
    - 3 samples per patient/treatment combo, crossed with 4 timepoints
    - ~8000 cells per sample

    Returns:
        ExperimentalDesign object
    """
    grammar = "Hospital(4) > Patient(15) × Treatment(2) > Sample(3) × Timepoint(4) > Cell(~8000)"
    return ExperimentalDesign.from_grammar(grammar)


def batch_effects_design() -> ExperimentalDesign:
    """Create a design with batch effects.

    Design includes:
    - Multiple nested and crossed factors
    - Cell type classification

    Note: Batch effects are better added programmatically after defining factors,
    as the grammar requires all factors to have size specifications.

    Returns:
        ExperimentalDesign object
    """
    grammar = """
    Site(3) > Patient(20) > Sample(2) × Treatment(3) > Cell(~5000) : CellType(42)
    """
    design = ExperimentalDesign.from_grammar(grammar)

    # Add batch effects programmatically
    design.add_factor("ProcessingBatch", 6, "batch")
    design.add_factor("SequencingRun", 8, "batch")
    design.add_batch_effect("ProcessingBatch", ["Sample"])
    design.add_batch_effect("SequencingRun", ["Cell"])

    return design


def complex_design() -> ExperimentalDesign:
    """Create a complex design with confounding, batch effects, and partial crossing.

    Design includes:
    - Confounded factors (Center and Protocol)
    - Unbalanced patient counts across centers
    - Partial crossing of samples with treatments
    - Full crossing with timepoints
    - Batch effects (added programmatically)
    - Cell type classification

    Returns:
        ExperimentalDesign object
    """
    grammar = """
    # Main structure with confounding
    {Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) ◊ Treatment(3) × Timepoint(4) > Cell(~5000) : CellType(42)
    """
    design = ExperimentalDesign.from_grammar(grammar)

    # Add batch effects programmatically
    design.add_factor("ProcessingBatch", 4, "batch")
    design.add_factor("SequencingRun", 8, "batch")
    design.add_batch_effect("ProcessingBatch", ["Sample"])
    design.add_batch_effect("SequencingRun", ["Cell"])

    return design


def programmatic_design() -> ExperimentalDesign:
    """Create a design programmatically (without grammar).

    This example shows how to build a design using the API methods
    instead of parsing a grammar string.

    Returns:
        ExperimentalDesign object
    """
    design = ExperimentalDesign()

    # Add factors
    design.add_factor("Hospital", 3)
    design.add_factor("Patient", 20)
    design.add_factor("Treatment", 2)
    design.add_factor("Sample", 3)
    design.add_factor("Cell", "~5000")
    design.add_factor("CellType", 35, "classification")

    # Add relationships
    design.add_nesting("Hospital", "Patient")
    design.add_crossing("Patient", "Treatment")
    design.add_nesting("Patient", "Sample")
    design.add_nesting("Sample", "Cell")
    design.add_classification("Cell", "CellType")

    return design


def main() -> None:
    """Run examples and display results."""
    print("=" * 60)
    print("Experimental Design Visualization Examples")
    print("=" * 60)
    print()

    # Example 1: Simple hierarchical
    print("1. Simple Hierarchical Design")
    print("-" * 60)
    design = simple_hierarchical()
    print(design.describe())
    print()
    print("ASCII Diagram:")
    print(design.ascii_diagram())
    print()

    # Example 2: Crossed design
    print("2. Crossed Factorial Design")
    print("-" * 60)
    design = crossed_design()
    print(design.describe())
    print()

    # Example 3: Batch effects
    print("3. Design with Batch Effects")
    print("-" * 60)
    design = batch_effects_design()
    print(design.describe())
    print()

    # Example 4: Complex design
    print("4. Complex Design")
    print("-" * 60)
    design = complex_design()
    print(design.describe())
    print()

    # Example 5: Programmatic construction
    print("5. Programmatically Constructed Design")
    print("-" * 60)
    design = programmatic_design()
    print(design.describe())
    print()

    # Export examples
    print("6. Export Examples")
    print("-" * 60)
    design = simple_hierarchical()

    # JSON export
    json_str = design.to_json()
    print(f"JSON export length: {len(json_str)} characters")

    # DOT export
    dot_str = design.to_dot()
    print(f"DOT export length: {len(dot_str)} characters")

    # GraphML export
    graphml_str = design.to_graphml()
    print(f"GraphML export length: {len(graphml_str)} characters")

    # NetworkX conversion
    graph = design.to_networkx()
    print(f"NetworkX graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print()

    # Validation example
    print("7. Validation Example")
    print("-" * 60)
    design = simple_hierarchical()
    issues = design.validate()
    if issues:
        print("Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Design is valid!")
    print()


if __name__ == "__main__":
    main()
