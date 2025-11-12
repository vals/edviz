"""Parser for experimental design grammar."""

import re
from dataclasses import dataclass
from typing import List, Union, Tuple, Optional
from edviz.data_structures import Factor, Relationship, ParsedDesign, FactorType


@dataclass
class Token:
    """Represents a token in the grammar."""
    type: str
    value: str
    position: int


class DesignGrammarParser:
    """Parser for experimental design grammar.

    Grammar precedence (highest to lowest):
    1. Parentheses ()
    2. Classification :
    3. Nesting >
    4. Crossing × and ◊
    5. Batch effects ==
    6. Confounding ≈≈
    """

    # Token patterns
    PATTERNS = [
        ("COMMENT", r"#[^\n]*"),
        ("WHITESPACE", r"\s+"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACKET", r"\["),
        ("RBRACKET", r"\]"),
        ("CONFOUNDED", r"≈≈"),
        ("BATCH", r"=="),
        ("PARTIAL_CROSS", r"◊"),
        ("CROSS", r"×"),
        ("NESTS", r">"),
        ("CLASSIFIES", r":"),
        ("PIPE", r"\|"),
        ("TILDE", r"~"),
        ("NUMBER", r"\d+k?"),
        ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
    ]

    def __init__(self) -> None:
        """Initialize the parser."""
        self.tokens: List[Token] = []
        self.current = 0
        self.parsed_design = ParsedDesign()

    def parse(self, grammar_string: str) -> ParsedDesign:
        """Parse grammar string into intermediate representation.

        Args:
            grammar_string: The grammar string to parse

        Returns:
            ParsedDesign object containing factors and relationships

        Raises:
            ValueError: If the grammar is invalid
        """
        self.tokens = self.tokenize(grammar_string)
        self.current = 0
        self.parsed_design = ParsedDesign()

        if not self.tokens:
            return self.parsed_design

        # Parse the entire expression
        self._parse_confounding()

        # Check for remaining tokens
        if self.current < len(self.tokens):
            raise ValueError(f"Unexpected token at position {self.current}: {self.tokens[self.current].value}")

        return self.parsed_design

    def tokenize(self, grammar_string: str) -> List[Token]:
        """Tokenize grammar string.

        Args:
            grammar_string: The grammar string to tokenize

        Returns:
            List of tokens

        Raises:
            ValueError: If invalid characters are found
        """
        tokens = []
        position = 0

        while position < len(grammar_string):
            match_found = False

            for token_type, pattern in self.PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(grammar_string, position)

                if match:
                    value = match.group(0)
                    if token_type not in ("COMMENT", "WHITESPACE"):
                        tokens.append(Token(token_type, value, position))
                    position = match.end()
                    match_found = True
                    break

            if not match_found:
                raise ValueError(f"Invalid character at position {position}: '{grammar_string[position]}'")

        return tokens

    def _current_token(self) -> Optional[Token]:
        """Get current token."""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def _consume(self, expected_type: Optional[str] = None) -> Token:
        """Consume and return current token.

        Args:
            expected_type: If provided, validates token type

        Returns:
            The consumed token

        Raises:
            ValueError: If token type doesn't match expected
        """
        token = self._current_token()
        if token is None:
            raise ValueError("Unexpected end of input")

        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type} but got {token.type} at position {token.position}")

        self.current += 1
        return token

    def _peek_type(self) -> Optional[str]:
        """Peek at current token type without consuming."""
        token = self._current_token()
        return token.type if token else None

    def _parse_confounding(self) -> List[str]:
        """Parse confounding level (lowest precedence).

        Returns:
            List of factor names at this level
        """
        factors = self._parse_batch()

        while self._peek_type() == "CONFOUNDED":
            self._consume("CONFOUNDED")
            right_factors = self._parse_batch()

            # Add confounding relationships
            for left_factor in factors:
                for right_factor in right_factors:
                    self.parsed_design.relationships.append(
                        Relationship(left_factor, right_factor, "confounded")
                    )

            factors.extend(right_factors)

        return factors

    def _parse_batch(self) -> List[str]:
        """Parse batch effect level.

        Returns:
            List of factor names at this level
        """
        factors = self._parse_crossing()

        while self._peek_type() == "BATCH":
            self._consume("BATCH")
            right_factors = self._parse_crossing()

            # Add batch effect relationships
            for left_factor in factors:
                for right_factor in right_factors:
                    self.parsed_design.relationships.append(
                        Relationship(left_factor, right_factor, "batch_effect")
                    )

            factors.extend(right_factors)

        return factors

    def _parse_crossing(self) -> List[str]:
        """Parse crossing level.

        Returns:
            List of factor names at this level
        """
        factors = self._parse_nesting()

        while self._peek_type() in ("CROSS", "PARTIAL_CROSS"):
            cross_type = self._consume()
            right_factors = self._parse_nesting()

            rel_type = "crosses" if cross_type.type == "CROSS" else "partial_crosses"

            # Add crossing relationships
            for left_factor in factors:
                for right_factor in right_factors:
                    self.parsed_design.relationships.append(
                        Relationship(left_factor, right_factor, rel_type)
                    )

            factors.extend(right_factors)

        return factors

    def _parse_nesting(self) -> List[str]:
        """Parse nesting level.

        Returns:
            List of factor names at this level
        """
        factors = self._parse_classification()

        while self._peek_type() == "NESTS":
            self._consume("NESTS")
            right_factors = self._parse_classification()

            # Add nesting relationships
            for left_factor in factors:
                for right_factor in right_factors:
                    self.parsed_design.relationships.append(
                        Relationship(left_factor, right_factor, "nests")
                    )

            factors = right_factors  # Only return the nested factors for further nesting

        return factors

    def _parse_classification(self) -> List[str]:
        """Parse classification level (highest precedence).

        Returns:
            List of factor names at this level
        """
        factors = self._parse_primary()

        if self._peek_type() == "CLASSIFIES":
            self._consume("CLASSIFIES")
            classifier_factors = self._parse_primary()

            # Add classification relationships
            for factor in factors:
                for classifier in classifier_factors:
                    self.parsed_design.relationships.append(
                        Relationship(factor, classifier, "classifies")
                    )
                    # Mark classifier as classification type
                    classifier_factor = self.parsed_design.get_factor(classifier)
                    if classifier_factor:
                        classifier_factor.type = "classification"

        return factors

    def _parse_primary(self) -> List[str]:
        """Parse primary expression (factor, group, or parenthesized expression).

        Returns:
            List of factor names
        """
        token_type = self._peek_type()

        if token_type == "LBRACE":
            # Parse confound group: {A ≈≈ B}
            return self._parse_group()
        elif token_type == "LPAREN":
            # Parse parenthesized expression
            self._consume("LPAREN")
            factors = self._parse_confounding()
            self._consume("RPAREN")
            return factors
        elif token_type == "IDENTIFIER":
            # Parse factor
            return [self._parse_factor()]
        else:
            raise ValueError(f"Unexpected token: {token_type}")

    def _parse_group(self) -> List[str]:
        """Parse a confounded group: {A ≈≈ B ≈≈ C}.

        Returns:
            List of factor names in the group
        """
        self._consume("LBRACE")

        factors = []
        factors.append(self._parse_factor())

        # Store confound group in metadata
        confound_group = [factors[0]]

        while self._peek_type() == "CONFOUNDED":
            self._consume("CONFOUNDED")
            factor = self._parse_factor()
            factors.append(factor)
            confound_group.append(factor)

            # Add confounding relationship
            for existing_factor in confound_group[:-1]:
                self.parsed_design.relationships.append(
                    Relationship(existing_factor, factor, "confounded")
                )

        self._consume("RBRACE")

        # Store confound group in metadata
        if "confound_groups" not in self.parsed_design.metadata:
            self.parsed_design.metadata["confound_groups"] = []
        self.parsed_design.metadata["confound_groups"].append(confound_group)

        return factors

    def _parse_factor(self) -> str:
        """Parse a factor with its size specification.

        Returns:
            The factor name

        Raises:
            ValueError: If factor specification is invalid
        """
        name_token = self._consume("IDENTIFIER")
        name = name_token.value

        # Parse size specification
        next_type = self._peek_type()

        if next_type == "LPAREN":
            # Balanced: Factor(n) or approximate: Factor(~n)
            self._consume("LPAREN")

            n: Union[int, str]
            if self._peek_type() == "TILDE":
                self._consume("TILDE")
                number_token = self._consume("NUMBER")
                n = f"~{self._parse_number(number_token.value)}"
            else:
                number_token = self._consume("NUMBER")
                n = self._parse_number(number_token.value)

            self._consume("RPAREN")

            self.parsed_design.factors.append(Factor(name, n, "factor"))

        elif next_type == "LBRACKET":
            # Unbalanced: Factor[n1|n2|n3]
            self._consume("LBRACKET")

            numbers = []
            number_token = self._consume("NUMBER")
            numbers.append(self._parse_number(number_token.value))

            while self._peek_type() == "PIPE":
                self._consume("PIPE")
                number_token = self._consume("NUMBER")
                numbers.append(self._parse_number(number_token.value))

            self._consume("RBRACKET")

            self.parsed_design.factors.append(Factor(name, numbers, "factor"))

        else:
            raise ValueError(f"Expected size specification for factor {name} at position {name_token.position}")

        return name

    def _parse_number(self, value: str) -> int:
        """Parse a number, handling 'k' suffix.

        Args:
            value: The number string (possibly with 'k' suffix)

        Returns:
            The parsed integer value
        """
        if value.endswith("k"):
            return int(value[:-1]) * 1000
        return int(value)

    def validate_syntax(self, tokens: List[Token]) -> bool:
        """Validate token sequence.

        Args:
            tokens: List of tokens to validate

        Returns:
            True if valid, False otherwise
        """
        # Basic validation - check matching braces and parentheses
        brace_count = 0
        paren_count = 0
        bracket_count = 0

        for token in tokens:
            if token.type == "LBRACE":
                brace_count += 1
            elif token.type == "RBRACE":
                brace_count -= 1
            elif token.type == "LPAREN":
                paren_count += 1
            elif token.type == "RPAREN":
                paren_count -= 1
            elif token.type == "LBRACKET":
                bracket_count += 1
            elif token.type == "RBRACKET":
                bracket_count -= 1

            if brace_count < 0 or paren_count < 0 or bracket_count < 0:
                return False

        return brace_count == 0 and paren_count == 0 and bracket_count == 0
