# Known Issues and Limitations

## Parser Limitations

### 1. Batch Effects Cannot Be Parsed from Grammar

**Issue**: The grammar parser cannot handle batch effect syntax where the target factor is a reference.

**Example that fails:**
```python
grammar = """
ProcessingBatch(4) == Sample
Site(3) > Patient(20) > Sample(2) > Cell(~5000)
"""
design = ExperimentalDesign.from_grammar(grammar)  # ✗ Error!
```

**Error**: `ValueError: Expected size specification for factor Sample at position 23`

**Why**: The parser expects every factor mention to include a size specification `Factor(n)`, but in `ProcessingBatch(4) == Sample`, the `Sample` should be a reference to a factor defined elsewhere.

**Workaround**: Add batch effects programmatically after parsing:

```python
# ✓ Correct approach
design = ExperimentalDesign.from_grammar(
    "Site(3) > Patient(20) > Sample(2) > Cell(~5000)"
)
design.add_factor("ProcessingBatch", 4, "batch")
design.add_batch_effect("ProcessingBatch", ["Sample"])
```

**Status**: Known limitation. The programmatic approach is the recommended pattern.

---

### 2. Parser Creates Unexpected Relationships for Complex Crossing

**Issue**: For complex expressions with mixed crossing and nesting, the parser may create relationships that don't match intuitive interpretation.

**Example:**
```python
grammar = "Patient(15) × Treatment(2) > Sample(3)"
```

**Expected relationships:**
- `Patient nests Sample`
- `Patient crosses Treatment`
- `Treatment crosses Sample` (or `Treatment nests Sample`)

**Actual relationships:**
- `Patient crosses Sample`
- `Treatment nests Sample`

**Why**: The parser follows strict precedence rules that may not match the intuitive "left-to-right" reading.

**Impact**:
- Factors may appear multiple times in ASCII visualizations
- Relationship structure may be confusing for complex designs

**Workaround**: Use programmatic construction for complex mixed designs:

```python
design = ExperimentalDesign()
design.add_factor("Patient", 15)
design.add_factor("Treatment", 2)
design.add_factor("Sample", 3)
design.add_nesting("Patient", "Sample")
design.add_crossing("Patient", "Treatment")
design.add_crossing("Treatment", "Sample")
```

**Status**: Under investigation. The visualization handles this gracefully by showing factors where the parser places them.

---

## Visualization Notes

### Factor Duplication in Complex Designs

Due to parser issue #2 above, factors may appear multiple times in ASCII diagrams when they participate in both crossing and nesting relationships. This is not a visualization bug - the visualizer correctly displays the relationships as created by the parser.

**Example:**
```
│ Patient(15)  ────×──── Sample(3)       │
│    ↓                                   │
│ Treatment(2)                           │
│    ↓                                   │
│ Sample(3)  ────×──── Patient(15)       │  <-- Sample appears again
```

The visualizer shows Sample twice because the parser created it as both:
1. A crossing target from Patient
2. A nested child of Treatment

---

## Design Decisions

### Batch Effects Are Programmatic

After evaluating the trade-offs, batch effects are intentionally added programmatically rather than via grammar. This provides:

✅ **Clearer semantics** - Batch factors are clearly distinguished from design factors
✅ **Better validation** - Can validate batch targets exist
✅ **Flexibility** - Can add multiple batch effects easily
✅ **No ambiguity** - No confusion about factor references vs. definitions

### Grammar is for Design Structure, API is for Metadata

The grammar syntax focuses on the experimental design structure (nesting, crossing, classification). Additional metadata like batch effects and detailed annotations are better expressed programmatically.

This separation makes the grammar:
- Easier to read and write
- Focused on the core design
- Less prone to parsing ambiguity

---

## Future Improvements

Potential enhancements being considered:

1. **Factor References**: Allow `@FactorName` syntax for references without size specs
2. **Improved Crossing Semantics**: Better handling of mixed crossing/nesting
3. **Grammar Validation**: Pre-parse validation to catch issues earlier
4. **Parser Error Messages**: More helpful error messages with suggestions

---

## Reporting Issues

If you encounter a parser or visualization issue:

1. Try the programmatic API as a workaround
2. Check if it's listed in this document
3. File an issue at: https://github.com/vals/edviz/issues
4. Include the grammar string and expected vs. actual behavior
