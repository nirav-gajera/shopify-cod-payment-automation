# AGENTS.md

Welcome to the Shopify COD Order Mark as Paid Automation repository. This document serves as the entry point and contract for all AI agents working on this codebase.

## Project Overview & Core Mission
A lightweight, Python-based CLI tool to automate marking Cash-on-Delivery (COD) orders as Paid in Shopify. It reads delivered order IDs from logistics Excel sheets (placed in the `orders/` directory) and updates their payment status via the Shopify GraphQL Admin API.

- **Backend Runtime:** Python 3.10+
- **Primary Dependencies:** `requests`, `python-dotenv`, `openpyxl`
- **Integrations:** Shopify Admin GraphQL API

## Architecture Diagram & Flow

```mermaid
graph TD
    A[Excel Files in orders/] -->|Read OrderIds via openpyxl| B(mark_as_paid.py)
    B -->|1. Authenticate| C(Shopify OAuth endpoint)
    C -->|Return Access Token| B
    B -->|2. Find Order GID & Status| D(Shopify GraphQL: orders query)
    D -->|Return GID & displayFinancialStatus| B
    B -->|3. If PENDING, Mark Paid| E(Shopify GraphQL: orderMarkAsPaid mutation)
    E -->|Confirm Success/Errors| B
```

## Repository Conventions & Coding Standards
- **Python Style:** Follow PEP 8 guidelines. Use clean snake_case for functions and variables. UPPER_CASE for global constants.
- **Dependency Management:** Packages should be listed in instructions/dependencies. Use a virtual environment.
- **Error Handling:** Always check for `userErrors` returned in GraphQL payloads, not just HTTP status codes.
- **Environment Variables:** All secrets and configurations (`SHOPIFY_SHOP`, `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET`) must be kept in `.env` and never committed.

## Project Structure Tree
```
.
├── .env                  # Shopify store credentials (ignored by git)
├── .gitignore            # Git ignore file
├── README.md             # Public project description and user guide
├── find_order.py         # Debug utility to look up order info by number
├── mark_as_paid.py       # Main automation script (Excel parser + Shopify caller)
├── test_shopify.py       # Authentication validation script
├── orders/               # Input directory for Excel invoice files
└── docs/                 # Project documentation suite
```

## Workflows
- **Running a single order test:** `python mark_as_paid.py --order <number>`
- **Running a single file test:** `python mark_as_paid.py --file "orders/<filename>.xlsx"`
- **Running full automation:** `python mark_as_paid.py`

## AI Directives
1. **Analyze First:** Before modifying any GraphQL query or mutation, verify the schema version in use (default is `2026-04`).
2. **GraphQL Safety:** Always include the `userErrors` field in mutations to properly detect business logic errors (e.g., trying to pay an archived order).
3. **Paths:** Use relative repository paths when referencing files, never absolute paths.

## Definition of Done
1. Implementation is clean and adheres to PEP 8.
2. Code runs successfully without unhandled exceptions.
3. Documentation is updated according to the mapping below.

## Documentation Update Mapping

| Trigger Event | Target Files to Update |
| :--- | :--- |
| New feature added | `docs/FEATURES.md`, `docs/CHANGELOG.md`, `docs/OVERVIEW.md` (if scope changes) |
| API route / webhook changed | `docs/API.md`, `docs/WORKFLOWS.md` |
| Database migration added/edited | `docs/DATABASE.md` |
| Architecture / system design changed | `docs/ARCHITECTURE.md`, `docs/WORKFLOWS.md`, `AGENTS.md` |
| Frontend component added/edited | `docs/COMPONENTS.md` |
| Deployment / serverless config changed | `docs/DEPLOYMENT.md`, `docs/PROJECT.md` |
| Bug fixed | `docs/CHANGELOG.md`, `docs/TROUBLESHOOTING.md` |
