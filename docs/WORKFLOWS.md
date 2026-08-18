# Sequence Workflows

## Batch Processing Workflow

The following sequence diagram illustrates the workflow when running the main script to process all Excel invoice files.

```mermaid
sequenceDiagram
    participant User as User
    participant WebUI as Web Interface (index.html)
    participant Flask as Flask API (app.py)
    participant Shopify as Shopify GraphQL Admin API

    User->>WebUI: Drag and drop Excel file
    WebUI->>Flask: POST /api/upload
    Flask-->>WebUI: Return session ID & file preview data
    User->>WebUI: Click "Process"
    WebUI->>Flask: POST /api/process
    Flask->>Flask: Start Background Thread
    WebUI->>Flask: GET /api/stream/<session_id> (SSE Connect)
    Flask->>Shopify: POST /admin/oauth/access_token
    Shopify-->>Flask: Return Access Token
    loop For each unique Order ID
        Flask->>Shopify: Query: FindOrder (name:#ID)
        Shopify-->>Flask: Return order details (GID, status)
        alt status != PAID
            Flask->>Shopify: Mutation: orderMarkAsPaid (GID)
            Shopify-->>Flask: Return success/errors
        else status == PAID
            Flask->>Flask: Log "already_paid" and skip
        end
        Flask-->>WebUI: SSE data (log update, summary counts)
    end
    Flask-->>WebUI: SSE data (done)
    WebUI-->>User: Visual update indicating completion
```
