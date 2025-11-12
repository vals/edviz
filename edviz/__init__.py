"""Experimental Design Visualization (edviz) package.

A package for documenting, parsing, and visualizing complex experimental designs.
"""

from edviz.core import ExperimentalDesign
from edviz.data_structures import Factor, Relationship, ParsedDesign

__version__ = "0.1.0"
__all__ = ["ExperimentalDesign", "Factor", "Relationship", "ParsedDesign"]
