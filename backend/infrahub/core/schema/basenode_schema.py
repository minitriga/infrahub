from __future__ import annotations

import hashlib
import keyword
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Union

from infrahub_sdk.utils import compare_lists
from pydantic import field_validator

from infrahub.core.models import HashableModelDiff

from .attribute_schema import AttributeSchema  # noqa: TCH001
from .generated.base_node_schema import GeneratedBaseNodeSchema
from .relationship_schema import RelationshipSchema  # noqa: TCH001

if TYPE_CHECKING:
    from typing_extensions import Self

    from infrahub.core.branch import Branch
    from infrahub.core.schema import GenericSchema, NodeSchema

# pylint: disable=redefined-builtin


NODE_METADATA_ATTRIBUTES = ["_source", "_owner"]


class BaseNodeSchema(GeneratedBaseNodeSchema):  # pylint: disable=too-many-public-methods
    _exclude_from_hash: List[str] = ["attributes", "relationships"]
    _sort_by: List[str] = ["name"]

    @property
    def kind(self) -> str:
        if self.namespace == "Attribute":
            return self.name
        return self.namespace + self.name

    @property
    def menu_title(self) -> str:
        return self.label or self.name

    def __hash__(self) -> int:
        """Return a hash of the object.
        Be careful hash generated from hash() have a salt by default and they will not be the same across run"""
        return hash(self.get_hash())

    def get_hash(self, display_values: bool = False) -> str:
        """Extend the Hash Calculation to account for attributes and relationships."""

        md5hash = hashlib.md5()
        md5hash.update(super().get_hash(display_values=display_values).encode())

        for attr_name in sorted(self.attribute_names):
            md5hash.update(self.get_attribute(name=attr_name).get_hash(display_values=display_values).encode())

        for rel_name in sorted(self.relationship_names):
            md5hash.update(self.get_relationship(name=rel_name).get_hash(display_values=display_values).encode())

        return md5hash.hexdigest()

    def diff(self, other: Self) -> HashableModelDiff:
        """Extend the Diff Calculation to account for attributes and relationships."""

        node_diff = super().diff(other=other)

        attrs_both, attrs_local, attrs_other = compare_lists(list1=self.attribute_names, list2=other.attribute_names)

        attrs_diff = HashableModelDiff()
        if attrs_local:
            attrs_diff.added = {attr_name: None for attr_name in attrs_local}
        if attrs_other:
            attrs_diff.removed = {attr_name: None for attr_name in attrs_other}
        if attrs_both:
            for attr_name in sorted(attrs_both):
                local_attr = self.get_attribute(name=attr_name)
                other_attr = other.get_attribute(name=attr_name)
                attr_diff = local_attr.diff(other_attr)
                if attr_diff.has_diff:
                    attrs_diff.changed[attr_name] = attr_diff

        rels_diff = HashableModelDiff()
        rels_both, rels_local, rels_other = compare_lists(list1=self.relationship_names, list2=other.relationship_names)
        if rels_local:
            rels_diff.added = {rel_name: None for rel_name in rels_local}
        if rels_other:
            rels_diff.removed = {rel_name: None for rel_name in rels_other}
        if rels_both:
            for rel_name in sorted(rels_both):
                local_rel = self.get_relationship(name=rel_name)
                other_rel = other.get_relationship(name=rel_name)
                rel_diff = local_rel.diff(other_rel)
                if rel_diff.has_diff:
                    rels_diff.added[rel_name] = rel_diff

        if attrs_diff.has_diff:
            node_diff.changed["attributes"] = attrs_diff
        if rels_diff.has_diff:
            node_diff.changed["relationships"] = rels_diff

        return node_diff

    def get_field(self, name: str, raise_on_error: bool = True) -> Optional[Union[AttributeSchema, RelationshipSchema]]:
        if field := self.get_attribute(name, raise_on_error=False):
            return field

        if field := self.get_relationship(name, raise_on_error=False):
            return field

        if not raise_on_error:
            return None

        raise ValueError(f"Unable to find the field {name}")

    def get_attribute(self, name, raise_on_error: bool = True) -> AttributeSchema:
        for item in self.attributes:
            if item.name == name:
                return item

        if not raise_on_error:
            return None

        raise ValueError(f"Unable to find the attribute {name}")

    def get_relationship(self, name, raise_on_error: bool = True) -> RelationshipSchema:
        for item in self.relationships:
            if item.name == name:
                return item

        if not raise_on_error:
            return None

        raise ValueError(f"Unable to find the relationship {name}")

    def get_relationship_by_identifier(self, id: str, raise_on_error: bool = True) -> RelationshipSchema:
        for item in self.relationships:
            if item.identifier == id:
                return item

        if not raise_on_error:
            return None

        raise ValueError(f"Unable to find the relationship {id}")

    def get_relationships_by_identifier(self, id: str) -> List[RelationshipSchema]:
        """Return a list of relationship instead of a single one"""
        rels: List[RelationshipSchema] = []
        for item in self.relationships:
            if item.identifier == id:
                rels.append(item)

        return rels

    @property
    def valid_input_names(self) -> List[str]:
        return self.attribute_names + self.relationship_names + NODE_METADATA_ATTRIBUTES

    @property
    def attribute_names(self) -> List[str]:
        return [item.name for item in self.attributes]

    @property
    def relationship_names(self) -> List[str]:
        return [item.name for item in self.relationships]

    @property
    def mandatory_input_names(self) -> List[str]:
        return self.mandatory_attribute_names + self.mandatory_relationship_names

    @property
    def mandatory_attribute_names(self) -> List[str]:
        return [item.name for item in self.attributes if not item.optional and item.default_value is None]

    @property
    def mandatory_relationship_names(self) -> List[str]:
        return [item.name for item in self.relationships if not item.optional]

    @property
    def local_attributes(self) -> List[AttributeSchema]:
        return [item for item in self.attributes if not item.inherited]

    @property
    def local_relationships(self) -> List[RelationshipSchema]:
        return [item for item in self.relationships if not item.inherited]

    @property
    def unique_attributes(self) -> List[AttributeSchema]:
        return [item for item in self.attributes if item.unique]

    def generate_fields_for_display_label(self) -> Dict:
        """Generate a Dictionnary containing the list of fields that are required
        to generate the display_label.

        If display_labels is not defined, we return None which equal to everything.
        """

        if not hasattr(self, "display_labels") or not isinstance(self.display_labels, list):
            return None

        fields: dict[str, Union[str, None, dict[str, None]]] = {}
        for item in self.display_labels:
            elements = item.split("__")
            if len(elements) == 1:
                fields[elements[0]] = None
            elif len(elements) == 2:
                fields[elements[0]] = {elements[1]: None}
            else:
                raise ValueError(f"Unexpected value for display_labels, {item} is not valid.")

        return fields

    @field_validator("name")
    @classmethod
    def name_is_not_keyword(cls, value: str) -> str:
        if keyword.iskeyword(value):
            raise ValueError(f"Name can not be set to a reserved keyword '{value}' is not allowed.")

        return value

    def parse_attribute_path(
        self,
        attribute_path: str,
        branch: Optional[Union[Branch, str]] = None,
        schema_map_override: Optional[Dict[str, Union[NodeSchema, GenericSchema]]] = None,
    ) -> SchemaAttributePath:
        allowed_leaf_properties = ["value"]
        schema_path = SchemaAttributePath()
        relationship_piece: Optional[str] = None
        attribute_piece: Optional[str] = None
        property_piece: Optional[str] = None
        path_parts = attribute_path.split("__")
        if path_parts[0] in self.relationship_names:
            relationship_piece = path_parts[0]
            attribute_piece = path_parts[1] if len(path_parts) > 1 else None
            property_piece = path_parts[2] if len(path_parts) > 2 else None
        elif path_parts[0] in self.attribute_names:
            attribute_piece = path_parts[0]
            property_piece = path_parts[1] if len(path_parts) > 1 else None
        else:
            raise AttributePathParsingError(f"{attribute_path} is invalid on schema {self.kind}")
        if relationship_piece:
            if relationship_piece not in self.relationship_names:
                raise AttributePathParsingError(f"{relationship_piece} is not a relationship of schema {self.kind}")
            relationship_schema = self.get_relationship(path_parts[0])
            schema_path.relationship_schema = relationship_schema
            if schema_map_override:
                try:
                    schema_path.related_schema = schema_map_override.get(relationship_schema.peer)
                except KeyError as exc:
                    raise AttributePathParsingError(f"No schema {relationship_schema.peer} in map") from exc
            else:
                schema_path.related_schema = relationship_schema.get_peer_schema(branch=branch)
        if attribute_piece:
            schema_to_check = schema_path.related_schema or self
            if attribute_piece not in schema_to_check.attribute_names:
                raise AttributePathParsingError(f"{attribute_piece} is not a valid attribute of {schema_to_check.kind}")
            schema_path.attribute_schema = schema_to_check.get_attribute(attribute_piece)
        if property_piece:
            if property_piece not in allowed_leaf_properties:
                raise AttributePathParsingError(
                    f"{property_piece} is not a valid property of {schema_path.attribute_schema.name}"
                )
            schema_path.attribute_property_name = property_piece
        return schema_path

    def get_unique_constraint_schema_attribute_paths(self) -> List[List[SchemaAttributePath]]:
        if not self.uniqueness_constraints:
            return []

        constraint_paths_groups = []
        for uniqueness_path_group in self.uniqueness_constraints:
            constraint_paths_groups.append(
                [
                    self.parse_attribute_path(attribute_path=uniqueness_path_part)
                    for uniqueness_path_part in uniqueness_path_group
                ]
            )
        return constraint_paths_groups


@dataclass
class SchemaAttributePath:
    relationship_schema: Optional[RelationshipSchema] = None
    related_schema: Optional[Union[NodeSchema, GenericSchema]] = None
    attribute_schema: Optional[AttributeSchema] = None
    attribute_property_name: Optional[str] = None


class AttributePathParsingError(Exception):
    ...
