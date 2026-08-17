# AI Knowledge Base & Development Guide

## System Design Rationale
- **Stateless CLI Architecture:** Keeps the codebase extremely simple and easy to maintain. Since Shopify maintains the source-of-truth state, local state storage is redundant and error-prone.
- **GraphQL over REST:** The Shopify GraphQL Admin API allows fetching exactly what is needed (GID, status) in a single request and making targeted mutations, which is more resource-efficient than REST endpoints.

## Reusable Helper Index
- `get_access_token()`: Authenticates client credentials via OAuth.
- `gql(token, query, variables)`: Sends standard HTTP POST requests to the GraphQL endpoint with auth headers.
- `find_order_id(token, order_number)`: Resolves user-facing name/ID to Shopify GraphQL GID.
- `mark_as_paid(token, order_gid)`: Mutates payment status to PAID.

## Development Rules & Guardrails
- **GraphQL Scope Limit:** Never request fields that are not used by the script logic.
- **Header Parsing Guard:** When parsing spreadsheet files, always strip whitespace and match headers case-insensitively to prevent errors caused by manual sheet adjustments.
- **Error Propagation:** Always output `userErrors` messages in the terminal logs rather than silencing them.
