export const branchesQuery = `
query GetBranches {
  Branch {
    id
    name
    description
    origin_branch
    branched_from
    created_at
    is_data_only
    is_default
  }
}
`;

export const branchesMocks = [
  {
    id: "eb870135-a2fd-4825-a0eb-66026c970e8d",
    name: "main",
    description: "Default Branch",
    origin_branch: "main",
    branched_from: "2023-05-23T11:15:42.209793Z",
    created_at: "2023-05-23T11:15:42.209819Z",
    is_data_only: false,
    is_default: true,
    __typename: "Branch",
  },
];
