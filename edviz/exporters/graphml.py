"""GraphML format exporter."""

from typing import Union, List
from lxml import etree
from edviz.data_structures import ParsedDesign


class GraphMLExporter:
    """Exporter for GraphML format."""

    def export(self, design: ParsedDesign) -> str:
        """Export design to GraphML format.

        Args:
            design: The parsed design to export

        Returns:
            GraphML format string
        """
        # Create root element
        graphml = etree.Element(
            "graphml",
            nsmap={
                None: "http://graphml.graphdrawing.org/xmlns",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
        )
        graphml.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://graphml.graphdrawing.org/xmlns "
            "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
        )

        # Define attribute keys for nodes
        self._add_key(graphml, "d0", "node", "factor_n", "string")
        self._add_key(graphml, "d1", "node", "factor_type", "string")

        # Define attribute keys for edges
        self._add_key(graphml, "d2", "edge", "rel_type", "string")

        # Create graph element
        graph = etree.SubElement(graphml, "graph", id="G", edgedefault="directed")

        # Add nodes (factors)
        for factor in design.factors:
            node = etree.SubElement(graph, "node", id=factor.name)
            self._add_data(node, "d0", self._format_factor_n(factor.n))
            self._add_data(node, "d1", factor.type)

        # Add edges (relationships)
        edge_id = 0
        for rel in design.relationships:
            edge = etree.SubElement(
                graph,
                "edge",
                id=f"e{edge_id}",
                source=rel.from_factor,
                target=rel.to_factor
            )
            self._add_data(edge, "d2", rel.rel_type)
            edge_id += 1

        # Convert to string
        return etree.tostring(
            graphml,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8"
        ).decode("utf-8")

    def _add_key(
        self,
        parent: etree.Element,
        id: str,
        for_type: str,
        attr_name: str,
        attr_type: str
    ) -> None:
        """Add a key definition element.

        Args:
            parent: Parent element
            id: Key ID
            for_type: "node" or "edge"
            attr_name: Attribute name
            attr_type: Attribute type
        """
        etree.SubElement(
            parent,
            "key",
            id=id,
            **{"for": for_type, "attr.name": attr_name, "attr.type": attr_type}
        )

    def _add_data(self, parent: etree.Element, key: str, value: str) -> None:
        """Add a data element.

        Args:
            parent: Parent element
            key: Key reference
            value: Data value
        """
        data = etree.SubElement(parent, "data", key=key)
        data.text = value

    def _format_factor_n(self, n: Union[int, List[int], str]) -> str:
        """Format factor size for GraphML.

        Args:
            n: Factor size

        Returns:
            Formatted string
        """
        if isinstance(n, str):
            return n
        elif isinstance(n, list):
            return f"[{','.join(map(str, n))}]"
        else:
            return str(n)
