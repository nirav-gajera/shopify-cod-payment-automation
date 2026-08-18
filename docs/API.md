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

## Internal Web App Endpoints (Flask)

### 1. Upload File
- **Endpoint:** `POST /api/upload`
- **Description:** Accepts one or more `.xlsx` files via multipart/form-data. Parses them for Order IDs and returns session data and a file preview.
- **Response Format:**
  ```json
  [
    {
      "session_id": "uuid",
      "filename": "orders.xlsx",
      "headers": ["OrderId", "Customer", "Amount"],
      "rows": [["1001", "John", "50"]],
      "total_rows": 100,
      "order_count": 99,
      "order_id_col": 0
    }
  ]
  ```

### 2. Process Session
- **Endpoint:** `POST /api/process`
- **Description:** Accepts a JSON body with `{"session_id": "uuid"}`. Starts the background processing thread for the specified session.
- **Response Format:** `{"ok": true}`

### 3. Stream Logs (SSE)
- **Endpoint:** `GET /api/stream/<session_id>`
- **Description:** Opens a Server-Sent Events connection to stream logs and progress metrics for the given session.
- **Event Types:** `ping`, `log`, `summary`, `error`, `separator`, `done`.

### 4. Remove Session
- **Endpoint:** `POST /api/remove`
- **Description:** Deletes a session from the server cache.
- **Response Format:** `{"ok": true}`
