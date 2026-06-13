# SADS GraphQL API Specification

## 1. Cooperative Document Editing
SADS uses GraphQL subscriptions to synchronize visual design canvas actions:
- **Queries:** Fetch architecture component specs and design diagrams.
- **Mutations:** Modify canvas nodes, connect edges, or place payload elements.
- **Subscriptions:** Stream real-time position updates of collaborative users.

## 2. Schema Blueprint
```graphql
type Node {
  id: ID!
  type: String!
  x: Float!
  y: Float!
  properties: String
}

type Mutation {
  moveNode(id: ID!, x: Float!, y: Float!): Node
}

type Subscription {
  nodeMoved: Node
}
```
