# edviz - Experimental Design Visualization

A Python package for documenting, parsing, and visualizing complex experimental designs, particularly for biological experiments with hierarchical and crossed factors, batch effects, and confounding.

## Features

- **Compact Grammar**: Express complex experimental designs in a simple text format
- **Advanced ASCII Visualization**: Rich diagrams with batch effect flow lines, confounding connections, and spatial layout
- **Multiple Export Formats**: Export to JSON, DOT (Graphviz), and GraphML
- **NetworkX Integration**: Convert designs to NetworkX graphs for analysis
- **Validation**: Detect cycles, invalid structures, and other design issues

## Installation

```bash
pip install edviz
```

For optional visualization support:
```bash
pip install edviz[viz]
```

## Quick Start

```python
from edviz import ExperimentalDesign

# Parse from grammar
design = ExperimentalDesign.from_grammar(
    "Hospital(3) > Patient(20) > Sample(2) × Treatment(3) > Cell(5000) : CellType(35)"
)

# Get advanced ASCII visualization with rich visual connections
print(design.ascii_diagram())

# Export to various formats
design.to_json("design.json")
design.to_dot("design.dot")
design.to_graphml("design.graphml")

# Validate and describe
issues = design.validate()
if not issues:
    print(design.describe())
```

### ASCII Visualization Example

```
┌─────────────────────── Design Structure ───────────────────────┐
│                                                                │
│ ProcessingBatch(6)═════════════════════════════════════════╗   │
│                                                            ║   │
│ Center(3)  ≈≈≈≈  Protocol(2)                               ║   │
│    ↓                ↓                                      ║   │
│ Patient([30 | 25 | 18])                                    ║   │
│    ↓                                                       ║   │
│ Sample(2) ═════════════════════════════════════════════════╝   │
│    ↓                                                           │
│ Cell(~5000)                                                    │
│    :                                                           │
│ CellType(42)                                                   │
│                                                                │
│   Confounded: Center ≈≈ Protocol                               │
│   Batch: ProcessingBatch ══ Sample                             │
└────────────────────────────────────────────────────────────────┘
```

### Run Interactive Demos

```bash
# Basic demo with simple examples
python demo.py

# Show ASCII diagrams for complex designs
python demo.py --diagrams

# Compare different design patterns
python demo.py --patterns

# Show everything
python demo.py --all
```

## Grammar Syntax

### Factors
```
Factor(n)           # Balanced factor with n levels
Factor[n1|n2|n3]    # Unbalanced factor with different sizes per branch
Factor(~n)          # Approximate count
Factor(5k)          # Using 'k' for thousands
```

### Relationships
```
A > B               # A nests B (hierarchical)
A × B               # A fully crossed with B
A ◊ B               # A partially crossed with B
A : B               # A classified by B
{A ≈≈ B}            # A confounded with B
```

### Batch Effects

**Note**: Batch effects must be added programmatically (grammar parsing not supported).

```python
design.add_factor("ProcessingBatch", 6, "batch")
design.add_batch_effect("ProcessingBatch", ["Sample"])
```

## Examples

### Simple Hierarchical Design
```python
design = ExperimentalDesign.from_grammar(
    "Site(3) > Patient(20) > Sample(2) > Cell(5000) : CellType(35)"
)
print(design.ascii_diagram())
```

### Complex Design with Batch Effects
```python
# Create design
design = ExperimentalDesign.from_grammar(
    "{Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) > Cell(~5000) : CellType(42)"
)

# Add batch effects programmatically
design.add_factor("ProcessingBatch", 4, "batch")
design.add_factor("SequencingRun", 8, "batch")
design.add_batch_effect("ProcessingBatch", ["Sample"])
design.add_batch_effect("SequencingRun", ["Cell"])

# Visualize
print(design.ascii_diagram(width=80))
print(f"Total observations: {design.count_observations()}")
```

### Programmatic Construction
```python
design = ExperimentalDesign()

# Add factors
design.add_factor("Hospital", 4)
design.add_factor("Patient", 15)
design.add_factor("Treatment", 2)

# Add relationships
design.add_nesting("Hospital", "Patient")
design.add_crossing("Patient", "Treatment")

# Validate
issues = design.validate()
if not issues:
    print("✓ Design is valid!")
```

## Visualization Features

The advanced ASCII visualizer includes:

- **Batch Effect Flow Lines**: Double-line characters (║ ═ ╗ ╝) showing batch effects through hierarchy
- **Confounding Connections**: Side-by-side factors with visual connections (≈≈≈≈)
- **Classification Symbol**: Uses `:` for classification relationships
- **Crossing Symbols**: `×` for full crossing, `◊` for partial crossing
- **Spatial Layout**: Smart 2D positioning prevents visual clutter
- **Annotations**: Clear notes at bottom for batch effects and confounding

## Export Formats

- **JSON**: For data interchange and storage
- **DOT**: For Graphviz visualization (complex graph layouts)
- **GraphML**: For network analysis tools (Gephi, Cytoscape)
- **NetworkX**: For programmatic graph analysis in Python

## Documentation

- [GRAMMAR.md](GRAMMAR.md) - **Formal grammar specification (for AI agents and implementers)**
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide with examples
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) - Known limitations and workarounds
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details
- [ADVANCED_ASCII_IMPLEMENTATION.md](ADVANCED_ASCII_IMPLEMENTATION.md) - ASCII visualization technical docs
- [experimental_design_viz_spec.md](experimental_design_viz_spec.md) - Original specification

## License

MIT License
