export const schema = {
  id: "17886265-844e-0fee-362b-d8ec908693eb",
  name: "AutonomousSystem",
  namespace: "Infra",
  description:
    "An Autonomous System (AS) is a set of Internet routable IP prefixes belonging to a network",
  default_filter: "name__value",
  branch: "aware",
  order_by: ["asn__value"],
  display_labels: ["name__value", "asn__value"],
  attributes: [
    {
      id: "17886265-85b9-ea17-3628-d8e472239eb4",
      name: "name",
      kind: "Text",
      namespace: "Attribute",
      label: "Name",
      description: null,
      default_value: null,
      enum: null,
      regex: null,
      max_length: null,
      min_length: null,
      inherited: false,
      unique: true,
      branch: "aware",
      optional: false,
      order_weight: 1000,
    },
    {
      id: "17886265-887b-07b1-3627-d8ef55cb84a2",
      name: "asn",
      kind: "Number",
      namespace: "Attribute",
      label: "Asn",
      description: null,
      default_value: null,
      enum: null,
      regex: null,
      max_length: null,
      min_length: null,
      inherited: false,
      unique: true,
      branch: "aware",
      optional: false,
      order_weight: 2000,
    },
    {
      id: "17886265-8b98-1597-3629-d8e801316e16",
      name: "description",
      kind: "Text",
      namespace: "Attribute",
      label: "Description",
      description: null,
      default_value: null,
      enum: null,
      regex: null,
      max_length: null,
      min_length: null,
      inherited: false,
      unique: false,
      branch: "aware",
      optional: true,
      order_weight: 3000,
    },
  ],
  relationships: [
    {
      id: "17886265-8e57-6afa-362b-d8eb29364153",
      name: "organization",
      peer: "CoreOrganization",
      kind: "Attribute",
      label: "Organization",
      description: null,
      identifier: "coreorganization__infraautonomoussystem",
      inherited: false,
      cardinality: "one",
      branch: "aware",
      optional: false,
      filters: [
        { name: "ids", kind: "Text", enum: null, object_kind: null, description: null },
        { name: "name__value", kind: "Text", enum: null, object_kind: null, description: null },
        { name: "label__value", kind: "Text", enum: null, object_kind: null, description: null },
        {
          name: "description__value",
          kind: "Text",
          enum: null,
          object_kind: null,
          description: null,
        },
      ],
      order_weight: 4000,
    },
    {
      id: "17886265-9022-6077-362b-d8eca6855d30",
      name: "member_of_groups",
      peer: "CoreGroup",
      kind: "Group",
      label: "Member Of Groups",
      description: null,
      identifier: "group_member",
      inherited: false,
      cardinality: "many",
      branch: "aware",
      optional: true,
      filters: [
        { name: "ids", kind: "Text", enum: null, object_kind: null, description: null },
        { name: "name__value", kind: "Text", enum: null, object_kind: null, description: null },
        { name: "label__value", kind: "Text", enum: null, object_kind: null, description: null },
        {
          name: "description__value",
          kind: "Text",
          enum: null,
          object_kind: null,
          description: null,
        },
      ],
      order_weight: 5000,
    },
    {
      id: "17886265-91e7-fcd1-362e-d8efb8c0988e",
      name: "subscriber_of_groups",
      peer: "CoreGroup",
      kind: "Group",
      label: "Subscriber Of Groups",
      description: null,
      identifier: "group_subscriber",
      inherited: false,
      cardinality: "many",
      branch: "aware",
      optional: true,
      filters: [
        { name: "ids", kind: "Text", enum: null, object_kind: null, description: null },
        { name: "name__value", kind: "Text", enum: null, object_kind: null, description: null },
        { name: "label__value", kind: "Text", enum: null, object_kind: null, description: null },
        {
          name: "description__value",
          kind: "Text",
          enum: null,
          object_kind: null,
          description: null,
        },
      ],
      order_weight: 6000,
    },
  ],
  label: "Autonomous System",
  inherit_from: [],
  groups: [],
  filters: [
    { name: "ids", kind: "Text", enum: null, object_kind: null, description: null },
    { name: "name__value", kind: "Text", enum: null, object_kind: null, description: null },
    { name: "asn__value", kind: "Number", enum: null, object_kind: null, description: null },
    { name: "description__value", kind: "Text", enum: null, object_kind: null, description: null },
    {
      name: "organization__ids",
      kind: "Text",
      enum: null,
      object_kind: "CoreOrganization",
      description: null,
    },
  ],
  kind: "InfraAutonomousSystem",
};

export const formFields = [
  { label: "ids", name: "ids", type: "text", value: "" },
  { label: "name__value", name: "name__value", type: "text", value: "" },
  { label: "asn__value", name: "asn__value", type: "number", value: "" },
  { label: "description__value", name: "description__value", type: "text", value: "" },
  { label: "organization__ids", name: "organization__ids", type: "text", value: "" },
];
