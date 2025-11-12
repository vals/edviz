"""2D Canvas for ASCII art rendering.

This module provides a 2D grid-based canvas for rendering complex ASCII diagrams
with text, lines, and box-drawing characters.
"""

from typing import Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class LineStyle(Enum):
    """Line styles for drawing."""
    SINGLE = "single"  # ─ │ ┌ ┐ └ ┘
    DOUBLE = "double"  # ═ ║ ╔ ╗ ╚ ╝
    BOLD = "bold"      # ━ ┃ ┏ ┓ ┗ ┛


class Layer(Enum):
    """Z-index layers for rendering priority."""
    BACKGROUND = 0
    LINES = 1
    TEXT = 2
    ANNOTATIONS = 3


@dataclass
class Cell:
    """Represents a single cell in the canvas."""
    char: str = " "
    layer: Layer = Layer.BACKGROUND

    def can_overwrite(self, new_layer: Layer) -> bool:
        """Check if this cell can be overwritten by a new layer."""
        return new_layer.value >= self.layer.value


class Canvas:
    """2D canvas for ASCII art rendering.

    Provides a grid-based system for placing text and drawing lines
    with proper layering and collision detection.
    """

    # Box drawing characters
    BOX_CHARS = {
        LineStyle.SINGLE: {
            "h": "─",  # horizontal
            "v": "│",  # vertical
            "tl": "┌",  # top-left
            "tr": "┐",  # top-right
            "bl": "└",  # bottom-left
            "br": "┘",  # bottom-right
            "t": "┬",   # T junction down
            "b": "┴",   # T junction up
            "l": "├",   # T junction right
            "r": "┤",   # T junction left
            "cross": "┼",  # cross
        },
        LineStyle.DOUBLE: {
            "h": "═",
            "v": "║",
            "tl": "╔",
            "tr": "╗",
            "bl": "╚",
            "br": "╝",
            "t": "╦",
            "b": "╩",
            "l": "╠",
            "r": "╣",
            "cross": "╬",
        },
        LineStyle.BOLD: {
            "h": "━",
            "v": "┃",
            "tl": "┏",
            "tr": "┓",
            "bl": "┗",
            "br": "┛",
            "t": "┳",
            "b": "┻",
            "l": "┣",
            "r": "┫",
            "cross": "╋",
        },
    }

    def __init__(self, width: int, height: int):
        """Initialize canvas.

        Args:
            width: Width of canvas in characters
            height: Height of canvas in characters
        """
        self.width = width
        self.height = height
        self.grid: Dict[Tuple[int, int], Cell] = {}

    def get(self, x: int, y: int) -> Cell:
        """Get cell at position."""
        return self.grid.get((x, y), Cell())

    def set(self, x: int, y: int, char: str, layer: Layer = Layer.TEXT) -> bool:
        """Set character at position.

        Args:
            x: X coordinate (column)
            y: Y coordinate (row)
            char: Character to place
            layer: Layer for z-ordering

        Returns:
            True if character was placed, False if out of bounds or blocked
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        current = self.get(x, y)
        if current.can_overwrite(layer):
            self.grid[(x, y)] = Cell(char=char, layer=layer)
            return True
        return False

    def write_text(self, x: int, y: int, text: str, layer: Layer = Layer.TEXT) -> None:
        """Write text starting at position.

        Args:
            x: Starting X coordinate
            y: Y coordinate (row)
            text: Text to write
            layer: Layer for z-ordering
        """
        for i, char in enumerate(text):
            self.set(x + i, y, char, layer)

    def draw_hline(
        self,
        x1: int,
        x2: int,
        y: int,
        style: LineStyle = LineStyle.SINGLE,
        layer: Layer = Layer.LINES
    ) -> None:
        """Draw horizontal line.

        Args:
            x1: Start X coordinate
            x2: End X coordinate (inclusive)
            y: Y coordinate (row)
            style: Line style
            layer: Layer for z-ordering
        """
        char = self.BOX_CHARS[style]["h"]
        start, end = min(x1, x2), max(x1, x2)
        for x in range(start, end + 1):
            self.set(x, y, char, layer)

    def draw_vline(
        self,
        x: int,
        y1: int,
        y2: int,
        style: LineStyle = LineStyle.SINGLE,
        layer: Layer = Layer.LINES
    ) -> None:
        """Draw vertical line.

        Args:
            x: X coordinate (column)
            y1: Start Y coordinate
            y2: End Y coordinate (inclusive)
            style: Line style
            layer: Layer for z-ordering
        """
        char = self.BOX_CHARS[style]["v"]
        start, end = min(y1, y2), max(y1, y2)
        for y in range(start, end + 1):
            self.set(x, y, char, layer)

    def draw_corner(
        self,
        x: int,
        y: int,
        corner_type: str,  # "tl", "tr", "bl", "br"
        style: LineStyle = LineStyle.SINGLE,
        layer: Layer = Layer.LINES
    ) -> None:
        """Draw corner character.

        Args:
            x: X coordinate
            y: Y coordinate
            corner_type: Type of corner ("tl", "tr", "bl", "br")
            style: Line style
            layer: Layer for z-ordering
        """
        char = self.BOX_CHARS[style][corner_type]
        self.set(x, y, char, layer)

    def draw_box(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        style: LineStyle = LineStyle.SINGLE,
        title: str = ""
    ) -> None:
        """Draw a box.

        Args:
            x: Left X coordinate
            y: Top Y coordinate
            width: Width of box
            height: Height of box
            style: Line style
            title: Optional title to display in top border
        """
        chars = self.BOX_CHARS[style]

        # Corners
        self.set(x, y, chars["tl"], Layer.LINES)
        self.set(x + width - 1, y, chars["tr"], Layer.LINES)
        self.set(x, y + height - 1, chars["bl"], Layer.LINES)
        self.set(x + width - 1, y + height - 1, chars["br"], Layer.LINES)

        # Top and bottom
        if title:
            title_text = f" {title} "
            title_start = x + (width - len(title_text)) // 2
            # Left side of top border
            for i in range(x + 1, title_start):
                self.set(i, y, chars["h"], Layer.LINES)
            # Title
            self.write_text(title_start, y, title_text, Layer.TEXT)
            # Right side of top border
            for i in range(title_start + len(title_text), x + width - 1):
                self.set(i, y, chars["h"], Layer.LINES)
        else:
            # Full top border
            for i in range(x + 1, x + width - 1):
                self.set(i, y, chars["h"], Layer.LINES)

        # Bottom border (no title)
        for i in range(x + 1, x + width - 1):
            self.set(i, y + height - 1, chars["h"], Layer.LINES)

        # Sides
        for i in range(y + 1, y + height - 1):
            self.set(x, i, chars["v"], Layer.LINES)
            self.set(x + width - 1, i, chars["v"], Layer.LINES)

    def render(self) -> str:
        """Render canvas to string.

        Returns:
            Multi-line string representation of canvas
        """
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                cell = self.get(x, y)
                line += cell.char
            lines.append(line)
        return "\n".join(lines)

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get bounds of non-empty content.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        if not self.grid:
            return (0, 0, 0, 0)

        xs = [x for x, y in self.grid.keys()]
        ys = [y for x, y in self.grid.keys()]

        return (min(xs), min(ys), max(xs), max(ys))
