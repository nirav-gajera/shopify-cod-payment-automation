# API & Integrations

All API calls interact with Shopify's GraphQL Admin API.

## API Version
The script uses API version `2026-04`.
Endpoint URL: `https://{SHOPIFY_SHOP}.myshopify.com/admin/api/2026-04/graphql.json`

## Authentication Endpoint
- **URL:** `POST https://{SHOPIFY_SHOP}.myshopify.com/admin/oauth/access_token`
- **Request Body:**
  ```url
  grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}
  ```
- **Response Format:**
  ```json
  {
    "access_token": "shpca_xxxxxxxxxxxxxxxxxxxxxxxxxx",
    "scope": "read_orders,write_orders"
  }
  ```

## GraphQL Operations

### 1. FindOrder Query
Used to fetch internal Shopify GID and financial status.

- **Query:**
  ```graphql
  query FindOrder($query: String!) {
      orders(first: 1, query: $query) {
          nodes {
              id
              name
              displayFinancialStatus
          }
      }
  }
  ```
- **Variables:**
  ```json
  {
    "query": "name:#1001"
  }
  ```

### 2. orderMarkAsPaid Mutation
Used to mark a pending/unpaid order as paid.

- **Mutation:**
  ```graphql
  mutation OrderMarkAsPaid($input: OrderMarkAsPaidInput!) {
      orderMarkAsPaid(input: $input) {
          order {
              id
              name
              displayFinancialStatus
          }
          userErrors {
              field
              message
          }
      }
  }
  ```
- **Variables:**
  ```json
  {
    "input": {
      "id": "gid://shopify/Order/6557315858590"
    }
  }
  ```
