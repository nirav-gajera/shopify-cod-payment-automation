# System Architecture

## Architecture Diagram
```mermaid
flowchart TD
    A[Excel File] -->|orders/*.xlsx| B(collect_order_numbers)
    B -->|deduplicated list| C[process_order]
    C -->|API Authentication| D[Shopify OAuth Token Endpoint]
    C -->|GraphQL Query: FindOrder| E[Shopify GraphQL Endpoint]
    C -->|GraphQL Mutation: OrderMarkAsPaid| E
```

## Lifecycle Flow
1. **Startup:** `load_dotenv` initializes environment variables.
2. **Authentication:** Main script obtains a temporary OAuth access token from Shopify's OAuth endpoint.
3. **Parsing:** Directory `orders/` is scanned. Columns named `OrderId` (case-insensitive) are read. Order IDs are collected and deduplicated.
4. **Execution Loop:**
   - Query Shopify to retrieve order GID and financial status.
   - If not found: report as `not_found`.
   - If status is `PAID`: report as `already_paid` and skip.
   - If status is not `PAID`: invoke `orderMarkAsPaid` mutation.
   - If user errors return: report as `error` and print message.
   - If success: report as `success`.
5. **Teardown:** Close workbooks and output summary counts to terminal.

## Error Resilience
- **Invalid Tokens / Unauthorized:** Script immediately calls `raise_for_status()` to abort execution if authentication fails, preventing silent failure.
- **User Errors Handling:** User errors in Shopify (e.g. order is archived) are parsed from the GraphQL response structure and output directly instead of crashing.
- **File Parsing Safety:** Openpyxl workbooks are closed in a `finally` block or explicitly after iteration to prevent memory leaks and file locks.
