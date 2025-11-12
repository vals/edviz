# edviz Quick Start Guide

## Installation

```bash
cd /Users/val/Documents/Software/edviz
pip install -e .
```

## Basic Usage

### 1. Parse a Design from Grammar

```python
from edviz import ExperimentalDesign

design = ExperimentalDesign.from_grammar(
    "Site(3) > Patient(20) > Sample(2) > Cell(5000) : CellType(35)"
)

print(design.describe())
```

### 2. View ASCII Diagram

```python
print(design.ascii_diagram())
```

Output:
```
┌──────────────────── Design Structure ────────────────────┐
│  Site(3)
│     ↓
│  Patient(20)
│     ↓
│  Sample(2)
│     ↓
│  Cell(5000)
│     :
│  CellType(35)
└──────────────────────────────────────────────────────────┘
```

### 3. Count Observations

```python
total = design.count_observations()
print(f"Total observations: {total:,}")
# Output: Total observations: 600,000
```

### 4. Validate Design

```python
issues = design.validate()
if issues:
    print("Issues found:", issues)
else:
    print("✓ Design is valid!")
```

### 5. Export to Different Formats

```python
# JSON
design.to_json("design.json")

# Graphviz DOT
design.to_dot("design.dot")

# GraphML
design.to_graphml("design.graphml")

# NetworkX graph
graph = design.to_networkx()
print(f"Nodes: {graph.number_of_nodes()}, Edges: {graph.number_of_edges()}")
```

## Grammar Syntax Cheat Sheet

| Syntax | Meaning | Example |
|--------|---------|---------|
| `A(n)` | Factor A with n levels | `Site(3)` |
| `A[n1\|n2]` | Unbalanced factor | `Patient[30\|25\|18]` |
| `A(~n)` | Approximate count | `Cell(~5000)` |
| `A(5k)` | Using 'k' for thousands | `Cell(5k)` |
| `A > B` | A nests B | `Site(3) > Patient(20)` |
| `A × B` | A crosses B (fully) | `Treatment(2) × Timepoint(4)` |
| `A ◊ B` | A partially crosses B | `Sample(2) ◊ Treatment(3)` |
| `A : B` | A classified by B | `Cell(5000) : CellType(35)` |
| `{A ≈≈ B}` | A confounded with B | `{Center(3) ≈≈ Protocol(2)}` |
| `# comment` | Comment | `# This is a comment` |

## Programmatic Construction

Instead of using grammar, you can build designs programmatically:

```python
design = ExperimentalDesign()

# Add factors
design.add_factor("Hospital", 3)
design.add_factor("Patient", 20)
design.add_factor("Treatment", 2)

# Add relationships
design.add_nesting("Hospital", "Patient")
design.add_crossing("Patient", "Treatment")

# Add batch effects
design.add_factor("ProcessingBatch", 4, "batch")
design.add_batch_effect("ProcessingBatch", ["Patient"])
```

## Common Patterns

### Hierarchical Design
```python
design = ExperimentalDesign.from_grammar(
    "Site(3) > Patient(20) > Sample(2) > Cell(5000)"
)
```

### Factorial Design
```python
design = ExperimentalDesign.from_grammar(
    "Treatment(3) × Timepoint(4) × Replicate(5)"
)
```

### Mixed Design (Nested + Crossed)
```python
design = ExperimentalDesign.from_grammar(
    "Hospital(4) > Patient(15) × Treatment(2) > Sample(3)"
)
```

### With Classification
```python
design = ExperimentalDesign.from_grammar(
    "Sample(100) > Cell(5000) : CellType(35)"
)
```

### Complex Design
```python
grammar = """
{Center(3) ≈≈ Protocol(2)} >
Patient[30|25|18] >
Sample(2) ◊ Treatment(3) × Timepoint(4) >
Cell(~5000) : CellType(42)
"""
design = ExperimentalDesign.from_grammar(grammar)
```

## Run Examples

```bash
# Basic demo with simple examples
python demo.py

# Show ASCII diagrams for complex designs
python demo.py --diagrams

# Compare different design patterns
python demo.py --patterns

# Show everything
python demo.py --all

# Run example suite
python -m edviz.examples.biology
```

## Run Tests

```bash
pytest edviz/tests/ -v
```

## Next Steps

- Read the full [README.md](README.md)
- Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details
- Explore [examples/biology.py](edviz/examples/biology.py) for more examples
- See the original [specification](experimental_design_viz_spec.md)
