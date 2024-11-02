from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from lxml import html  # type: ignore

import xml.etree.ElementTree as ET


@dataclass
class ElementData:
    tag: str
    attributes: Dict[str, str]
    text: Optional[str] = None
    tail: Optional[str] = None
    children: List["ElementData"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "attributes": self.attributes,
            "text": self.text,
            "tail": self.tail,
            "children": [child.to_dict() for child in self.children],
        }


def element_to_dict(element: ET.Element) -> ElementData:
    children = [element_to_dict(child) for child in element]

    return ElementData(
        tag=element.tag,
        attributes=dict(element.attrib),
        text=element.text.strip() if element.text and element.text.strip() else None,
        tail=element.tail.strip() if element.tail and element.tail.strip() else None,
        children=children,
    )


def html_to_json(html_content: str) -> Dict[str, Any]:
    tree = html.fromstring(html_content)
    return element_to_dict(tree).to_dict()
