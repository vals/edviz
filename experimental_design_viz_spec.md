# Experimental Design Visualization Package Specification

## Package Overview

**Package Name**: `experimental_design_viz` (or `edviz` for short)

**Purpose**: Create a Python package for documenting, parsing, and visualizing complex experimental designs, particularly for biological experiments with hierarchical and crossed factors, batch effects, and confounding.

**Key Goals**:
1. Parse a compact text grammar into a structured representation
2. Export to standard graph formats (DOT, GraphML, JSON)
3. Visualize designs for publication and comparison
4. Document real-world experimental complexity (unbalanced data, batch effects, confounding)

## Core Grammar Specification

### Basic Syntax Elements

```
# Factors and sample sizes
Factor(n)           # Balanced factor with n levels
Factor[n1|n2|n3]    # Unbalanced factor with different sizes per branch
Factor(~n)          # Approximate count
Factor(n:m)         # n instances with m sub-categories

# Relationships
A > B               # A nests B (hierarchical)
A × B               # A fully crossed with B
A ◊ B               # A partially crossed with B
A : B               # A classified by B
A == B              # Batch effect from A to B
A ≈≈ B              # A confounded with B

# Grouping
{A B C}             # Group factors (often for confounded sets)
(A > B)             # Parentheses for precedence

# Comments
# This is a comment
```

### Grammar Rules

1. **Precedence** (highest to lowest):
   - Parentheses `()`
   - Classification `:`
   - Nesting `>`
   - Crossing `×` and `◊`
   - Batch effects `==`
   - Confounding `≈≈`

2. **Valid Structures**:
   - Factors must be defined before use
   - Cycles are not allowed in nesting
   - Classification (`:`) is terminal (no operations after)

### Example Grammar Strings

```python
# Simple hierarchical design
"Site(3) > Patient(20) > Sample(2) > Cell(5000) : CellType(35)"

# With crossing
"Hospital(4) > Patient(15) × Treatment(2) > Sample(3) × Timepoint(4) > Cell(~8000)"

# Complex with batch effects and confounding
"""
ProcessBatch(6) == Sample == SequencingRun
{Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) ◊ Treatment(3) > Cell(5k) : CellType(42)
"""
```

## Core API Design

### Main Classes

```python
class ExperimentalDesign:
    """Core class representing an experimental design."""
    
    @classmethod
    def from_grammar(cls, grammar_string: str) -> 'ExperimentalDesign':
        """Parse grammar string into design object."""
        pass
    
    @classmethod
    def from_dict(cls, design_dict: dict) -> 'ExperimentalDesign':
        """Create from dictionary representation."""
        pass
    
    def add_factor(self, name: str, n: Union[int, List[int], str]) -> None:
        """Add a factor. n can be: int, list of ints, or string like '~5000'."""
        pass
    
    def add_nesting(self, parent: str, child: str) -> None:
        """Add nesting relationship: parent > child."""
        pass
    
    def add_crossing(self, factor1: str, factor2: str, partial: bool = False) -> None:
        """Add crossing: × for full, ◊ for partial."""
        pass
    
    def add_classification(self, factor: str, classifier: str) -> None:
        """Add classification relationship: factor : classifier."""
        pass
    
    def add_batch_effect(self, batch_factor: str, affected: List[str]) -> None:
        """Add batch effect: batch == affected_factors."""
        pass
    
    def add_confound(self, factor1: str, factor2: str) -> None:
        """Add confounding: factor1 ≈≈ factor2."""
        pass
    
    def to_dict(self) -> dict:
        """Export to dictionary representation."""
        pass
    
    def to_json(self, filepath: Optional[str] = None) -> str:
        """Export to JSON string or file."""
        pass
    
    def to_dot(self, filepath: Optional[str] = None) -> str:
        """Export to Graphviz DOT format."""
        pass
    
    def to_graphml(self, filepath: Optional[str] = None) -> str:
        """Export to GraphML format."""
        pass
    
    def to_networkx(self) -> 'networkx.DiGraph':
        """Convert to NetworkX directed graph."""
        pass
    
    def ascii_diagram(self, width: int = 60) -> str:
        """Generate ASCII box diagram."""
        pass
    
    def validate(self) -> List[str]:
        """Validate design, return list of issues (empty if valid)."""
        pass
    
    def count_observations(self) -> int:
        """Calculate total observation count."""
        pass
    
    def describe(self) -> str:
        """Generate human-readable description."""
        pass
```

### Parser Module

```python
class DesignGrammarParser:
    """Parser for experimental design grammar."""
    
    def parse(self, grammar_string: str) -> ParsedDesign:
        """Parse grammar string into intermediate representation."""
        pass
    
    def tokenize(self, grammar_string: str) -> List[Token]:
        """Tokenize grammar string."""
        pass
    
    def validate_syntax(self, tokens: List[Token]) -> bool:
        """Validate token sequence."""
        pass
```

### Data Structures

```python
@dataclass
class Factor:
    name: str
    n: Union[int, List[int], str]  # int, unbalanced list, or ~approx
    type: str  # 'factor', 'observation', 'classification', 'batch'
    
@dataclass
class Relationship:
    from_factor: str
    to_factor: str
    rel_type: str  # 'nests', 'crosses', 'partial_crosses', 'classifies', 'batch_effect', 'confounded'
    
@dataclass
class ParsedDesign:
    factors: List[Factor]
    relationships: List[Relationship]
    metadata: dict
```

## Export Formats

### JSON Schema

```json
{
  "schema_version": "1.0",
  "study": "Optional study name",
  "factors": [
    {
      "name": "Patient",
      "n": [30, 25, 18],  // or single number, or "~5000"
      "type": "factor"
    }
  ],
  "relationships": [
    {
      "from": "Site",
      "to": "Patient", 
      "type": "nests"
    }
  ],
  "metadata": {
    "confound_groups": [["Center", "Protocol"]],
    "notes": "Optional notes"
  }
}
```

### DOT Template

```python
DOT_TEMPLATE = """
digraph ExperimentalDesign {{
  rankdir=TB;
  node [shape=box, style="rounded,filled"];
  
  // Factors
  {factors}
  
  // Relationships
  {relationships}
  
  // Confound groups
  {confound_groups}
}}
"""
```

### GraphML Template

Should follow standard GraphML schema with custom attributes for:
- Factor types
- Sample sizes  
- Relationship types
- Batch effects

## Visualization Specifications

### ASCII Diagram

```
┌─ Design Structure ─────────────────────────┐
│                                            │
│   Site(3)                                  │
│      ↓                                     │
│   Patient(20) ────×──── Treatment(2)       │
│      ↓                      ×              │
│   Sample(2) ──────×──── Timepoint(4)      │
│      ↓                                     │
│   Cell(~5k)                               │
│      :                                     │
│   CellType(35)                            │
│                                            │
└────────────────────────────────────────────┘
```

### Symbol Set

```python
SYMBOLS = {
    'nests': '↓',
    'crosses': '×', 
    'partial_crosses': '◊',
    'classifies': ':',
    'batch_effect': '══',
    'confounded': '≈≈',
    'box_horizontal': '─',
    'box_vertical': '│',
    'box_corners': {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘'}
}
```

## Implementation Requirements

### Dependencies

```python
# requirements.txt
networkx>=2.8
graphviz>=0.20  # optional, for rendering DOT
lxml>=4.9  # for GraphML
pytest>=7.0  # for testing
```

### File Structure

```
experimental_design_viz/
├── __init__.py
├── core.py          # ExperimentalDesign class
├── parser.py        # Grammar parser
├── validators.py    # Design validation
├── exporters/
│   ├── __init__.py
│   ├── dot.py
│   ├── graphml.py
│   └── json.py
├── visualizers/
│   ├── __init__.py
│   └── ascii.py
├── examples/
│   ├── __init__.py
│   └── biology.py
└── tests/
    ├── test_parser.py
    ├── test_core.py
    └── test_exporters.py
```

## Usage Examples

### Basic Usage

```python
from experimental_design_viz import ExperimentalDesign

# Parse from grammar
design = ExperimentalDesign.from_grammar(
    "Hospital(3) > Patient(20) > Sample(2) × Treatment(3) > Cell(5000) : CellType(35)"
)

# Export to various formats
design.to_json("design.json")
design.to_dot("design.dot")
design.to_graphml("design.graphml")

# Get ASCII visualization
print(design.ascii_diagram())

# Validate and describe
issues = design.validate()
if not issues:
    print(design.describe())
```

### Complex Example

```python
# Complex design with batch effects and confounding
complex_grammar = """
# Batch effects
ProcessingBatch(4) == Sample
SequencingRun(8) == Cell

# Main structure with confounding
{Center(3) ≈≈ Protocol(2)} > Patient[30|25|18] > Sample(2) ◊ Treatment(3) × Timepoint(4) > Cell(~5000) : CellType(42)
"""

design = ExperimentalDesign.from_grammar(complex_grammar)

# Programmatic construction alternative
design2 = ExperimentalDesign()
design2.add_factor("Center", 3)
design2.add_factor("Protocol", 2)
design2.add_factor("Patient", [30, 25, 18])
design2.add_confound("Center", "Protocol")
design2.add_nesting("Center", "Patient")
# ... etc

# Analysis
print(f"Total observations: {design.count_observations()}")
nx_graph = design.to_networkx()  # For further network analysis
```

## Testing Requirements

### Test Cases to Include

1. **Parser Tests**
   - Valid grammar strings
   - Invalid syntax
   - Edge cases (empty, very large designs)
   - Unicode symbols

2. **Design Tests**  
   - Cycle detection
   - Valid/invalid structures
   - Observation counting with different structures

3. **Export Tests**
   - Round-trip (grammar → design → JSON → design)
   - Valid output formats
   - Large design handling

### Example Test

```python
def test_simple_nesting():
    grammar = "Site(3) > Patient(20) > Cell(1000)"
    design = ExperimentalDesign.from_grammar(grammar)
    
    assert len(design.factors) == 3
    assert design.count_observations() == 3 * 20 * 1000
    
    json_str = design.to_json()
    design2 = ExperimentalDesign.from_dict(json.loads(json_str))
    assert design2.count_observations() == design.count_observations()
```

## Additional Features for Future Versions

1. **Statistical Analysis**
   - Degrees of freedom calculation
   - Power analysis integration
   - Valid contrast identification

2. **Interactive Visualization**
   - Plotly/Bokeh interactive graphs
   - Jupyter notebook widgets

3. **Comparison Tools**
   - Compare multiple designs
   - Identify common structures
   - Design similarity metrics

4. **Import from Statistical Software**
   - Parse R formula notation
   - Import from SAS/SPSS syntax
   - Integration with statsmodels

## Success Criteria

The package should:
1. Parse all example grammar strings correctly
2. Produce valid DOT/GraphML/JSON output
3. Handle designs with 50+ factors gracefully
4. Generate readable ASCII diagrams for designs up to 10 factors
5. Provide helpful error messages for invalid grammar
6. Install cleanly with pip

## Notes for Implementation

- Use regex or pyparsing for the grammar parser
- NetworkX for graph operations
- Keep core functionality dependency-light
- Make visualization dependencies optional
- Include comprehensive docstrings
- Follow PEP 8 style guidelines
- Target Python 3.8+

## Implementation Priority

1. **Phase 1 (Core)**: Parser, basic data structures, JSON export
2. **Phase 2 (Visualization)**: ASCII diagrams, DOT export
3. **Phase 3 (Extended)**: GraphML, NetworkX integration
4. **Phase 4 (Polish)**: Validation, error handling, comprehensive tests

This specification should provide Claude Code with everything needed to implement the package. Start with the parser and core classes, then add exporters, and finally visualization features.