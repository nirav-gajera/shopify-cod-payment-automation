# Features & Functional Specifications

## 1. Excel Order Extraction Engine
- **Description:** Scans target folder, loads `.xlsx` workbooks, dynamically matches headers for the order number key (case-insensitive `orderid`), deduplicates the numbers, and returns them for processing.
- **Related Files:**
  - `mark_as_paid.py` (specifically `collect_order_numbers()`)
- **Dependencies:** `openpyxl`, `glob`

## 2. Shopify OAuth Authenticator
- **Description:** Exchanges store client ID and secret for a Shopify Admin access token.
- **Related Files:**
  - `mark_as_paid.py` (specifically `get_access_token()`)
  - `find_order.py`
  - `test_shopify.py`
- **Dependencies:** `requests`

## 3. Shopify Order Lookup
- **Description:** Resolves Shopify-visible order numbers (e.g. `1001`) to internal Shopify Global IDs (`gid://shopify/Order/6557315858590`) and grabs current payment status.
- **Related Files:**
  - `mark_as_paid.py` (specifically `find_order_id()`)
  - `find_order.py`
- **Dependencies:** `requests` (GraphQL)

## 4. Mark as Paid Execution
- **Description:** Sends mutation to Shopify to mark an unpaid order as PAID.
- **Related Files:**
  - `mark_as_paid.py` (specifically `mark_as_paid()`)
- **Dependencies:** `requests` (GraphQL)
