#!/usr/bin/env python
"""Quick demo of edviz package capabilities."""

import argparse
from edviz import ExperimentalDesign


def show_basic_demo():
    """Show basic demo with simple examples."""
    print("=" * 70)
    print("EDVIZ DEMO - Experimental Design Visualization")
    print("=" * 70)
    print()

    # Example 1: Simple hierarchical design
    print("1. Simple Hierarchical Design")
    print("-" * 70)
    grammar1 = "Site(3) > Patient(20) > Sample(2) > Cell(5000) : CellType(35)"
    design1 = ExperimentalDesign.from_grammar(grammar1)
    print(f"Grammar: {grammar1}")
    print(f"Total observations: {design1.count_observations():,}")
    print()
    print(design1.ascii_diagram())
    print()

    # Example 2: Complex design with confounding
    print("2. Complex Design with Confounding and Crossing")
    print("-" * 70)
    grammar2 = "{Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) ◊ Treatment(3) × Timepoint(4) > Cell(~5000)"
    design2 = ExperimentalDesign.from_grammar(grammar2)
    print(f"Grammar: {grammar2}")
    print()
    print(design2.describe())
    print()

    # Example 3: Programmatic construction
    print("3. Programmatic Construction")
    print("-" * 70)
    design3 = ExperimentalDesign()
    design3.add_factor("Hospital", 4)
    design3.add_factor("Patient", 15)
    design3.add_factor("Treatment", 2)
    design3.add_factor("Sample", 3)
    design3.add_nesting("Hospital", "Patient")
    design3.add_crossing("Patient", "Treatment")
    design3.add_nesting("Patient", "Sample")

    print("Built design programmatically:")
    print(f"  - {len(design3.factors)} factors")
    print(f"  - {len(design3.relationships)} relationships")
    print(f"  - Total observations: {design3.count_observations():,}")
    print()

    # Validation
    print("4. Validation")
    print("-" * 70)
    issues = design3.validate()
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Design is valid!")
    print()

    # Export examples
    print("5. Export Formats")
    print("-" * 70)
    print("Available export formats:")
    print("  - JSON (for data interchange)")
    print("  - DOT (for Graphviz visualization)")
    print("  - GraphML (for network analysis tools)")
    print("  - NetworkX (for Python network analysis)")
    print()

    # NetworkX example
    graph = design1.to_networkx()
    print(f"NetworkX graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print()

    print("=" * 70)
    print("Demo complete! Try --diagrams or --patterns for more examples.")
    print("=" * 70)


def show_diagrams():
    """Display ASCII diagrams for complex experimental designs."""
    print("=" * 80)
    print("COMPLEX EXPERIMENTAL DESIGN ASCII DIAGRAMS")
    print("=" * 80)
    print()

    examples = [
        {
            "title": "1. CROSSED FACTORIAL DESIGN",
            "grammar": "Hospital(4) > Patient(15) × Treatment(2) > Sample(3) × Timepoint(4) > Cell(~8000)",
        },
        {
            "title": "2. DESIGN WITH PARTIAL CROSSING",
            "grammar": "Site(3) > Patient(20) > Sample(2) ◊ Treatment(3) > Cell(~5000)",
        },
        {
            "title": "3. DESIGN WITH CONFOUNDED FACTORS",
            "grammar": "{Center(3) ≈≈ Protocol(2)} > Patient(30) > Sample(2)",
        },
        {
            "title": "4. UNBALANCED DESIGN",
            "grammar": "Center[30|25|18] > Patient(5) > Sample(3) > Cell(1000)",
        },
        {
            "title": "5. COMPLEX MULTI-RELATIONSHIP DESIGN",
            "grammar": "{Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) ◊ Treatment(3) × Timepoint(4) > Cell(~5000) : CellType(42)",
        },
        {
            "title": "6. DEEPLY NESTED HIERARCHICAL DESIGN",
            "grammar": "Country(4) > Region(5) > Hospital(3) > Ward(2) > Patient(10) > Sample(3) > Cell(500)",
        },
        {
            "title": "7. MULTIPLE CROSSING FACTORS",
            "grammar": "Subject(10) × Treatment(3) × Timepoint(5) × Dose(4) > Measurement(2)",
        },
    ]

    for example in examples:
        print(example["title"])
        print("=" * 80)
        print(f"Grammar: {example['grammar']}")
        print()
        design = ExperimentalDesign.from_grammar(example["grammar"])
        print(design.ascii_diagram(width=80))
        obs = design.count_observations()
        print(f"\nTotal observations: {obs if isinstance(obs, str) else f'{obs:,}'}")
        print()
        print()

    # Example with batch effects
    print("8. DESIGN WITH BATCH EFFECTS")
    print("=" * 80)
    grammar = "Site(3) > Patient(20) > Sample(2) × Treatment(3) > Cell(~5000) : CellType(42)"
    print(f"Grammar: {grammar}")
    design = ExperimentalDesign.from_grammar(grammar)
    # Add batch effects programmatically
    design.add_factor("ProcessingBatch", 6, "batch")
    design.add_factor("SequencingRun", 8, "batch")
    design.add_batch_effect("ProcessingBatch", ["Sample"])
    design.add_batch_effect("SequencingRun", ["Cell"])
    print("+ Added batch effects: ProcessingBatch(6) and SequencingRun(8)")
    print()
    print(design.ascii_diagram(width=80))
    print(f"\nTotal observations: {design.count_observations()}")
    print()
    print("Batch effects:")
    print("  - ProcessingBatch(6) affects Sample")
    print("  - SequencingRun(8) affects Cell")
    print()

    print("=" * 80)
    print("End of ASCII Diagram Examples")
    print("=" * 80)


def show_design(title, grammar, description=""):
    """Display a design with its grammar and diagram."""
    print(f"\n{title}")
    print("─" * 80)
    print(f"Grammar: {grammar}")
    if description:
        print(f"Description: {description}")
    print()
    design = ExperimentalDesign.from_grammar(grammar)
    print(design.ascii_diagram(width=80))

    # Show key metrics
    obs = design.count_observations()
    print(f"\n📊 Metrics:")
    print(f"   • Factors: {len(design.factors)}")
    print(f"   • Relationships: {len(design.relationships)}")
    print(f"   • Total observations: {obs if isinstance(obs, str) else f'{obs:,}'}")

    # Show validation
    issues = design.validate()
    status = "✅ Valid" if not issues else f"⚠️  Issues: {', '.join(issues)}"
    print(f"   • Validation: {status}")
    print()


def show_patterns():
    """Compare different experimental design patterns side by side."""
    print("=" * 80)
    print("EXPERIMENTAL DESIGN PATTERN COMPARISON")
    print("=" * 80)

    # Pattern 1: Pure hierarchy
    show_design(
        "PATTERN 1: PURE HIERARCHICAL (Nested)",
        "Country(3) > Region(4) > Site(5) > Patient(20) > Sample(2)",
        "Classic nested structure - each level contained in the one above"
    )

    # Pattern 2: Pure factorial
    show_design(
        "PATTERN 2: PURE FACTORIAL (Crossed)",
        "Treatment(3) × Dose(4) × Timepoint(5) × Replicate(3)",
        "Fully crossed design - all combinations of all factors"
    )

    # Pattern 3: Mixed (split-plot)
    show_design(
        "PATTERN 3: SPLIT-PLOT (Mixed nested and crossed)",
        "Field(6) > Plot(4) × Treatment(3) > Measurement(5)",
        "Nested fields/plots, but treatments crossed with plots"
    )

    # Pattern 4: Repeated measures
    show_design(
        "PATTERN 4: REPEATED MEASURES",
        "Subject(20) × Timepoint(6) × Condition(3) > Measurement(10)",
        "Subjects measured repeatedly across time and conditions"
    )

    # Pattern 5: With classification
    show_design(
        "PATTERN 5: WITH CLASSIFICATION",
        "Sample(100) > Cell(5000) : CellType(35)",
        "Cells classified into types - useful for scRNA-seq data"
    )

    # Pattern 6: Partial crossing
    show_design(
        "PATTERN 6: PARTIAL CROSSING (Incomplete)",
        "Hospital(5) > Patient(20) > Sample(3) ◊ Treatment(4)",
        "Not all samples receive all treatments"
    )

    # Pattern 7: Confounding
    show_design(
        "PATTERN 7: CONFOUNDED DESIGN",
        "{Batch(4) ≈≈ Technician(4)} > Sample(30) > Measurement(5)",
        "Batch and technician perfectly confounded (same thing)"
    )

    # Pattern 8: Unbalanced
    show_design(
        "PATTERN 8: UNBALANCED DESIGN",
        "Clinic[45|38|52|29] > Patient(10) > Visit(3) > Measurement(2)",
        "Different numbers of something at each level"
    )

    # Pattern 9: Large-scale scRNA-seq
    show_design(
        "PATTERN 9: SINGLE-CELL RNA-SEQ STUDY",
        "{Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) × Treatment(3) > Cell(~8000) : CellType(42)",
        "Realistic scRNA-seq: confounding, unbalanced, approximate counts, classification"
    )

    # Pattern 10: Clinical trial
    show_design(
        "PATTERN 10: CLINICAL TRIAL",
        "Site(8) > Patient(50) × Treatment(3) × Timepoint(5) > Biomarker(12)",
        "Multi-site trial with repeated measures"
    )

    print("=" * 80)
    print("KEY OBSERVATIONS:")
    print("=" * 80)
    print("""
1. HIERARCHICAL (>): Each child is nested within exactly one parent
   - Clear top-down structure
   - Observations multiply through levels

2. CROSSED (×): All combinations of factors
   - Factorial designs
   - Can dramatically increase observation count

3. PARTIAL CROSSING (◊): Some but not all combinations
   - Realistic for resource constraints
   - Smaller than full crossing

4. CLASSIFICATION (:): Terminal relationship
   - Used for categorizing observations
   - Common in single-cell data (CellType)

5. CONFOUNDING (≈≈): Factors that vary together
   - Cannot separate their effects
   - Important to document

6. UNBALANCED [n1|n2|...]: Different counts per branch
   - Realistic for real-world data
   - Still analyzable

7. APPROXIMATE (~n): Unknown exact count
   - Common in single-cell sequencing
   - Shows intent/expectation

RELATIONSHIP PRECEDENCE (highest to lowest):
  () > : > > > × and ◊ > == > ≈≈
""")

    print("=" * 80)


def main():
    """Main entry point for demo script."""
    parser = argparse.ArgumentParser(
        description="Demo script for edviz experimental design visualization package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo.py              # Basic demo with simple examples
  python demo.py --diagrams   # Show ASCII diagrams for complex designs
  python demo.py --patterns   # Compare different design patterns
  python demo.py --all        # Show everything
        """
    )

    parser.add_argument(
        "--diagrams",
        action="store_true",
        help="Show ASCII diagrams for complex experimental designs"
    )

    parser.add_argument(
        "--patterns",
        action="store_true",
        help="Compare different experimental design patterns"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all demos (basic, diagrams, and patterns)"
    )

    args = parser.parse_args()

    # Determine what to show
    if args.all:
        show_basic_demo()
        print("\n\n")
        show_diagrams()
        print("\n\n")
        show_patterns()
    elif args.diagrams:
        show_diagrams()
    elif args.patterns:
        show_patterns()
    else:
        # Default: basic demo
        show_basic_demo()


if __name__ == "__main__":
    main()
