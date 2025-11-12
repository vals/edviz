# Changelog

All notable changes to edviz will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Advanced ASCII visualization with rich visual connections
  - Batch effect flow lines using double-line characters (║ ═ ╗ ╝)
  - Confounding connections with horizontal links (≈≈≈≈)
  - Classification relationships with `:` symbol
  - Full and partial crossing with `×` and `◊` symbols
  - Spatial 2D layout with proper alignment
- Canvas-based rendering system with layer management
- Formal EBNF grammar specification in GRAMMAR.md
- Comprehensive documentation for AI agents
- NetworkX graph export functionality
- Multiple export formats: JSON, DOT (Graphviz), GraphML
- Validation system for detecting cycles and invalid structures
- Support for unbalanced designs with different branch sizes
- Approximate count notation using `~` prefix
- Thousands notation using `k` suffix (e.g., `5k` for 5000)

### Changed
- Batch effects must be added programmatically (not via grammar)
- Visualizer produces richer diagrams with better spatial layout

### Fixed
- Batch effect flow line alignment issues
- Factor duplication in complex crossed designs
- Corner characters being overwritten by vertical lines

### Known Issues
- Parser cannot handle batch effect syntax in grammar
- Parser may create unexpected relationships for complex crossing patterns
- See KNOWN_ISSUES.md for detailed workarounds

## [0.1.0] - Initial Development

### Added
- Basic experimental design grammar parser
- Core data structures for design representation
- Simple text-based visualization
- Programmatic API for building designs
- Basic validation

---

## Version History Guidelines

### Types of Changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

### Versioning
- **Major** (X.0.0): Breaking changes, major rewrites
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, minor improvements
